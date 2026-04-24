# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spring PetClinic sample application built with **Spring Data JDBC** (not JPA/Hibernate). Demonstrates best practices for Spring Boot 4.0.1 with Java 17, MySQL, and Thymeleaf server-side rendering.

## Build & Development Commands

```bash
# Start MySQL dependency
docker compose up -d

# Build and package
./mvnw -B package

# Run all tests (requires MySQL via TestContainers — starts automatically)
./mvnw test

# Run a single test class or method
./mvnw test -Dtest=OwnerControllerTests
./mvnw test -Dtest=PetclinicIntegrationTests#testFindAll

# Full verify: tests + Spotless formatting check + JaCoCo coverage
./mvnw verify

# Check/apply code formatting (must pass before commit)
./mvnw spotless:check
./mvnw spotless:apply
```

## Architecture

The application is organized into domain packages under `org.springframework.samples.petclinic`:

- **`owner`** — Owner, Pet, and Visit controllers + repositories + entities; the main domain
- **`vet`** — Vet and Specialty entities/repositories; exposes `VetController` with JSON and HTML views
- **`visit`** — Visit entity and repository
- **`system`** — `CacheConfiguration` (Caffeine), error handling, welcome page

**Data model:** `Owner` → `Pet` → `Visit` (one-to-many chains). `Vet` ↔ `Specialty` is many-to-many via `SpecialtyRef`. Schema is managed by Flyway migrations in `src/main/resources/db/migration/`.

**Spring Data JDBC** — entities use `@Table`/`@Column` annotations; no lazy loading or entity managers. `AggregateReference` is used for cross-aggregate references (e.g., `Pet` referencing `Owner` by ID).

**Caching** — Vet list is cached with Caffeine (`@Cacheable("vets")`), configured in `CacheConfiguration`.

**Validation** — Jakarta validation annotations on entities; custom `PetValidator` for web form logic.

**Modern Java** — DTOs use Java records (`VetDto`, `OwnerDetails`, `PetDetails`).

## Code Style

Spotless enforces formatting using Eclipse formatter rules from `etc/eclipse-formatter.xml`, plus license headers from `etc/license-header.txt`. Run `./mvnw spotless:apply` to auto-format before committing.

Use 4-space indentation (enforced by `.editorconfig`). Line endings are LF.

## Testing

Integration tests use **TestContainers** (MySQL) and run with `spring.test.database.replace=none`. The test Spring profile is activated automatically via Surefire configuration in `pom.xml`. No mocking of the database — tests hit a real MySQL instance spun up by TestContainers.
