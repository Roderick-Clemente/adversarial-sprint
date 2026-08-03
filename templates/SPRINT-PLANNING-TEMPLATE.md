> 📌 **Canonical copy.** Single source of truth for the GROK → CHUNK → EXECUTE method. It originated in `tone-dragons/_attic/planning/ai-sprints/` (v1.2) and was then copy-pasted into six-plus dakota repos, where it started to drift. Improve it here; treat every other copy as stale.
>
> Adapt stack specifics per repo — the npm/TypeScript examples below become Python/pytest for `QuantumBank`. Pair with the `review-tests` skill and cross-family plan review, see [`../PRD.md`](../PRD.md).

---

# AI Sprint Planning Template

Use this template to structure security, feature, refactor, and bug-fix sprints.

---

Template notes: This version tightens TDD expectations and test-quality guidance.

## Sprint Metadata

**Sprint Name:** [Brief descriptive name]
**Date:** YYYY-MM-DD
**Sprint Type:** [Security | Feature | Refactor | Bug Fix]
**Priority:** [P0-Critical | P1-High | P2-Medium | P3-Low]
**Estimated Duration:** [30 mins | 2 hours | 1 day]
**Status:** [Planning | Ready | In Progress | Complete]

## Sprint Principles

- **Low-token execution:** Plan once, execute in small chunks with minimal context.
- **Standardized practice:** Embed testing, flagging, and release discipline in the plan.
- **Audit trail:** Each chunk leaves clear evidence for review and future reference.
- **TDD-first (Red-Green-Refactor):** Write failing tests before implementation, then make them pass.

### TDD Cycle (Required for New/Changed Behavior)

Every code change chunk MUST follow this cycle:

```
1. RED    → Write a failing test that describes the expected behavior
2. GREEN  → Write the minimum code to make the test pass
3. REFACTOR → Clean up while keeping tests green
```

**Non-negotiable:** The test MUST fail before implementation when adding new or changed behavior. If it passes, the test isn't validating new behavior.

**Exceptions:** Refactors, test-only cleanups, documentation-only changes, or fixes where a failing test already exists do not require a new RED step. Document why in the chunk notes.

### Branch Discipline (Required)

- **Start clean:** Ensure `dev` branch is clean (no uncommitted changes) before starting
- **Sprint branch:** Create a feature branch off `dev` for each sprint (`feature/YYYY-MM-DD-sprint-name`)
- **Merge back:** Sprint branch merges to `dev` via PR when complete

---

## Sprint Objectives

### Primary Goal
[One-sentence description of what this sprint achieves]

### Success Criteria
- [ ] Criterion 1 (measurable outcome)
- [ ] Criterion 2 (measurable outcome)
- [ ] Criterion 3 (measurable outcome)

### Out of Scope
- [Explicitly list what this sprint does NOT cover]
- [Helps prevent scope creep]

---

## Stage 1: GROK - Problem Analysis

### Context & Background
[Describe the current state, why this sprint is needed, what triggered it]

### Root Cause Analysis
[For bugs/security issues: What's the underlying cause?]

### Risk Assessment
| Risk Factor | Severity | Probability | Impact | Mitigation |
|-------------|----------|-------------|---------|------------|
| [Risk 1]    | [H/M/L]  | [H/M/L]     | [Description] | [How to prevent] |
| [Risk 2]    | [H/M/L]  | [H/M/L]     | [Description] | [How to prevent] |

### Affected Systems
- **Frontend:** [List components/pages affected]
- **Backend:** [List APIs/services affected]
- **Infrastructure:** [List deployment/config affected]
- **Dependencies:** [List packages/libraries affected]

### Test Strategy (TDD-First)
- **New tests to write first:** [List the tests or behaviors to lock in]
- **Existing tests to extend:** [List test files or areas to expand]
- **Test types:** [Unit | Integration | UI | Contract | E2E]
- **Coverage goal (optional):** [Baseline → Target]
- **Expected failures:** [Which tests should FAIL before implementation]

### Test Quality Standards

Tests must follow behavior-driven principles:
- **Describe behaviors, not methods:** Test names read like specifications
- **Decouple from implementation:** Tests survive refactoring
- **Arrange-Act-Assert:** Every test follows this structure
- **Test boundaries, not internals:** Use public APIs only
- **No tautological tests:** Tests must call real code, not verify `1 === 1`
- **No conditional assertions:** Use definitive assertions that fail when elements are missing
- **No time-based waits for negatives:** Use fake timers or explicit scheduling control to cover the delay window
Use this checklist as the default standard for test reviews and new tests.

### Flags & Release Strategy (If Applicable)
- **Flag(s):** [ENABLE_* / REL_* / EXP_*]
- **Default values:** [on/off or variant]
- **Rollout plan:** [Local only | Dev | Staged | Full]
- **Metrics to watch:** [Signal(s) to validate]

---

## Stage 2: CHUNK - Task Breakdown

### Chunking Guidance
- Prefer sequential chunks with validation between each.
- Use parallel chunks only when file boundaries and dependencies are clean.
- Each chunk must be executable by a different agent without extra context.

### Dependency Graph
```
CHUNK_0 (Independent) ─────┐
CHUNK_1 (Independent) ─────┼──> CHUNK_N (Sequential, depends on 0-X)
CHUNK_2 (Depends on 0) ────┘
```

### Chunk Definitions

#### CHUNK_0: [Short Name]
**Type:** [Code Change | Config | Testing | Documentation]
**Dependencies:** None | [List chunk IDs]
**Parallelizable:** [Yes | No]
**Risk Level:** [Low | Medium | High]
**Est. Duration:** [X minutes]

**Tasks:**
1. [Specific actionable task]
2. [Specific actionable task]
3. [Specific actionable task]

**Files Modified:**
- [/path/to/file1.ts](path/to/file1.ts) (lines X-Y)
- [/path/to/file2.ts](path/to/file2.ts) (entire file)

**Test-First Notes:**
- [Test to write or update before implementation]

**Verification:**
- [ ] Verification step 1
- [ ] Verification step 2

**Audit Trail Artifacts:**
- [ ] Notes on decisions or trade-offs
- [ ] Test output or screenshots if applicable

---

#### CHUNK_1: [Short Name]
[Repeat structure for each chunk]

---

## Stage 3: EXECUTE - Execution Plan

### Parallel Execution Strategy
```bash
# Spawn N agents in parallel (only if chunks are independent)
agent execute chunk-0 &
agent execute chunk-1 &
agent execute chunk-2 &
wait

# Then sequential validation
agent execute chunk-N-validation
```

### Sequential Dependencies
```
If CHUNK_X must complete before CHUNK_Y:
1. Execute CHUNK_X
2. Validate CHUNK_X output
3. Execute CHUNK_Y with CHUNK_X results as input
```

### Agent Handoff Plan
- **Chunk ownership:** [Name/agent per chunk or "open"]
- **Handoff triggers:** [Token limit reached | Blocked | Timebox hit]
- **Handoff package:** [Link to chunk report + relevant diffs]

### Rollback Strategy
| Chunk | Rollback Method | Recovery Time |
|-------|-----------------|---------------|
| CHUNK_0 | `git checkout file.ts` | 30 seconds |
| CHUNK_1 | [Specific rollback steps] | [Estimate] |

---

## Critical Files Reference

### Files to Modify
1. [/path/to/critical-file1.ts](path/to/critical-file1.ts) - [Brief description of changes]
2. [/path/to/critical-file2.ts](path/to/critical-file2.ts) - [Brief description of changes]

### Files to Verify (Read-Only)
1. [/path/to/test-file.test.ts](path/to/test-file.test.ts) - [What to verify]
2. [/path/to/integration.ts](path/to/integration.ts) - [What to verify]

### Files to Ignore
- `node_modules/` (auto-managed)
- `dist/` (build artifacts)
- Large build artifacts or exported reports in `_attic/` (keep active sprint docs in scope)

---

## Testing & Verification

### TDD & Test Harness (Required)
- **Test command:** [e.g., `npm run test`]
- **Harness location:** [CI file/path if relevant]
- **TDD scope:** [What must be test-driven in this sprint]
- **Test types:** [unit | integration | e2e]
- **Mocks/fixtures:** [What needs mocking or test data]
- **New/updated tests:** [List file paths]

### Pre-Execution Checks
- [ ] `dev` branch is clean (`git status` shows no uncommitted changes)
- [ ] Sprint branch created off `dev`: `feature/YYYY-MM-DD-sprint-name`
- [ ] Currently on sprint branch (not `dev` or `main`)
- [ ] Dependencies installed (`npm install` successful)
- [ ] Test command verified locally (same as harness)
- [ ] Tests passing (if applicable)

### Post-Execution Checks
- [ ] All builds succeed (`npm run build`)
- [ ] Dev server starts (`npm run dev`)
- [ ] Tests pass (`npm test`)
- [ ] Manual testing complete (see test plan)
- [ ] No new console errors/warnings
- [ ] Performance metrics acceptable
- [ ] Version bumped in `package.json` (patch for fixes, minor for features)

### Test Plan
| Test Case | Steps | Expected Result | Pass/Fail |
|-----------|-------|-----------------|-----------|
| [Case 1]  | 1. [Step] 2. [Step] | [Expected outcome] | ☐ |
| [Case 2]  | 1. [Step] 2. [Step] | [Expected outcome] | ☐ |

### Validation Evidence (Audit Trail)
| Artifact | Location | Notes |
|----------|----------|-------|
| Test output | [path or command output] | [What it proves] |
| Screenshots/logs | [path] | [What it proves] |

---

## Success Metrics

### Quantitative Metrics
- **Build Time:** [Baseline: X ms] → [Target: Y ms]
- **Bundle Size:** [Baseline: X KB] → [Target: Y KB]
- **Test Coverage:** [Baseline: X%] → [Target: Y%]
- **Security Score:** [Baseline: X vulnerabilities] → [Target: 0]

### Qualitative Metrics
- User experience: [Improved | Unchanged | Degraded]
- Code maintainability: [Improved | Unchanged | Degraded]
- Documentation: [Complete | Needs update | Missing]

---

## Sprint Structure (Directory Layout)

Create sprint folder: `_attic/planning/ai-sprints/YYYY-MM-DD-sprint-name/`

**Required Files:**
```
YYYY-MM-DD-sprint-name/
├── README.md                       ← Sprint overview (this template)
├── 00-directory-structure.md       ← Guide for agents (what to ignore)
├── chunk-0-[short-name].md         ← Execution prompt for chunk 0
├── chunk-1-[short-name].md         ← Execution prompt for chunk 1
├── chunk-N-validation.md           ← Final validation prompt
└── RESULTS.md                      ← Post-sprint report (after completion)
```

**Optional Files:**
```
├── RISKS.md                        ← Detailed risk analysis
├── ARCHITECTURE.md                 ← System design changes
├── DECISIONS.md                    ← Key choices and rationale
├── RELEASE_FLAGS.md                ← Flag defaults and rollout steps
└── sub-plans/
    └── chunk-X-subplan.md          ← If a chunk needs its own planning agent
```

---

## Chunk File Format (CRITICAL)

**Each chunk file MUST be independently executable with minimal context.**

Every `chunk-X-[name].md` file should follow this exact structure:

```markdown
# CHUNK_X: [Short Descriptive Name]

## Execution Agent Prompt

You are an execution agent responsible for [specific task in one sentence].

## Context

**Vulnerability/Feature:** [What you're fixing/building]
**Severity/Priority:** [MEDIUM/HIGH/etc.]
**Scanner/Source:** [Semgrep/User Request/etc.]
**Issue:** [Brief description of problem]
**Goal:** [What success looks like in one sentence]

**Current State:**
- [Bullet point of relevant context]
- [Another relevant fact]
- [Current behavior or state]

## Problem Analysis

[Detailed explanation of the problem - this section can be extensive with:
- Code examples showing the issue
- Risk assessment
- Why this needs fixing
- Alternative approaches considered]

## Your Tasks

### 1. Read Current Implementation
```bash
# Commands to inspect the current code
cat path/to/file.ts | sed -n 'X,Yp'
```

Study [what to look for].

### 2. Write Failing Test First (RED)

**Test File:** `path/to/file.test.ts`

**New Test (MUST FAIL BEFORE IMPLEMENTATION):**
```typescript
test('describes expected behavior in plain language', () => {
  // Arrange
  const input = setupTestData();

  // Act
  const result = functionUnderTest(input);

  // Assert - verify externally observable behavior
  expect(result).toEqual(expectedOutcome);
});
```

**Run test to verify it fails:**
```bash
npm test -- --testPathPattern="file.test.ts"
# REQUIRED: Test must FAIL at this point
# If it passes, the test isn't validating new behavior
```

**Why it should fail:**
- [Explain what behavior doesn't exist yet]

### 3. Implement the Fix (GREEN)

**File to Modify:** `path/to/file.ts`

**Target:** [Specific function/component/section]

**Changes Required:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Complete Implementation:**
```typescript
// Full code example showing exactly what to change
```

**Why This Works:**
- [Reason 1]
- [Reason 2]

### 4. Verify Test Now Passes (GREEN)

```bash
npm test -- --testPathPattern="file.test.ts"
# REQUIRED: Test must PASS now
# If it still fails, implementation is incomplete
```

### 5. Refactor (REFACTOR)

Review the implementation for:
- [ ] Code duplication that can be extracted
- [ ] Naming clarity
- [ ] Unnecessary complexity

**After any refactoring, re-run tests:**
```bash
npm test
# REQUIRED: All tests must still pass
```

### 6. Final Verification

**Build Test:**
```bash
npm run build
# Expected: Success message
```

**Verification Commands:**
```bash
# Specific checks
grep -n "pattern" file.ts
# Expected: What you should see
```

### 7. Manual Testing (if needed)

[Manual testing steps]

## Success Criteria

All checks must pass before reporting completion:
- [ ] Test failed BEFORE implementation (RED verified)
- [ ] Test passes AFTER implementation (GREEN verified)
- [ ] Specific check 1
- [ ] Specific check 2
- [ ] Build succeeds
- [ ] All tests pass
- [ ] No regressions

## Files Modified
- `path/to/file1.ts` (lines X-Y)
- `path/to/file2.ts` (entire file)

## Audit Trail
- **Decisions:** [Key choices and rationale]
- **Evidence:** [Test output, screenshots, or logs]
- **Flags/Release Notes:** [If applicable]

## Report Template

When complete, report:
```
CHUNK_X STATUS: ✅ SUCCESS / ❌ FAILED

TDD Cycle:
- RED (test failed before): [YES/NO]
- GREEN (test passes after): [YES/NO]
- REFACTOR (cleanup done): [YES/NO/N/A]

[Metric 1]: [PASS/FAIL]
[Metric 2]: [YES/NO]
[Metric 3]: [Value or status]

Issues: [None / List any problems encountered]
```

## Security Impact / Change Summary

### Before:
- [Current state]
- [Issues]

### After:
- [New state]
- [Improvements]

## References
- [Relevant documentation]
- [Related vulnerabilities/features]
```

### Chunk Format Rules

**MUST HAVE:**
1. ✅ **Execution Agent Prompt** - Clear role definition ("You are...")
2. ✅ **Context** - Structured with bold labels (Vulnerability, Goal, etc.)
3. ✅ **Your Tasks** - Numbered steps following Red-Green-Refactor
4. ✅ **Failing Test First** - Test code that MUST fail before implementation
5. ✅ **Success Criteria** - Including "Test failed before, passes after"
6. ✅ **Report Template** - Standardized status format

**SHOULD HAVE:**
- Problem Analysis section with detailed explanation
- Complete code examples (not just snippets)
- Verification commands with expected output
- "Why This Works" explanations

**DON'T:**
- Reference external files for critical info (agent must have everything needed)
- Use vague instructions ("fix the bug" - be specific)
- Skip the RED step (writing failing test first)
- Skip verification steps
- Forget to include expected outputs
- Write tests that verify mocks are defined (test behavior, not setup)
- Write tautological tests that prove `1 === 1`

### Example Reference

See working examples:
- `_attic/planning/ai-sprints/2026-01-08-security-vulnerabilities/chunk-0-esbuild-update.md`
- `_attic/planning/ai-sprints/2026-01-09-additional-security-fixes/chunk-5-chart-xss.md`

---

## Execution Commands Reference

### Setup
```bash
# Create sprint folder
mkdir -p "_attic/planning/ai-sprints/YYYY-MM-DD-sprint-name"
cd "_attic/planning/ai-sprints/YYYY-MM-DD-sprint-name"

# Copy this template
cp ../SPRINT-PLANNING-TEMPLATE.md README.md
```

### Common Commands
```bash
# Check current state
git status
npm list [package-name]
npm run build

# Verify changes
git diff
git diff --name-only
git log --oneline -5

# Test locally
npm run dev
npm test
npm run lint
```

### Validation
```bash
# Check security
npm audit
[security-scanner] scan

# Check bundle
npm run build
du -sh dist/

# Check types
npx tsc --noEmit
```

---

## Post-Sprint Documentation

### Sprint Retrospective (Complete After Sprint)

**What Went Well:**
- [Success 1]
- [Success 2]

**What Could Be Improved:**
- [Improvement 1]
- [Improvement 2]

**Lessons Learned:**
- [Lesson 1]
- [Lesson 2]

**Action Items for Future Sprints:**
- [ ] [Action 1]
- [ ] [Action 2]

### Sprint Metrics (Actual Results)

**Execution Time:**
- Planned: [X minutes]
- Actual: [Y minutes]
- Variance: [+/- Z%]

**Chunks Completed:**
- Planned: [N chunks]
- Actual: [M chunks]
- Blocked: [List any blocked chunks]

**Issues Encountered:**
- [Issue 1: Description and resolution]
- [Issue 2: Description and resolution]

---

## Example: 2026-01-08 Security Vulnerabilities Sprint

This template was derived from the successful security vulnerability remediation sprint:

**Folder:** `_attic/planning/ai-sprints/2026-01-08-security-vulnerabilities/`

**Structure:**
- ✅ README.md (sprint overview)
- ✅ 00-directory-structure.md (agent guidance)
- ✅ chunk-0-esbuild-update.md (SCA fix)
- ✅ chunk-1-timing-safe-auth.md (Auth hardening)
- ✅ chunk-2-semgrep-config.md (False positive suppression)
- ✅ chunk-3-validation.md (Integration testing)

**Outcome:**
- 4 medium vulnerabilities → 0 active vulnerabilities
- 0 regressions introduced
- 30-45 minute execution time
- Parallel execution of 3 independent chunks

**Key Success Factors:**
1. Clear dependency graph (3 parallel → 1 sequential)
2. Detailed chunk prompts (agents knew exactly what to do)
3. Comprehensive validation plan (caught issues early)
4. Text-efficient guidance (agents didn't waste time reading irrelevant files)

---

## Template Checklist

Before starting a new sprint, ensure:
- [ ] Sprint metadata filled out
- [ ] Objectives clearly defined
- [ ] Chunks identified with dependencies
- [ ] Critical files listed
- [ ] Validation plan defined
- [ ] Rollback strategy documented
- [ ] Test-first plan documented
- [ ] Audit trail artifacts identified
- [ ] Sprint folder created with all required files

---

## Test Anti-Patterns to Avoid

When writing or reviewing tests, watch for these red flags:

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| `expect(mock).toBeDefined()` | Verifies setup, not behavior | Test that mock was called with expected args |
| `if (x.length > 0) { expect... }` | Assertion may never execute | Assert existence first, then check properties |
| `await new Promise(r => setTimeout(r, X))` | Flaky timing | Use `waitFor()` or fake timers |
| `expect(1 === 1).toBe(true)` | Tautological, tests nothing | Call real code and verify outcomes |
| `test('processData works')` | Vague name | Describe behavior: `'returns processed data for valid input'` |
| Mocking the class under test | You're not testing anything | Mock dependencies, not the subject |

---

**Template Version:** 1.2
**Last Updated:** 2026-01-26
**Maintainer:** Tone Dragons Dev Team
**Changelog:**
- v1.2 (2026-01-26): Added Branch Discipline section requiring clean `dev` and feature branch workflow
- v1.1 (2026-01-25): Enhanced TDD section with explicit Red-Green-Refactor cycle, added test quality standards and anti-patterns
