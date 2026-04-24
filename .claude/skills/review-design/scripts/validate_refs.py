#!/usr/bin/env python3
"""Validate every file/ADR/commit reference cited in a design plan.

Emits a JSON report to stdout so the review-design skill can pass it
forward as context to reviewer agents.

Exit code is always 0 — broken references are data, not an error.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]

# Matches paths that look like source/doc references (heuristic, intentionally tight).
PATH_HINT = re.compile(
    r"""
    (?:`|\(|\s)                          # opened by backtick, paren, or whitespace
    (?P<path>
      (?:\.\./|\./)?                     # optional relative prefix
      (?:src|plans|docs|schema|scripts|\.claude|tests) # known top-level dirs
      /[\w\-./]+                         # path body
    )
    (?=`|\)|\s|$|:)                      # closing delimiter
    """,
    re.VERBOSE,
)

MD_LINK = re.compile(r"\[[^\]]*\]\((?P<target>[^)]+)\)")
ADR_REF = re.compile(r"\bADR-(\d{3})\b")
COMMIT_HASH = re.compile(r"(?<![0-9a-f])([0-9a-f]{7,40})(?![0-9a-f])")
CODE_FENCE = re.compile(r"^```")


@dataclass
class Ref:
    kind: str          # "path", "md_link", "adr", "commit"
    raw: str           # as cited in the plan
    resolved: str      # absolute or normalized form
    exists: bool
    source_line: int


def strip_code_fences(text: str) -> str:
    """Replace fenced code blocks with blank lines so paths inside examples
    don't produce false positives. Line numbers are preserved."""
    lines = text.splitlines()
    out, in_fence = [], False
    for line in lines:
        if CODE_FENCE.match(line.lstrip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def check_path(raw: str, plan_dir: Path) -> tuple[str, bool]:
    candidate = (plan_dir / raw).resolve() if raw.startswith((".", "/")) is False and raw.startswith("../") else None
    # Prefer repo-rooted lookup for absolute-looking relative paths
    if candidate is None:
        candidate = (REPO_ROOT / raw).resolve()
        if not candidate.exists():
            # Try relative to plan dir as fallback
            alt = (plan_dir / raw).resolve()
            if alt.exists():
                candidate = alt
    return str(candidate.relative_to(REPO_ROOT)) if candidate.is_relative_to(REPO_ROOT) else str(candidate), candidate.exists()


def check_adr(num: str) -> tuple[str, bool]:
    matches = list((REPO_ROOT / "docs/architecture/decisions").glob(f"{num}-*.md"))
    if matches:
        return str(matches[0].relative_to(REPO_ROOT)), True
    return f"docs/architecture/decisions/{num}-*.md", False


def check_commit(sha: str) -> tuple[str, bool]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "-e", sha],
        capture_output=True,
    )
    return sha, result.returncode == 0


def find_refs(plan_path: Path) -> list[Ref]:
    text = plan_path.read_text()
    stripped = strip_code_fences(text)
    refs: list[Ref] = []
    plan_dir = plan_path.parent

    for lineno, line in enumerate(stripped.splitlines(), start=1):
        for m in MD_LINK.finditer(line):
            target = m.group("target").split()[0]  # drop optional title
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Strip anchor fragment; anchors within a file aren't path-validated here
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue  # purely in-doc anchor
            resolved, exists = check_path(path_part, plan_dir)
            refs.append(Ref("md_link", target, resolved, exists, lineno))

        for m in PATH_HINT.finditer(line):
            raw = m.group("path")
            resolved, exists = check_path(raw, plan_dir)
            refs.append(Ref("path", raw, resolved, exists, lineno))

        for m in ADR_REF.finditer(line):
            num = m.group(1)
            resolved, exists = check_adr(num)
            refs.append(Ref("adr", f"ADR-{num}", resolved, exists, lineno))

        for m in COMMIT_HASH.finditer(line):
            sha = m.group(1)
            resolved, exists = check_commit(sha)
            refs.append(Ref("commit", sha, resolved, exists, lineno))

    # Deduplicate by (kind, raw) keeping earliest occurrence
    seen: dict[tuple[str, str], Ref] = {}
    for ref in refs:
        key = (ref.kind, ref.raw)
        if key not in seen:
            seen[key] = ref
    return list(seen.values())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_refs.py <plan-file>", file=sys.stderr)
        return 2

    plan_path = Path(sys.argv[1]).resolve()
    if not plan_path.is_file():
        print(f"not a file: {plan_path}", file=sys.stderr)
        return 2

    refs = find_refs(plan_path)
    broken = [asdict(r) for r in refs if not r.exists]
    ok = [asdict(r) for r in refs if r.exists]

    report = {
        "plan": str(plan_path.relative_to(REPO_ROOT)),
        "totals": {
            "checked": len(refs),
            "ok": len(ok),
            "broken": len(broken),
        },
        "broken": broken,
        "ok": ok,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
