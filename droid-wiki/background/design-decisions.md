# Design decisions

Each decision below is recorded with what was chosen, why, and the evidence behind it. Some were forced by a probe result; some are judgement calls the spec argues for explicitly. Where a decision was forced, the probe is named, because a decision without its evidence is an opinion that will be relitigated.

## At a glance

| Decision | Driver |
|---|---|
| Command-orchestrated, not Mission-native | forced by [Probe 1](../probes/probe-1-model-pinning.md) |
| Evidence in `phase-0/evidence/`, not `.factory/` | `.factory/` is gitignored |
| One reference guard, three policies | [Probes 2, 3, 4](../probes/index.md) converged on one primitive |
| Register hooks via `settings.json` or a plugin | forced by [Probe 4](../probes/probe-4-hook-blocking.md) |
| Ship as a plugin | [Probe 6](../probes/probe-6-plugin-boundary.md) |
| Model families curated by hand | no runtime can verify provenance |
| Single-blind review, not double-blind | honesty about what blinding buys |
| Hidden tests for Goodhart protection, not bias insulation | humans author both sets |
| Superseded records kept under a banner | how a wrong call was caught is evidence |
| Branch per agent, commits as the baton | the method applied to its own authors |

## Command-orchestrated, not Mission-native

**Decision.** The orchestrator is a command-level state machine that invokes `droid exec` once per role. Factory is the execution substrate, not the workflow engine.

**Why.** `droid exec --mission` performs no work and reports success at 0.186.0 — zero turns, zero tokens, zero credits, exit 0, with a real prompt in a real git repo at `--auto high`. A control run of plain `droid exec` on the same machine took a turn and consumed tokens, so the defect is scoped to mission mode; `input_tokens: 0` means it short-circuits before any model call. The per-role model flags `--worker-model` and `--validator-model` exist on this version but are **only valid with `--mission`**, so the entire Mission-native path is closed. It also blocks Probes 5 and 7.

**Evidence.** [Probe 1](../probes/probe-1-model-pinning.md), and the replacement path is verified: [Probe 2](../probes/probe-2-fallback-safety.md) shows explicit `--model <id>` resolving exactly and failing closed at exit 1 on an invalid ID.

**This was anticipated.** PRD §8 carried the contingency before any probe ran:

> **Probe 5 contingency.** If Missions cannot route a validator rejection back to retry or re-plan, Phase 3 is redesigned around a command-orchestrated state machine with Factory as the execution substrate. **That redesign happens before any Phase 2 work begins**, not mid-Phase 3 — which is why Probe 5 runs first in Phase 0.

The mapping from assumption to replacement is in `phase-0/GO-NO-GO.md`. One row is a gain rather than a loss: `usage.factory_credits` is **per run**, so one invocation per role attributes cost directly, which partially unblocks Probe 7 and H3 without missions.

**Cost.** Invariant #6 (blocking validation) becomes our code rather than a platform feature. Real but bounded, and it removes a dependency on an untested platform behaviour.

## Evidence lives in `phase-0/evidence/`, not `.factory/adversarial-sprints/`

**Decision.** Phase 0 probe evidence is committed under `phase-0/evidence/`, one directory per probe.

**Why.** PRD §9 nominates `.factory/adversarial-sprints/<run-id>/` as the default artifact path, but `.factory/` is gitignored here as local tool state, so anything written there is invisible to git. Phase 0's exit criteria require a *captured* run artifact, and §9 explicitly permits "another configured artifact path."

**Evidence.** The reasoning is recorded in `phase-0/evidence/README.md`, which also draws the boundary: this does **not** settle the §16 open decision about artifact paths and retention for repositories that should not commit run evidence. That is a product question about arbitrary target repos. This is a local choice for this repo's probes.

## One reference guard, three policies

**Decision.** A single `PreToolUse` hook carries the locked-test guard, the isolation guard, and the family gate — not three separate hooks.

**Why.** Three probes independently arrived at the same primitive. All three policies need the same three things: the tool payload, `transcript_path` to learn what actually happened, and a fail-closed default. Writing them once means one canary-based install check, one fail-closed code path to review, and one place where a payload shape nobody anticipated is handled. Three hooks means three chances to get the fail-closed rule wrong, and Probe 4's A4 shows what one such mistake costs.

| Policy | Denies when | Invariant | From |
|---|---|---|---|
| Locked-test guard | the target path, or a shell command mentioning it, is a hash-pinned test | #3 | [Probe 4](../probes/probe-4-hook-blocking.md) |
| Isolation guard | the command touches `~/.factory/sessions` or invokes `droid search` | #2 | [Probe 3](../probes/probe-3-context-isolation.md) |
| Family gate | `message.modelId` is outside the expected family | #1, #7 | [Probe 2](../probes/probe-2-fallback-safety.md) |

**Evidence.** `phase-0/GO-NO-GO.md` makes it the first item in the Phase 1 build order and forbids starting items 3–5 before it is proven firing in the target repo. The family gate reads the resolved model from the transcript's startup context, available from turn 0, so it denies **before any tool acts**. Details in [The reference guard](../findings/reference-guard.md).

## Register hooks via `settings.json` or inside a plugin

**Decision.** Hooks are registered in the `hooks` key of `.factory/settings.json`, or shipped inside a plugin. Never in a project-scope `.factory/hooks.json`.

**Why.** `.factory/hooks.json` is silently never read at 0.186.0, though the documentation lists it as the project-scope primary location. Canary hooks at four locations: `hooks.json` fired 0 times, user-scope `hooks.json` 0, legacy `hooks/hooks.json` 0, `settings.json` **1**. A misregistered hook produces no warning and exit 0 — a security control that appears installed and is not.

**Evidence.** [Probe 4](../probes/probe-4-hook-blocking.md). This trap produced a wrong BLOCKED verdict inside this very repository before it was caught, which is why the rule is stated as absolute rather than as a preference. The corollary is a practice, not just a config choice: **install a canary and assert it logged.** Configuration being present is not evidence of enforcement.

## Ship as a plugin

**Decision.** The guard, the Droid definitions, the skill and the command all ship inside one installable plugin.

**Why.** A plugin's own `hooks/hooks.json` **does** fire, even though a standalone project-scope `.factory/hooks.json` never does. Same filename, two loaders, no diagnostic either way. A minimal plugin carrying one droid, one skill, one command and one `PreToolUse` hook installed at project scope and **all four activated with no manual repo setup** — install wrote only `enabledPlugins` into the project's `.factory/settings.json` plus a cache copy under `~/.factory/plugins/cache/`. So the design ships as one installable thing rather than a plugin plus a pile of hand-edited settings.

**Evidence.** [Probe 6](../probes/probe-6-plugin-boundary.md), which also confirmed that a plugin droid's `tools:` allowlist is enforced by schema omission, extending Probe 3's result from local to distributed droids.

**The trap that travels with it.** A developer testing the guard standalone in `.factory/hooks.json` will see nothing fire and draw the wrong conclusion — exactly as this repository's own Probe 4 did.

## Model families curated by hand

**Decision.** The plugin owns a versioned `model-families.json` with a named owner and a review date. Provenance is maintained by hand, not detected. Any model absent from the map resolves to `unknown`.

**Why.** PRD §4 states the reasoning directly: many hosted providers will not declare an upstream base family, and **nothing in the runtime can verify a claim of provenance.** Family is declared provenance — Anthropic/Claude, OpenAI/GPT, Google/Gemini, DeepSeek — not a marketing label or a cost tier, and open-weight derivatives must declare their upstream base.

**The consequence is deliberate.** `unknown` cannot satisfy a hard separation constraint, so it stops the run rather than being optimistically admitted. Every run records resolved model ID, provider, family, role, and whether a fallback occurred; a fallback that violates a role constraint stops the run. The maintenance cost of a hand-curated map is accepted rather than wished away.

**Supporting evidence.** [Probe 2](../probes/probe-2-fallback-safety.md) supplies the runtime half: the resolved model is absent from the `droid exec -o json` envelope entirely, but present in the session transcript as `message.modelId` and in the startup context from turn 0. Two rules fall out. **Never use `--model auto`** — it resolved to a concrete model the caller cannot predict, so invariant #1 would hold only by luck. And validate `--reasoning-effort` against the model's advertised list, because `-r xhigh` on a model that does not support it resolves to `off` rather than clamping.

## Single-blind review, not double-blind

**Decision.** The first reviewer pass sees the plan document and repository evidence, but not the planner's private reasoning and not a competing review.

**Why.** That reduces anchoring and performative disagreement. It is deliberately *not* double-blind, and PRD §5.3 records the distinction as a **limitation rather than a feature**:

> The reviewer reads the plan itself, so it inherits the plan's framing, vocabulary, and choice of what to make salient. Calling this "blind review" would encourage exactly the over-trust in independence that the method exists to avoid.

**Why that framing matters.** The whole product claim is that independence is structural. Overstating how much independence a single-blind pass delivers would undermine the claim more than the limitation does. The same posture appears in §13's close: agreement between reviewers is the absence of a known dispute, nothing more.

**Related, from the same section.** `max_review_rounds` stays at 2 for v1. It was challenged during cross-family review of the PRD as too tight for legitimate scope disagreement, and the challenge was **rejected with the reason recorded**: it is a tuning parameter with a human escape hatch already attached, and it should be set from observed non-convergence rates rather than intuition before the first run.

## Hidden tests buy Goodhart protection, not bias insulation

**Decision.** The §13 evaluation uses hidden acceptance tests as the primary external correctness measure, and states precisely what they do and do not provide.

**Why.** Humans author both the locked tests and the hidden tests, so the same blind spots ride along in both. Claiming insulation from human bias would overstate the design. What hidden tests actually detect is the executor satisfying the letter of a test it can see — special-casing the asserted input, implementing to the example rather than the rule. They are the held-out set that measures whether the behaviour was built or the test was beaten.

**Consequence.** Hidden tests stay out of every agent's context **including the validator's**, because a validator that can see them can coach toward them.

**Evidence.** PRD §13, "What hidden tests actually buy."

## Superseded records are kept under a banner

**Decision.** When a verdict is overturned, the original record stays unedited with a banner pointing at the correction. The correction lives beside it.

**Why.** How a wrong call was caught is part of the evidence. Probe 4's original BLOCKED verdict was produced by a config-location trap rather than a runtime limit, and that failure mode — a misregistered hook that produces no warning and exit 0 — is a finding in its own right. Editing the record away would delete the demonstration.

**Evidence.** `phase-0/evidence/probe-4/README.md` is preserved alongside `phase-0/evidence/probe-4/reverify/README.md`. Probe 3 applies the same rule differently: its addendum lists four inline corrections to the main record rather than rewriting the claims, and it **retains two mis-scoped runs** produced by a scripting error, because an accident that refutes your own recommendation is data. The convention is written up in [Patterns and conventions](../how-to-contribute/patterns-and-conventions.md).

## Branch per agent, commits as the baton

**Decision.** Three agents work in this repository — Factory Droid, Codex, Claude Code — sharing one working tree. Branches are named `<agent>/<topic>`, handoff is by `git diff`, and work lands on `main` only after review.

**Why.** Authorship stays obvious in history, a bad run is one `git branch -D`, and nobody reconstructs who wrote what from commit messages. The reviewing agent reads the diff, not the other agent's reasoning — which is the same independence property the runtime is supposed to enforce, applied to the repository's own authors. `AGENTS.md` says so explicitly: role separation is invariant #1 applied to the humans-and-agents layer, not just the runtime. The agent that authored a plan does not approve it; the agent that wrote an implementation does not validate it.

**Two rules that carry weight.** Convention and spec changes stay off feature branches so they do not ride along with unreviewed work. And if the workflow feels clumsy in practice, that is real signal about the design and belongs in `phase-0/README.md` under Notes — the repository is using its own method as an experiment on itself.

**Evidence.** `AGENTS.md`, and the branch topology in [Architecture](../overview/architecture.md). Details in [Development workflow](../how-to-contribute/development-workflow.md).

## Two decisions the PRD made against itself

Worth recording, because both were proposed during a structured cross-family review of the PRD and both were **rejected with the reason written down** — the disposition ledger working as designed.

- **Consolidating the three Droid definitions into "prompt variations"** was rejected in §8. The roles carry different tool policies (plan reviewer read-only, test designer with test-file write, validator read-only plus execution) and different hard family constraints. Collapsing them collapses the invariants they exist to enforce. Cut packaging, never role separation.
- **Raising `max_review_rounds`** was rejected in §5.3, per the reasoning above.

The v1 surface *was* cut, elsewhere: `sprint-report` and `adversarial-plan-review` start as prompts inside the command and graduate to skills only when reuse is demonstrated, `run.schema.json` waits for the state machine to stabilise, and `preflight.sh` starts inline.

## Related

- [Open questions](./open-questions.md) — what these decisions did not settle
- [Probes](../probes/index.md) · [Findings](../findings/index.md) · [Invariants](../method/invariants.md)
- [Architecture](../overview/architecture.md) — the shape these decisions produced
- [Security](../security.md) — the fail-closed rule and the boundaries behind it
