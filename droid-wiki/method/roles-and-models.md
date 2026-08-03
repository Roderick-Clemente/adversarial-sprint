# Roles and models

Five roles, three hard separation constraints, and one hand-curated provenance map. The role and model policy is PRD §7; the stages the roles run are PRD §5, detailed in [Workflow](./workflow.md).

> A note on section numbers: the role table is **PRD §7**. **PRD §6** is the adjacent human judgment policy: the `oversight` setting, covered at the end of this page.

## The five roles

| Role | Default tier | Required separation | Tool policy |
|---|---|---|---|
| Planner / orchestrator | Frontier | — | Read-only during planning; orchestration tools |
| Plan reviewer | Frontier | ≠ planner family | Read-only |
| Test designer | Frontier or mid | ≠ executor family | Test-file edit + focused test execution |
| Executor | Cheap / fast | — | Approved implementation files + test and build commands |
| Validator | Mid / frontier | ≠ executor family | Read-only repo + test and build execution |

Three things are worth reading off that table.

**The separation constraints are pairwise, not global.** Only three pairs are constrained: planner ≠ reviewer, test designer ≠ executor, executor ≠ validator. The planner and the executor may share a family. The reviewer and the validator may be the same family, or the same model. Adding constraints that the method does not need would make model assignment harder for no gain.

**The executor is the only role with implementation write access, and it is the cheapest.** That is the cost hypothesis made concrete: the expensive thinking is in the three roles that plan, review, and design tests, all of which are read-only or test-only.

**Tool policy differs per role, and that is why the roles are separate Droid definitions.** PRD §8 records that consolidating the three Droid definitions into "prompt variations" was proposed during review and rejected: the roles carry different tool policies (plan reviewer read-only, test designer with test-file write, validator read-only plus execution) and different hard family constraints. Collapsing them collapses the invariants they exist to enforce. The rule stated there is *cut packaging, never role separation*.

One role assignment is still open. PRD §16 lists whether the **test designer is the plan-reviewer model or a third independent model** in v1 as an undecided question, as it does the default model assignments themselves.

## What a model family is

Family is **declared model provenance**, not a marketing label and not a cost tier: Anthropic/Claude, OpenAI/GPT, Google/Gemini, DeepSeek, and so on. Open-weight derivatives must declare their upstream base family. Unknown provenance is treated as unknown and **cannot satisfy a hard separation constraint**.

Two models from the same lab at different price points are the same family. Two models with similar benchmark scores from different labs are different families. The property the method wants is uncorrelated priors and training, and price is not a proxy for that.

## Why provenance is curated by hand

The plugin owns a versioned `model-families.json`. PRD §4 is direct about what it is:

> Provenance is maintained by hand, not detected.

The reason is that detection is not available. Many hosted providers will not declare an upstream base family, and **nothing in the runtime can verify a claim of provenance** even when one is made. A model can be asked what it is; the answer is a self-report, and the method already treats self-reports as inadmissible where a guarantee is required. That is the same reasoning that keeps the autonomy tier out of the enforcement path ([Probe 8](../probes/probe-8-self-declared-risk.md)).

So `model-families.json` is a curated file with an **owner and a review date**, not an inference. The failure behaviour follows from that:

- Any model absent from the map resolves to `unknown`.
- `unknown` cannot satisfy a hard separation constraint.
- A run that needs a separation constraint satisfied by an `unknown` model **stops**, rather than being optimistically admitted.

That is invariant 7, explicit degradation, applied to provenance. PRD §4 calls the maintenance burden a known cost and accepts it deliberately. PRD §16 leaves the initial source of truth for the file open.

## What is recorded per run

Every run records, for every role: the **resolved** model ID, the provider, the family, the role, and **whether a fallback occurred**. A fallback that violates a role constraint stops the run.

Resolved is the operative word. The requested model and the model that ran are different facts, and only the second one tells you whether the constraint held. Phase 0 found that the `droid exec -o json` result envelope does not contain the model that ran at all. The only runtime source is the session transcript's `message.modelId` and the startup context block.

Models are **explicitly pinned** for v1. Factory's automatic router may recommend candidates, but it may not choose or fall back across a hard family constraint without a new preflight check.

## Reasoning effort and cost tiers

Cost tier is a default, not dogma. An executor may be escalated one tier after a single failed attempt if the chunk exceeds its declared complexity ceiling, and the run records the reason, the incremental cost, and the model change. Repeated escalation means the chunking was wrong, so the chunk is re-chunked rather than escalated again.

Reasoning effort needs its own preflight check, because Phase 0 found the platform will not perform one. `phase-0/GO-NO-GO.md` puts it in the Phase 1 build order as part of the per-role invocation wrapper: **reasoning effort validated against the model's advertised list**, before the invocation rather than after.

## What Phase 0 established about model resolution

All from [Probe 2](../probes/probe-2-fallback-safety.md), scoped to `droid` 0.186.0.

| Behaviour | Consequence for role pinning |
|---|---|
| An invalid `--model` ID **fails closed** at exit 1 | A typo cannot silently become a different family. This is the one place the platform fails loudly, and the method depends on it |
| A valid model ID **resolves exactly** | Explicit per-role pinning works. One `droid exec --model <id>` per role is the supported surface |
| `--model auto` resolves to a concrete model **the caller cannot predict** | Unusable for role-pinned work. `phase-0/GO-NO-GO.md` states the rule as *never use `--model auto`* |
| `-r xhigh` on a model that does not support it **silently resolves to `off`** at exit 0 | Maximum reasoning to none, no warning, success exit code. Validate reasoning effort ourselves |
| `usage.factory_credits` is **per run** | One invocation per role attributes cost per role directly — which partially unblocks Probe 7 and hypothesis H3 |

The first and fourth rows together are the shape of the platform Phase 0 describes: an invalid *model* is an error, an invalid *reasoning effort* is a silent downgrade. Neither is guessable from the documentation, and only one of them is safe. See [Silent green](../findings/silent-green.md).

Per-role pinning via the Mission flags `--worker-model` and `--validator-model` is not available, because those flags are only valid with `--mission` and `droid exec --mission` performs no work while reporting success ([Probe 1](../probes/probe-1-model-pinning.md)).

### The runtime check

Recording the resolved model is not the same as enforcing the constraint, so the family gate policy of the reference guard does the enforcing. It reads `message.modelId` from the session transcript's **startup context**, which is available from turn 0, and denies when the resolved model is outside the expected family. Because startup context precedes the first turn, the gate fires **before any tool acts**, so a wrong-model run is stopped rather than detected afterwards. Full description in [The reference guard](../findings/reference-guard.md).

**One gap is open.** No real fallback was induced. Probe 2 used `--model auto` and an explicit cross-family ID as proxies for a substitution. Quota exhaustion and server-side substitution are untested, and `phase-0/GO-NO-GO.md` names **custom and BYOK endpoints as the most plausible real silent fallback**, measured not at all.

## Hypothesis H3: role-tiered models reduce cost

> Frontier planning and review plus cheaper execution will cost less than an all-frontier run while preserving hidden acceptance-test results.

PRD §4 states H3 with a condition attached, and the condition is unusual enough to be worth quoting the intent: **H3 is conditional on Probe 7.** If Phase 0 could not produce per-role credit or token attribution at usable granularity, H3 is excluded from the PRD §13 evaluation and v1 makes **no cost claim at all**. The reasoning is that an unmeasured cost claim is worse than a missing one, particularly in a demo, because it invites a question that cannot be answered with evidence.

Phase 0's contribution is that the attribution mechanism exists after all, and it does not need missions: `usage.factory_credits` is reported per run, so invoking once per role yields per-role credits directly in the result envelope. That partially unblocks Probe 7.

How H3 would actually be tested is PRD §13: three bounded pilot tasks from identical repository snapshots (a single frontier model self-planning and self-reviewing, an all-frontier separated-role run, and the role-tiered adversarial run) run with the same goals, criteria, tool permissions, elapsed-time cap, and hidden tests. The targets are no decrease in hidden acceptance-test pass rate against the all-frontier separated-role arm, and at least 25% lower credit or token cost, reported as a goal rather than a guaranteed outcome.

Two things sit alongside the cost measurement. Retry loops can erase the savings, which PRD §14 mitigates with per-role budgets and hard retry caps. A cheap executor that needs three attempts is not cheap. And the hidden tests stay out of **every** agent's context including the validator's, because a validator that can see them can coach toward them.

## Oversight: the human role

PRD §6 controls how often a human is consulted, without weakening any hard gate.

| Setting | Human gates |
|---|---|
| `high` | Plan approval; all semantic, factual and test disagreements; every high-risk chunk; every rejection; final PR |
| `medium` (default) | Plan approval; unresolved high or unknown findings; course-changing chunks; re-plan events; repeated rejection; final PR |
| `low` | Plan approval; blockers and unknown classifications; budget or scope breach; repeated rejection; final PR |

Plan approval and the final PR appear at every level. Unknown disagreement classifications **fail toward review**, not auto-dismissal. Stylistic findings never block on their own. And the hard invariants in PRD §4 apply at every oversight level. `low` buys fewer interruptions, not fewer guarantees.

Queued decisions are batched, and each item explains what changed, why the run paused, the competing positions, the evidence, the cost of delay, and the available actions.

PRD §16 records that `oversight` may not be the right public name; "judgment density" was considered more memorable but less immediately clear.

## Related

- [Invariants](./invariants.md) — invariant 1 (family separation) and invariant 7 (explicit degradation) in full
- [Workflow](./workflow.md) — which role runs which stage
- [Probe 2](../probes/probe-2-fallback-safety.md) — the model resolution evidence
- [Glossary](../overview/glossary.md), [Findings](../findings/index.md)
