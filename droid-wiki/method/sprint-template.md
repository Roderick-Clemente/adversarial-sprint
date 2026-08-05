# Sprint template

`templates/SPRINT-PLANNING-TEMPLATE.md` is the canonical GROK → CHUNK → EXECUTE method, at version 1.2 and 666 lines. It is the hand-run ancestor of the plugin: everything the plugin is meant to enforce, this file currently asks a human to do by hand.

**It is the canonical copy, and this matters.** The header says so in a pinned note: the template originated in a `tone-dragons` planning directory at v1.2 and was then copy-pasted into six-plus repositories, where it started to drift. Improve it here; treat every other copy as stale. The template also instructs the reader to adapt stack specifics per repository (its examples are npm and TypeScript, and become Python and pytest for the `QuantumBank` pilot) and to pair it with the `review-tests` skill and cross-family plan review.

## Structure

| Section | Contents |
|---|---|
| Sprint Metadata | Name, date, sprint type (Security / Feature / Refactor / Bug Fix), priority P0–P3, estimated duration, status |
| Sprint Principles | Low-token execution, standardized practice, audit trail, TDD-first — plus the TDD cycle and branch discipline subsections |
| Sprint Objectives | Primary goal in one sentence, measurable success criteria as checkboxes, explicit out-of-scope list |
| Stage 1: GROK | Context, root cause analysis, risk assessment table, affected systems, test strategy, test quality standards, flags and release strategy |
| Stage 2: CHUNK | Chunking guidance, dependency graph, chunk definitions |
| Stage 3: EXECUTE | Parallel execution strategy, sequential dependencies, agent handoff plan, rollback strategy table |
| Critical Files Reference | Files to modify, files to verify read-only, files to ignore |
| Testing & Verification | TDD harness, pre-execution checks, post-execution checks, test plan table, validation evidence table |
| Success Metrics | Quantitative baselines and targets, qualitative assessments |
| Sprint Structure | The required and optional files a sprint directory must contain |
| Chunk File Format | The full per-chunk document format, marked CRITICAL, with format rules |
| Execution Commands Reference | Setup, common, and validation command blocks |
| Post-Sprint Documentation | Retrospective and actual-versus-planned metrics |
| Template Checklist | Nine pre-start items |
| Test Anti-Patterns to Avoid | Six-row table of red flags with fixes |
| Worked example | The 2026-01-08 security sprint the template was derived from |

The document ends with a version block and changelog: v1.1 added the explicit Red-Green-Refactor cycle and the test quality standards; v1.2 added branch discipline.

## The TDD cycle, as the template states it

```
1. RED      → Write a failing test that describes the expected behavior
2. GREEN    → Write the minimum code to make the test pass
3. REFACTOR → Clean up while keeping tests green
```

The template marks one line **non-negotiable**: the test must fail before implementation when adding new or changed behaviour, and *if it passes, the test is not validating new behaviour*. Exceptions are refactors, test-only cleanups, documentation-only changes, and fixes where a failing test already exists, with the reason documented in the chunk notes. That carve-out is the same one PRD §5.4 formalises, with the difference that the PRD routes the exception to the validator for approval before execution rather than leaving it as a note.

## Branch discipline

Three rules, added in v1.2:

- **Start clean.** The `dev` branch has no uncommitted changes before starting.
- **Sprint branch.** One feature branch off `dev` per sprint, named `feature/YYYY-MM-DD-sprint-name`.
- **Merge back.** The sprint branch merges to `dev` via PR when complete.

The pre-execution checklist re-asserts these as things to verify rather than assume, including "currently on sprint branch (not `dev` or `main`)".

## What a chunk definition contains

In Stage 2, each chunk carries: a type (Code Change / Config / Testing / Documentation), dependencies as chunk IDs or none, a parallelizable flag, a risk level, an estimated duration, numbered actionable tasks, files modified with line ranges, test-first notes naming the test to write before implementation, verification checkboxes, and audit-trail artifacts.

The chunking guidance is the same instinct the PRD hardens: prefer sequential chunks with validation between each, use parallel chunks only when file boundaries and dependencies are clean, and, the requirement everything else hangs on, **each chunk must be executable by a different agent without extra context**.

## The chunk file format

Stage 2 defines the chunk *summary*. A separate section, marked CRITICAL, defines the standalone `chunk-X-[name].md` file that an agent actually executes. Its structure walks the TDD cycle explicitly:

1. Read the current implementation, with the inspection commands given.
2. **Write the failing test first (RED)**: the test file path, the test code, the command to run it, an annotation that the test *must* fail at this point, and a written "why it should fail".
3. **Implement the fix (GREEN)**: file to modify, target, changes required, a complete implementation example, and "why this works".
4. **Verify the test now passes (GREEN)**, with the note that if it still fails, the implementation is incomplete.
5. **Refactor**: duplication, naming, unnecessary complexity, then re-run everything.
6. Final verification: build, plus specific verification commands with expected output.
7. Manual testing, if needed.

Then success criteria (led by "test failed BEFORE implementation" and "test passes AFTER implementation"), files modified, an audit trail of decisions and evidence, and a standardised report template that reports the RED / GREEN / REFACTOR beats as separate YES/NO answers.

The format rules are worth reading as a list of things that went wrong before. **Must have**: an execution agent prompt defining the role, structured context, numbered Red-Green-Refactor tasks, the failing test first, success criteria including "failed before, passes after", and the report template. **Don't**: reference external files for critical information, use vague instructions, skip the RED step, skip verification, omit expected outputs, write tests that verify mocks are defined, or write tautological tests.

## Test quality standards

Stage 1 sets the standard the template asks reviewers to use as their default:

- Describe behaviours, not methods; test names read like specifications.
- Decouple from implementation; tests survive refactoring.
- Arrange-Act-Assert in every test.
- Test boundaries, not internals; public APIs only.
- No tautological tests; tests must call real code.
- No conditional assertions; use definitive assertions that fail when elements are missing.
- No time-based waits for negatives; use fake timers or explicit scheduling control.

The closing anti-pattern table gives each of these a concrete failure and a fix:

| Anti-pattern | Why it is bad |
|---|---|
| `expect(mock).toBeDefined()` | Verifies setup, not behaviour |
| `if (x.length > 0) { expect... }` | The assertion may never execute |
| `await new Promise(r => setTimeout(r, X))` | Flaky timing |
| `expect(1 === 1).toBe(true)` | Tautological; tests nothing |
| `test('processData works')` | Vague name — describe the behaviour instead |
| Mocking the class under test | Nothing is being tested |

This list is close to the validator's test-review criteria in PRD §5.7, which rejects private or internal coupling, weak truthiness, tautologies, conditional assertions, timing sleeps, mocks of the subject under test, and assertions that replay implementation details. The template asks a human to apply it; the PRD makes it a validator's blocking check.

## Sprint directory layout

A sprint is a directory, and the template specifies its contents. Required: `README.md` from the template, `00-directory-structure.md` guiding agents on what to ignore, one `chunk-N-[short-name].md` per chunk, `chunk-N-validation.md`, and `RESULTS.md` after completion. Optional: `RISKS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `RELEASE_FLAGS.md`, and `sub-plans/` for a chunk that needs its own planning agent.

The correspondence with the plugin's run artifacts in PRD §9 is close enough to be recognisable: `RESULTS.md` keeps its name, chunk files become `chunks/`, and the risk and decision documents become `findings.jsonl` with dispositions.

## How the template relates to the plugin

The plugin automates and enforces what the template asks a human to do by hand. The method is the same; what changes is who guarantees it.

| Template asks the operator to | Plugin makes it | Invariant |
|---|---|---|
| Pair with cross-family plan review (header note) | A pinned reviewer model from a different family, checked at preflight and at runtime | 1 |
| Keep the validation chunk's reviewer independent | A validator in a fresh context with no executor transcript, and an isolation guard | 2 |
| Write the failing test first, in the chunk file | A separate test designer authors the test; the executor cannot touch it | 3 |
| Verify the test fails before implementation | A recorded RED with predicted-versus-observed failure and an invalid-RED classification | 4 |
| Not change the test between RED and GREEN | SHA-256 hash comparison across the transition | 5 |
| Treat `chunk-N-validation.md` as a real gate | A rejection verdict that blocks completion in the wrapper's state machine | 6 |
| Notice when the discipline slipped | A guard that fails closed and stops the run | 7 |
| Merge the sprint branch via PR | A branch, local commits, and a PR — never an auto-merge | 8 |

PRD §15 states the gap between the two columns as the demo's argument. Run by hand, the method genuinely works, and that is the point: and it is why the manual baseline must not be strawmanned. The cost is that the operator is the orchestrator, so the process runs at the speed of their attention; the laptop must stay open; nothing is enforced, so a tired operator silently degrades family separation, test locking, and validator independence one at a time; nobody can say what the run cost or which role spent it; and the evidence lives in scrollback.

The template's honest name for its own weakest point is *Sprint Principles*. Principles are conventions an operator maintains. The plugin's contribution is turning eight of them into invariants that fail the run instead.

## Phase 0.5 — ladder as a gate machine

The plugin turn eight principles into invariants, but only four of them (#3 / #4 / #5 / #6) live at chunk level and only four (#1 / #2 / #7 / #8) live at runtime level. A different decomposition applies **to the gate side itself**: a single validator invocation against a single chunk is one run; the *gates* that gate that run are themselves a small machine.

Phase 0.5 wrote that machine as a seven-rung ladder, each rung owning one orthogonal axis. The ladder lives in `tools/` rather than in the plugin because it sits below the plugin's chunk-validation step — its job is to vet the validator's invocation, not the chunk itself.

| rung | axis (one only — failures do not sound as each other) | gate file (committed) |
|------|---|---|
|  1   | the bug-present pin (BASE → HEAD + diff_hash) is reproducible | `tools/fixtures/rung1-grep-gate.py` |
|  2   | the rendered prompt keeps executor reasoning out of the validator's view | `tools/fixtures/rung2-canary-check.py` |
|  3   | the run actually happened (`num_turns > 0`, tokens present, tools exercised) | `tools/fixtures/rung3-gate.py` |
|  4   | validator and executor seats are different model lineages | `tools/fixtures/rung4-family-gate.py` |
|  5   | the validator actually inspected the code, not narrated from KB | `tools/fixtures/rung5-gate.py` |
|  6   | the verdict LITERALLY reports what it claims (decision regex + finding regex) | `tools/fixtures/rung6-gate.py` |
|  7   | a no-op run fails loud (negative control) | `tools/fixtures/rung7-{configA,configB}-digest.json` |

Three rules govern the ladder:

- **One rung owns one axis.** A rung-3 fail is "the run did not happen"; a rung-5 fail is "the validator did not inspect"; a rung-6 fail is "the verdict text does not match the prose". Different axes imply different fixes.
- **Gates assert on reality, never on exit code alone.** Each rung parses the inner-session jsonl, the verifier's verdict text, or both — the gate's exit code is a digest of those assertions, not a stand-alone verdict.
- **Negative controls are committed.** A rung-7 fixture with an empty diff passes rung 3 / 5 / 6 in its pre-fix shape; the brief's intent of fail-loud on no-op is what rung 7 measures.

The seam under the ladder is `tools/adapters/factory.py`, a single public function returning a normalised envelope. The gates consume the normalised shape and never mention the executor by name. Vendor adapters beyond the Factory one (Codex/Anthropic/Ollama) are explicit Phase 4 work; the seam is what permits them.

The ladder was closed with a one-rung fix-up — rung 5.5 — when the gates were found to mint a clean accept-cut from a forged verifier input whose only `tool_use` had no matching `tool_result`. Three aligned gaps aligned into the silent-green: the adapter extracted `is_error=None`, the rung-5 predicate refused only `True`, and no gate read the envelope's run-level `is_error`. The fix changes rung 5's failure condition to `if tc.get("is_error") is not False` and threads the envelope-level check into rung 3 / 5 / 6. The forged fixture ships in `tools/fixtures/rung7b-fakepass/` as the regression guard, gated by `tools/fixtures/rung7b-fakepass-gate.py`. The finding is recorded in [Fake-pass via unmatched tool_use](../findings/fake-pass.md).

The ladder's contribution to the method it shares with this template is also load-bearing. Its `tools/RUN-LEDGER.md` carries the §13 One-vs-N proof: per-validation-loop operator-intervention count drops from N (the prior hand-relay method) to 1 (one auto-routed executor invocation per loop). The principles the template names are conventions; the ladder makes the *gate-level* discipline principle — never gate on exit code — machine-enforced.

## Related

- [Workflow](./workflow.md) — the same GROK/CHUNK/EXECUTE machine as the plugin's stage machine
- [Invariants](./invariants.md) — the eight guarantees the right-hand column above refers to
- [Roles and models](./roles-and-models.md) — who performs each step once it is automated
- [Glossary](../overview/glossary.md)
- `tools/README.md` — the validation primitive canonicalised
- `tools/RUN-LEDGER.md` — five-run ledger and §13 One-vs-N comparison
- `tools/PHASE-0.5-CLOSE.md` — the close criteria with verbatim gate outputs
- [Fake-pass via unmatched tool_use](../findings/fake-pass.md) — the rung-5.5 fix
