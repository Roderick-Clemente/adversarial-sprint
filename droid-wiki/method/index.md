# Method

The plugin does not invent a workflow. It packages one that has been run by hand for months: one model plans, a model from a different family attacks the plan, both audit the test strategy, a cheap agent implements small chunks, and an independent agent validates each result. The specification for it is `PRD.md`; the hand-run form is `templates/SPRINT-PLANNING-TEMPLATE.md`.

## The thesis

Quality in agentic coding does not come from a smarter model. It comes from three things:

- **Structural separation of roles across model families.** Two passes from one model family are one opinion twice. The author of a plan is a poor grader of it, and the author of an implementation is a poor grader of that.
- **Expensive thinking front-loaded into planning.** Frontier models plan, review, and design tests. Cheap models do the mechanical execution. Hypothesis H3 in PRD §4 predicts this costs less without reducing task success, and it is measured, not assumed.
- **Executable evidence over self-assessment.** A chunk is complete when a test that was written by someone else, locked by hash, and observed failing for the intended reason now passes. Not when the executor says so.

PRD §2 puts the point more sharply: the product problem is not "use two models," it is making independence and evidence **structural properties of the run** instead of prompt suggestions.

## The four headline properties

From `README.md`. All four are meant to be enforced rather than suggested.

1. **Family separation.** The plan reviewer is not the planner's family. The validator is not the executor's family.
2. **Fresh review context.** The validator sees the approved spec, the diff, read-only repository state, and test evidence. It never sees the executor's reasoning or self-assessment.
3. **Independent test authorship.** The executor cannot write or modify the tests that judge it. Locked by content hash, enforced by a hook.
4. **Valid RED before GREEN.** Behavior-changing work cannot start until the intended assertion has run and failed *for the expected reason*. A syntax error is not a RED.

These four are the public summary. The complete set is eight runtime invariants, listed with their enforcement mechanism and current Phase 0 status in [Invariants](./invariants.md).

## What the method does not claim

The honesty constraints are part of the design, not a disclaimer bolted on afterwards.

- **Different model families are an independence control, not proof.** They reduce correlated blind spots. They do not make a second opinion correct.
- **Tests are executable evidence, not truth.** A locked test can be wrong. That is why test authorship is separated from implementation and why a held-out hidden set exists (PRD §13). Because humans author both, hidden tests buy Goodhart protection rather than insulation from human bias.
- **Two reviewers agreeing means no known dispute, nothing more.** PRD §5.3 states this directly: agreement is the absence of a known dispute, not evidence of correctness.
- **The plan review is single-blind, not double-blind.** The reviewer reads the plan, so it inherits the plan's framing, vocabulary, and choice of what to make salient. PRD §5.3 refuses to call this "blind review" for exactly that reason.
- **A demo illustrates the mechanism; it does not validate the hypotheses.** PRD §13 keeps product acceptance and thesis validation separate, and treats a clean null result as valid data.

What the method buys is a governed process that makes assumptions, disagreements, and evidence **visible**.

## Pages

| Page | What it covers |
|---|---|
| [Invariants](./invariants.md) | All eight runtime invariants, how each is enforced, and what Phase 0 proved about each |
| [Workflow](./workflow.md) | The end-to-end stage machine, its gates, and which stages the command wrapper now owns |
| [Roles and models](./roles-and-models.md) | The five roles, family-separation constraints, `model-families.json`, and reasoning-effort policy |
| [Sprint template](./sprint-template.md) | Guide to `templates/SPRINT-PLANNING-TEMPLATE.md`, the hand-run ancestor of the plugin |

Terms used throughout are defined in [Glossary](../overview/glossary.md). What the platform can actually enforce is in [Findings](../findings/index.md).
