# Open questions

Recorded so they are not mistaken for settled. Phase 0 answered enough to justify a GO, and an honest reading of it is that most of the amber cells turn green only once code we have not written yet exists. The items below come from PRD §16, the known unknowns in `phase-0/GO-NO-GO.md`, and the limits sections of the probe records.

An unmeasured thing recorded as unmeasured is a finding. An unmeasured thing left ambiguous is a defect.

## Unprobed and unreached

### Invariant #4 — valid RED before GREEN was never probed

Rated **unprobed, low risk** in the go/no-go scorecard, on the reasoning that it is pure orchestration: run the test, capture the exit code, assert it failed for the expected reason. No platform capability is in question.

Low risk is not zero risk. The invariant's whole content is the distinction between a behavioural failure and an infrastructure one — a syntax error, an import error, a missing fixture, an empty test selection, a timeout, or an unrelated assertion failure are all **invalid RED** and all produce a non-zero exit code. Nothing has yet demonstrated that classifier working on real output. It should be built with the never-trust-exit-0 rule attached, as [Invariants](../method/invariants.md) sets out.

### Probe 5 — rejection routing was never reached

Blocked by Probe 1: the test requires a Mission whose validator stage rejects, and `droid exec --mission` executes nothing. There is no rejection to route.

The consequence is already absorbed — the wrapper owns the state machine — but the question itself is untested rather than answered. [Probe 3](../probes/probe-3-context-isolation.md) adds a reason it may stay unanswerable in the form originally asked: Factory's own shipped mission validator, `scrutiny-feature-reviewer.md`, documents its inputs as including `worker-transcripts.jsonl`. If native validation is transcript-anchored by construction, a working rejection-routing surface would still be unusable for an adversarial gate. That reading is **unverified** and is the first thing to check the moment missions execute.

### Probe 7 — usage attribution is only partially unblocked

`usage.factory_credits` is per run, and in a command-orchestrated design each role is its own `droid exec` invocation, so per-role credits arrive in each envelope with no correlation work. That is the half H3 needs, and it means H3 stays in the §13 evaluation.

Still open: whether OpenTelemetry traces can be correlated back to individual role invocations, and whether attribution survives inside a single multi-role run. Neither is needed for H3 under the current design, so both are deferred rather than closed — and the narrower form still has to hold up once the orchestrator actually exists.

### Whether hooks fire on a subagent's tool calls

Unresolved out of [Probe 6](../probes/probe-6-plugin-boundary.md). The canary saw the parent's `Task` call, but the subagent made no tool calls of its own, so the measurement was never taken.

If they do not fire, a subagent is a hole in invariant #3 and in every other policy the reference guard carries. The go/no-go says to close this early because it is cheap; it is also the single most consequential unmeasured item on this page, since a guard that does not cover delegated work is a guard with a documented bypass. Also unmeasured on the same surface: `PostToolUse`, `Stop` and `SubagentStop`, of which `SubagentStop` is the natural place to validate a validator's output.

## Questions for the vendor

### Does `riskLevel` cause the permission decision, or merely ride along?

The correlation across [Probe 8](../probes/probe-8-self-declared-risk.md)'s seven runs is perfect and the mechanism is undocumented, but the tier might classify the command independently with the model's label sitting beside it. A hook cannot rewrite the label, so **the two explanations are not separable from outside the CLI.**

This matters because it sets how strongly the probe's caveat should be stated. If the tier classifies independently, the self-report concern weakens considerably. The record deliberately files this as inferred, not proven, and as a question to ask Factory before asserting it publicly.

### Why is `.factory/hooks.json` not read?

Observed, not explained. Four canary locations, one fired. The documentation lists the non-working path as the project-scope primary, and no diagnostic is emitted either way. Nobody outside the CLI knows whether this is a bug, a deprecation mid-flight, or a loader-ordering accident — which means nobody can predict which side an upgrade lands on. That is exactly the class of behaviour that changes without a release note, and it is why every probe record carries its CLI version.

### Can session search be disabled by policy?

Unmeasured. If `droid search` can be turned off at the settings or organisation layer, that is the first real mitigation for the leak path in [Probe 3](../probes/probe-3-context-isolation.md)'s addendum, rather than a guard bolted on top of a feature working as designed.

## Measurement gaps

### No real fallback was ever induced

[Probe 2](../probes/probe-2-fallback-safety.md) used `--model auto` and an explicit cross-family ID as **proxies** for a fallback. Neither is one. Quota exhaustion and server-side substitution are untested, and **custom/BYOK endpoints are the most plausible source of a real silent fallback** and were not measured at all.

The gate itself is demonstrated — it denied on a family mismatch before any tool acted — so what is unproven is the trigger, not the response. Invariant #7 rests on that distinction.

### Probe 8 measures one model's calibration

Seven runs, one model (`claude-opus-5` at `high` reasoning), one host. Enough to establish the label-to-permission threshold and to prove the label moves under argument; **not** enough to bound how far it moves. Whether any model will emit `low` for a mutating command is untested, and a negative across four framings is not proof of a floor. `--auto medium` was never exercised. The probe must be re-run per executor model, which puts it inside the H3 evaluation rather than beside it.

### Interactive mode is unmeasured

Every probe used `droid exec`. Hook loading may differ interactively, which is where a human operator actually works.

### Two cross-family read-only Droids were never stood up as a pair

The Phase 0 exit criteria list this as amber. Read-only enforcement is proven ([Probes 3](../probes/probe-3-context-isolation.md) and [6](../probes/probe-6-plugin-boundary.md)) and cross-family pinning is proven ([Probe 2](../probes/probe-2-fallback-safety.md)), but the two components have not been run together as the pair the design needs.

## Product decisions still open

From PRD §16, with current status where Phase 0 moved one.

| Open decision | Status |
|---|---|
| Exact `QuantumBank` pilot behaviour, after Phase 0 reconnaissance | open |
| Default model assignments, and the source of truth for the initial `model-families.json` | open |
| Whether Mission validation can express all retry and re-plan transitions, or a command-level state machine is required | **answered by Phase 0** — command-level, forced by Probe 1 |
| Whether the test designer is the plan-reviewer model or a third independent model in v1 | open |
| Artifact path and retention policy for repos that should not commit run evidence | open — `phase-0/evidence/` is a local choice for this repo's probes and explicitly does not settle it |
| Whether `oversight` is the right public name; "judgment density" is memorable but less immediately clear | open |
| Product name — "Adversarial Sprint" is descriptive but may overemphasise conflict over independence | open |
| What "replayable" means for the demo (§12) | open, and load-bearing |
| Whether the Phase 0.5 manual baseline harness ships publicly alongside the plugin, or stays an internal comparison instrument | open |

Two of those deserve expanding.

**Naming.** Both "Adversarial Sprint" and `oversight` are flagged in §16 as unsettled, for related reasons: each names the mechanism in a way that may misdescribe the intent. The method's value is independence, not conflict, and §13 is explicit that disagreement is not a success gate — a name that foregrounds adversarialism invites exactly the manufactured findings the precision metric exists to penalise.

**Replayability.** Models are stochastic, so same input → same tokens is not achievable and should not be implied. Same input → same *verdict* is defensible, and even that needs measuring across repeat runs before it is asserted in front of an audience. §16 says to pin the wording before the demo narrative is final, because a reviewer will ask.

## Upstream defects found

All with reproductions committed. The common thread across the first three: **the failure is indistinguishable from success at the exit code** — see [Silent green](../findings/silent-green.md).

| # | Defect | Severity | Found by |
|---|---|---|---|
| 1 | `droid exec --mission` is a no-op reporting success — 0 turns, 0 tokens, 0 credits, exit 0 | **High** — blocks the entire mission surface | [Probe 1](../probes/probe-1-model-pinning.md) |
| 2 | Project `.factory/hooks.json` is silently never read, though documented as the project-scope primary location | **High** — a security control that appears installed and is not | [Probe 4](../probes/probe-4-hook-blocking.md), confirmed from the other side by [Probe 6](../probes/probe-6-plugin-boundary.md) |
| 3 | Unsupported `--reasoning-effort` resolves to `off` rather than erroring or clamping to the nearest supported value | **High** — silent maximum-to-minimum degradation | [Probe 2](../probes/probe-2-fallback-safety.md) |
| 4 | `DROID_PLUGIN_ROOT` handed to plugin hooks is the literal sentinel `/PLUGIN_ROOT_NOT_EXPANDED_ERROR`, though `${DROID_PLUGIN_ROOT}` does expand in the hook's `command` string | Medium — scripts must take the plugin root as an argument | [Probe 6](../probes/probe-6-plugin-boundary.md) |
| 5 | A local marketplace is keyed by directory basename rather than the `name` field in `marketplace.json`; installing by the manifest name fails with a misdirecting `Run /marketplace add first` | Low | [Probe 6](../probes/probe-6-plugin-boundary.md) |
| 6 | Uninstall stops the hook but leaves `enabledPlugins: {}`, `extraKnownMarketplaces: {}` and a stale plugin cache behind — plugin operations mutate user-level config and do not fully clean up | Low — expect drift across install cycles | [Probe 6](../probes/probe-6-plugin-boundary.md) |

Also untested on the distribution surface and worth closing before relying on it: remote git-marketplace install, `--scope user`, and the settings-driven `extraKnownMarketplaces` team rollout. Mission artifacts inside plugins remain unanswerable while defect 1 stands.

## Related

- [Design decisions](./design-decisions.md) — what these questions did not block
- [Probes](../probes/index.md) — each record ends with its own limits section
- [Findings](../findings/index.md) · [Silent green](../findings/silent-green.md) · [The reference guard](../findings/reference-guard.md)
- [Security](../security.md) — the security-relevant subset of this page
- [Invariants](../method/invariants.md) — the scorecard these gaps sit against
