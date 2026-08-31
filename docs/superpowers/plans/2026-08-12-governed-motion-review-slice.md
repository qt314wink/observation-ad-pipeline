# Governed Motion Review Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Observation Ad PR #1 into an inspectable product slice with canonical LithoMemphis provenance, Git LFS media contracts, machine-readable motion observations, and a static review UI deployable to Vercel.

**Architecture:** GitHub retains contracts, observation records, review assets, and LFS pointers. Each source video has an immutable media record; observations remain explicitly `pending-source-verification` until the real LFS object is present and measured. A dependency-free static review UI renders the records without becoming a second source of truth.

**Tech Stack:** Python 3.10+, fastjsonschema, PyYAML, pytest, Git LFS, static HTML/CSS/JavaScript, Vercel.

## Global Constraints

- Canonical LithoMemphis authority is `qt314wink/nextjs-boilerplate@b1bcbcc3199b41b37616bd377a0461e4a6f489bf/docs/lithomemphis-v2-plan.md`.
- Source content address is Git blob SHA-1 `cb0504a0172fea90985d1ba1aa9476b70e1101ff`.
- MP4 binaries use Git LFS; ordinary Git stores pointers only.
- No observations, timestamps, dimensions, durations, or media digests may be invented when source binaries are unavailable.
- Review UI is read-only and static; Git records remain canonical.

---

### Task 1: Canonical authority closure

**Files:** modify `config/prompt-family-provenance/lithomemphis.yaml`; modify `schemas/prompt-family-provenance.schema.json`; test `tests/test_governance_validation.py`.

- [ ] Add a failing test requiring canonical authority to use an immutable locator and explicit content-address algorithm.
- [ ] Run the focused test and verify the expected failure.
- [ ] Extend the schema and authority validator minimally.
- [ ] Record the canonical commit and blob hash.
- [ ] Run focused and full governance tests.

### Task 2: Git LFS media and observation contracts

**Files:** create `.gitattributes`; create `schemas/motion-analysis.schema.json`; create `fixtures/motion/mandala-reel-set.yaml`; create `tests/test_motion_analysis.py`; create `src/obsad/validate_motion.py`.

- [ ] Write failing tests for four unique sources, LFS tracking, evidence status, taxonomy completeness, and prohibited fabricated measurements.
- [ ] Verify failures.
- [ ] Add the schema, validator, and four source records.
- [ ] Keep measured fields absent and observations explicitly pending until the MP4 objects are available.
- [ ] Verify focused tests pass.

### Task 3: Read-only review UI

**Files:** create `review/index.html`; create `review/styles.css`; create `review/app.js`; create `review/data/mandala-reel-set.json`; create `vercel.json`; test `tests/test_review_ui.py`.

- [ ] Write failing structural UI tests.
- [ ] Verify failures.
- [ ] Implement an accessible evidence ledger, taxonomy matrix, media readiness states, and splice/music panels.
- [ ] Verify UI tests and static path integrity.

### Task 4: CI, documentation, and publication

**Files:** modify `.github/workflows/governance-validation.yml`; modify `README.md`.

- [ ] Add motion validation and UI structural tests to CI.
- [ ] Document LFS hydration, validation, review, and deployment commands.
- [ ] Run all tests, compile checks, governance validation, and `git lfs track` verification.
- [ ] Publish changes to the existing PR branch.
- [ ] Create and inspect the first Vercel preview; do not promote to production.
