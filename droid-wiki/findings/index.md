# Findings

What Phase 0 concluded, as distinct from what each individual probe measured. The [probe records](../probes/index.md) are the evidence; this section is the reading of it.

Everything here is scoped to `droid` **0.186.0** on macOS, with one deliberate exception: [Cross-version validation](./cross-version-validation.md) re-runs the primitives on **0.180.0** to separate what is a platform property from what is a property of one patch release.

## The verdict

**GO, with one mandatory design change: build it command-orchestrated, not Mission-native.** Recorded in `phase-0/GO-NO-GO.md`.

Nothing came back red. Four invariants are green, three are amber with a known mitigation, and one was never probed.

| Invariant | Status | Basis |
|---|---|---|
| #1 family separation | Green | Explicit `--model` resolves exactly and fails closed on an invalid ID ([Probe 2](../probes/probe-2-fallback-safety.md)) |
| #2 fresh review context | Amber | Real at the agent channel, absent at the filesystem; needs an active guard ([Probe 3](../probes/probe-3-context-isolation.md)) |
| #3 independent test authorship | Green | Hook blocks the agent's own edit and the run continues ([Probe 4](../probes/probe-4-hook-blocking.md)) |
| #4 valid RED before GREEN | **Unprobed** | No platform dependency identified, so it was deprioritised. See [Open questions](../background/open-questions.md) |
| #5 immutable evidence | Green | Hook-side logs survive the run; the contract appears in the transcript ([Probe 4](../probes/probe-4-hook-blocking.md)) |
| #6 blocking validation | Amber | Mission-native routing is unavailable; the command wrapper owns the state machine ([Probe 1](../probes/probe-1-model-pinning.md)) |
| #7 explicit degradation | Amber | The runtime degrades silently, so the orchestrator must detect it ([Probe 2](../probes/probe-2-fallback-safety.md)) |
| #8 human merge | Green | Nothing in the design merges anything; PR creation is the terminal step |

Full per-invariant detail in [Invariants](../method/invariants.md).

## The two findings that matter

Everything else in Phase 0 is detail around these.

### [Silent green](./silent-green.md)

The platform cannot fail loudly. Four independent subsystems reported success for work that did not happen: a mission that ran zero turns, a hook that never loaded, a reasoning level silently downgraded to `off`, and a run whose every tool call was denied still returning a plausible answer.

Consequence: **exit code is not a signal.** Every gate in the design asserts on observed effects and on the guard's own log instead.

### [The reference guard](./reference-guard.md)

Three invariants collapse into one `PreToolUse` hook of roughly thirty lines. It reads `transcript_path` to inspect what actually happened, fails closed on any payload it cannot interpret, denies with exit 2 so the agent receives the contract and the run continues, and registers through `.factory/settings.json` or a plugin.

Consequence: the enforcement layer is one small, testable component rather than three mechanisms with three failure modes.

## Confirmed at a second version

[Cross-version validation](./cross-version-validation.md) re-ran the primitives on `droid` 0.180.0, six patch releases older. The plugin hook and the hash-locked test block both hold with no rescue modifications, so the enforcement layer is not a 0.186-only artifact.

The comparison also reclassified one defect. `.factory/hooks.json` **works** at 0.180.0 and is silent at 0.186.0, which makes it a regression with a known-good prior version rather than a standing bug. A single-version finding cannot tell those apart.

## Secondary conclusions

**Missions are not usable at this version.** `droid exec --mission` performs no work. The per-role model flags exist but are `--mission`-only, so they are unreachable. This forced the PRD §8 contingency and is what turns the plugin into a command-orchestrated state machine. It is not fatal: one `droid exec --model <id>` per role pins the model just as well, and it attributes cost per role for free because `usage.factory_credits` is per run.

**Permission tiers are not a substitute for a guard.** Removing the `Edit` tool did not protect a file, because the agent used a shell. Dropping to the default tier killed the run outright. Neither is what the design needs, which is a specific path protected and a live agent that reports the contract.

**The autonomy tier gates on a self-report.** `Execute` carries a `riskLevel` the model assigns to its own command, and the same `rm` was graded `high` unprompted and `medium` once the prompt offered a rationale ([Probe 8](../probes/probe-8-self-declared-risk.md)). Whether the label *causes* the decision is inferred, not proven. The practical response is a hook that denies on mismatch between the label and the command.

**A plugin is a viable distribution unit.** A droid, a skill, a command and a hook install together from a marketplace, and the plugin's own `hooks/hooks.json` fires even though a standalone one does not ([Probe 6](../probes/probe-6-plugin-boundary.md)).

**Twice, a control appeared to hold because the model was polite.** Probe 4's A3 and Probe 3's V3–V5 both nearly produced false passes. The house rule that came out of it: force the bypass, or you are measuring manners. See [Patterns and conventions](../how-to-contribute/patterns-and-conventions.md).

## Six upstream defects

Found incidentally while probing something else. Tabulated with their probes in [Open questions](../background/open-questions.md).

`droid exec --mission` is a no-op · `.factory/hooks.json` is never read *(a regression — it works at 0.180.0)* · `-r xhigh` resolves to `off` · `DROID_PLUGIN_ROOT` arrives as a literal error sentinel · a marketplace registers under its directory basename rather than its manifest name · uninstall leaves configuration and cache residue.

## What this section does not claim

Phase 0 answered whether the platform **can** enforce the invariants. It did not test whether the method **works**, which is the H1/H2/H3 evaluation in PRD §13 and belongs to a later phase.

Three probes are incomplete: #4 was never probed, #5 was never reached, and #7 is only partially unblocked. Every probe record ends with its own limits section, and those limits are part of the finding rather than a caveat on it.

## Related

- [Cross-version validation](./cross-version-validation.md) — the same primitives at `droid` 0.180.0
- [Probes](../probes/index.md) — the evidence these conclusions rest on
- [Invariants](../method/invariants.md) — what is being enforced and why
- [Open questions](../background/open-questions.md) — what is still unresolved
- [Design decisions](../background/design-decisions.md) — what changed because of these findings
- [Security](../security.md) — the trust boundaries these findings map
