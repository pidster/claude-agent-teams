# Review Scratchpad: <PLAN-NAME>

This file mirrors the plan's base name with a `-review-scratchpad.md`
suffix and lives alongside the plan, e.g.
`plans/current/2026-04-19-my-feature-review-scratchpad.md` next to
`plans/current/2026-04-19-my-feature.md`.

**Plan under review:** `plans/current/<PLAN-FILE>.md`
**Scratchpad created:** YYYY-MM-DD
**Status:** Active
**Delete when:** The user confirms the plan is ready and any revisions are
committed. On deletion, the plan itself must carry a `### Review history`
section summarising what this scratchpad recorded.

This scratchpad is **working memory for the review pipeline**. It is
deliberately ephemeral — merged findings land in the plan, the scratchpad
gets deleted at the end. Treat it as a ledger, not a discussion doc.

---

## Round ledger

Each row is a completed review round.

| Round | Date       | Reviewers                             | Critical | Warning | Suggestion | Revisions commit |
|-------|------------|---------------------------------------|----------|---------|------------|------------------|
| 1     | YYYY-MM-DD | rust, architect, security, reviewer, adversarial, tester | N | M | K | `<sha>` |

---

## Validator history

One row per validator run (pre-review and post-revision).

| When            | OK | Broken | Real-broken | Regressions introduced |
|-----------------|----|--------|-------------|-----------------------|
| Round 1 pre     | 10 | 5      | 0           | n/a                    |
| Round 1 post    | 10 | 5      | 0           | 0                      |

---

## Resolution ledger

Every finding, every round. Carried forward until each finding is
`verified-resolved`, `rejected`, or superseded.

Use the severity and confidence tags from the reviewer verbatim. Do not
re-rate. If consolidation changed the severity, record both
(`severity: Critical (rust); Warning (consolidated, reason: ...)`).

### Finding N — <one-line summary>
- **Severity / Confidence:** Critical / high
- **Reviewers who flagged:** rust-expert, architect, domain (3 independent)
- **Category:** trait conformance
- **Round 1 outcome:** applied — see §2 rewrite in plan
- **Round 2 check:** verified-resolved (all 3 reviewers agree)

### Finding M — <one-line summary>
- **Severity / Confidence:** Should fix / medium
- **Reviewers who flagged:** architect (1)
- **Category:** scope
- **Round 1 outcome:** deferred per user decision (see Trade-off Ledger)
- **Round 2 check:** n/a — superseded by Q7 coordination work

---

## Disagreements log

Where reviewers diverged on direction or severity. Disagreements are
information; they don't get deduped away.

- **Round 1, finding on `verify_as` inherent method:**
  - rust-expert: keep as test-only
  - architect: remove entirely
  - domain: remove entirely
  - **Resolution (Q3):** remove; trait-only `verify` with construction-time
    `VerificationPolicy`. Rationale: `Arc<dyn SigningProvider>` dispatch needs
    uniform surface.

---

## Not-applied log

Every Must-fix and Should-fix finding that did not land in an applied
revision, with the reason.

- **Round 1, finding N:** <summary>
  - Reason: rejected by user — <rationale>
- **Round 1, finding M:** <summary>
  - Reason: applied differently — see <commit> which addressed it as
    <what landed>

---

## Trade-off ledger

User-made decisions during iteration. Durable; on scratchpad deletion,
these move to the plan's own `### Trade-off Ledger` section.

- **YYYY-MM-DD, Q1:** `VULCAN_SIGNING_MODE` enum — chose
  `required|optional|disabled` + separate `VULCAN_SIGNING_PROVIDER` over
  `off|spiffe|required`. Reason: common framework already shipped this form;
  automata CLI enforces it.
- **YYYY-MM-DD, Q2:** Envelope extension — chose typed
  `SignerExtensions::<Provider>` on `SignedEnvelope` over adding
  `cert_chain` to `DsseSignature`. Reason: Sigstore's bundle doesn't fit
  a flat cert-chain field.

---

## Intended-future-artefact ledger

Per the validator's triage: paths the plan says it will create. Recorded
here so they can be verified when the tasks that create them are marked
Done.

- `src/vulcan-signing/src/spiffe.rs` — claimed in plan. Created by Phase 1
  task 2. Verify on that task's commit.
- `src/vulcan-signing/tests/support/mod.rs` — claimed. Created by Phase 2
  task 9. Verify on that task's commit.

---

## Pending questions

Open items that will become findings or decisions in a future round.

- <question 1>
- <question 2>

---

## Closure

When the user declares the plan ready:

1. Copy the **Round ledger** summary into the plan's `### Review history`
   section.
2. Copy the **Trade-off ledger** entries into the plan's
   `### Trade-off Ledger` section (if not already there).
3. Verify each **Intended-future-artefact** against the final plan; any
   still-unresolved becomes an open-questions entry in the plan.
4. Delete this scratchpad.

Deletion is the signal that iteration is closed. If you are tempted to
keep the scratchpad "just in case," that's usually a sign the plan is
not actually ready.
