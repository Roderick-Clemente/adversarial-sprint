# Probes

Phase 0 of this repository is a **build gate**. Nothing in Phase 1 starts until eight questions are answered with working probes rather than documentation reading or product assumptions. The framing in `phase-0/README.md` is blunt about why: each probe can kill or reshape the design, and a "no" found here saves weeks.

A probe is not a design document. It is an experiment against a specific version of the Factory `droid` CLI that either demonstrates a capability the [invariants](../method/invariants.md) depend on, or demonstrates its absence. Two of the eight overturned an assumption the spec was resting on, and one of those overturned an earlier probe of its own.

A probe is also a **Phase-0-only device**: one feasibility question aimed at the platform, used solely to decide the build gate. Later phases deliver vertical slices measured against exit criteria, not probes, so nothing after Phase 0 will be recorded this way. See the [Roadmap](../overview/index.md#roadmap) for the arc these eight sit at the front of.

Everything below is scoped to `droid` **0.186.0** on macOS (darwin 24.6.0), with `~/Work/QuantumBank` as the pilot repo. A CLI upgrade invalidates these results until the probes are re-run, and a capability that appears or disappears between versions is itself a finding worth recording rather than a silent correction.

## The evidence standard

`phase-0/evidence/README.md` sets the bar. A probe result is version-scoped and unfalsifiable without provenance, so each directory under `phase-0/evidence/` carries:

- the exact commands run, with exit codes
- raw stdout and stderr, secret-filtered
- the `droid --version` under test, because a "no" recorded against no version cannot be rechecked later
- resolved model IDs where the probe touches model selection, not the requested IDs

Two rules follow from that. **Negative results get the same treatment as positive ones** — a probe that fails is the artifact, not a missing artifact. And **a committed script beats prose**: if a probe cannot be re-run from what is in its directory, it is a claim rather than evidence. Most probe directories ship a `run.sh` for exactly this reason.

Evidence lives under `phase-0/evidence/` rather than the PRD §9 default of `.factory/adversarial-sprints/<run-id>/`, because `.factory/` is gitignored here as local tool state and anything written there would be invisible to git. That is a local choice for this repo's probes and does not settle the §16 open question about artifact paths in target repos.

## The eight probes

| # | Question | Verdict | Record |
|---|---|---|---|
| 1 | Can the installed version pin distinct models to planner, reviewer, worker and validator roles? | **BLOCKED** — `droid exec --mission` performs no work and reports success: 0 turns, 0 tokens, 0 credits, exit 0 | [Probe 1](./probe-1-model-pinning.md) |
| 2 | Can the plugin resolve *effective* model IDs at runtime and abort before a family-violating fallback? | **CONDITIONAL PASS** — the family gate is buildable and demonstrated; found a silent reasoning downgrade | [Probe 2](./probe-2-fallback-safety.md) |
| 3 | Do custom Droids give genuinely fresh context and enforceable tool restrictions? | **PASS with a gap** — tool restriction is real by schema omission; the executor's transcript is readable off disk | [Probe 3](./probe-3-context-isolation.md) |
| 4 | Can hooks reliably block edits to locked test files and persist command evidence? | **PASS, with one sharp condition** — overturns an earlier BLOCKED verdict | [Probe 4](./probe-4-hook-blocking.md) |
| 5 | Can Mission validation route a rejection to retry or re-plan, or must the command wrapper own that state machine? | **Unreached** — blocked by Probe 1 | see below |
| 6 | Which settings, hooks and Mission artifacts are safely distributable inside a plugin? | **PASS** — one droid, one skill, one command and one hook all activate on install | [Probe 6](./probe-6-plugin-boundary.md) |
| 7 | Can credit and token usage be associated with a run at per-role granularity? | **Unreached, but partially unblocked** | see below |
| 8 | Does the autonomy tier gate on the model's self-declared `riskLevel`? | **PASS with a named caveat** — the label is model output that responds to argument | [Probe 8](./probe-8-self-declared-risk.md) |

Aggregate verdict: **GO, with one mandatory design change** — build it command-orchestrated rather than Mission-native. See `phase-0/GO-NO-GO.md`, summarised in [Findings](../findings/index.md).

## Probe 8 was not in the original seven

Probe 8 was added during Phase 0, and it exists because of Probe 4. The `Execute` payloads that Probe 4's canary hook captured turned out to carry `riskLevel` and `riskLevelReason` alongside `command` — the model's own grade for the command it is about to run. That raised a question the original seven did not ask: if the autonomy tier acts on that label, the entity being restricted supplies the input to its own restriction. Probe 4's re-verification record names this explicitly as Probe 8's starting point.

This is the intended shape of Phase 0. A probe that turns up a new question is doing its job.

## Probe 5 — rejection routing, unreached

**Question:** can Mission validation route a rejection back to retry or re-plan, or must the command wrapper own that state machine?

**Why it mattered:** it decides whether this is a Factory-native Mission or a command-level orchestrator that calls Factory. That changes the build materially.

**Status:** blocked by Probe 1. The test requires constructing a Mission whose validator stage rejects and observing whether the Mission loops back to a prior stage, and `droid exec --mission` executes nothing at 0.186.0. There is no rejection to route.

The consequence is already absorbed into the design. Probe 5 being unreachable triggered the PRD §8 command-orchestrated contingency, which means the wrapper owns the retry and re-plan state machine. Invariant #6 (blocking validation) is therefore our code rather than a platform feature: the cost is real but bounded, and it removes a dependency on an untested platform behaviour.

## Probe 7 — usage attribution, partially unblocked

**Question:** can credit and token usage be associated with a run at per-role granularity?

**Why it mattered:** hypothesis H3 — that role-tiered models cut cost without cutting task success — is unmeasurable without it. "Roughly 50% cheaper" is not a claim worth making without evidence behind it.

**Status:** recorded as likely blocked by Probe 1, on the reasoning that a zero-credit mission attributes nothing. That reasoning was sound for the Mission-native design and is now partly obsolete.

**What unblocks it:** `usage.factory_credits` in the `droid exec -o json` result envelope is **per run**. Every captured run carries it. Probe 4's canary run, in `phase-0/evidence/probe-4/reverify/raw/canary-run.json`, reports `"usage": {"input_tokens": 4, "output_tokens": 193, "cache_read_input_tokens": 15786, "cache_creation_input_tokens": 15971, "factory_credits": 45023}`. In a command-orchestrated design each role is its own `droid exec` invocation, so each role's credits arrive in its own envelope with no correlation work required. Per-role cost attribution was thought to depend on missions. It does not.

What remains open is the part Probe 7 also asked about: whether OpenTelemetry traces can be correlated back to individual role invocations, and whether attribution survives inside a single multi-role run. Neither is needed for H3 under the command-orchestrated design. H3 stays in the §13 evaluation, conditional on this narrower form of Probe 7 holding up when the orchestrator exists.

## Where the evidence lives

Probe branches follow the `<agent>/<topic>` convention from `AGENTS.md`, and evidence was landed onto the Phase 0 chain as each probe finished.

| Probe | Evidence path | Branch |
|---|---|---|
| 1 | `phase-0/evidence/probe-1/` | `factory/phase-0-go-no-go` (originally `factory/probe-1-evidence`) |
| 2 | `phase-0/evidence/probe-2/` | `factory/phase-0-go-no-go` (originally `factory/probe-2-fallback-safety`) |
| 3 | `phase-0/evidence/probe-3/`, addendum in `phase-0/evidence/probe-3/ADDENDUM-droid-search.md` | `factory/phase-0-go-no-go` (originally `factory/probe-3-context-isolation`) |
| 4 | `phase-0/evidence/probe-4/`, current verdict in `phase-0/evidence/probe-4/reverify/` | `factory/phase-0-go-no-go` (originally `factory/probe-4-hook-blocking`) |
| 6 | `phase-0/evidence/probe-6/` | `factory/phase-0-go-no-go` (originally `factory/probe-6-plugin-boundary`) |
| 8 | `phase-0/evidence/probe-8/` | `factory/phase-0-go-no-go` (originally `factory/probe-8-self-declared-risk`) |

`factory/phase-0-go-no-go` carries all six records. Probe 3 was the exception for a while: recorded off the chain, it was the one probe whose evidence the Phase 0 branch did not have, even though the go/no-go cited it throughout. Consolidation merged it in, along with probes 1 and 4 and the steering-channel commit. The original per-probe branches were kept rather than deleted, so the commit history of any single probe is still readable on its own.

## Reading order

If you only read two, read [Probe 4](./probe-4-hook-blocking.md) and [Probe 2](./probe-2-fallback-safety.md). Between them they produce the one primitive the whole design rests on, described in [The reference guard](../findings/reference-guard.md), and three of the four instances of the failure mode described in [Silent green](../findings/silent-green.md). Terms used throughout are defined in the [Glossary](../overview/glossary.md).
