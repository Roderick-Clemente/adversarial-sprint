# Silent green

The platform's default failure mode is **reporting success for work that did not happen**. Four probes hit it independently, in four different subsystems, without anyone looking for it. It is the single most consequential Phase 0 result, and it shapes both the design of the plugin and how anyone should work with the CLI.

The name is this repository's own; see [Glossary](../overview/glossary.md).

## The four sightings

| # | What was asked for | What happened | Exit | Probe |
|---|---|---|---|---|
| 1 | A mission to add a comment to a README | 0 turns, 0 input tokens, 0 credits, no edit | **0** | [Probe 1](../probes/probe-1-model-pinning.md) |
| 2 | A hook registered at the documented project path | Never loaded, never fired | **0** | [Probe 4](../probes/probe-4-hook-blocking.md) |
| 3 | Maximum reasoning effort (`-r xhigh`) | Resolved to `off`, the weakest setting | **0** | [Probe 2](../probes/probe-2-fallback-safety.md) |
| 4 | A run under a family gate that denied every tool call | Plausible, correct-looking answer returned | **0** | [Probe 2](../probes/probe-2-fallback-safety.md) |

None of these emitted a warning. None set `is_error`. Each is individually defensible as a design choice; together they establish a property of the platform that a control system has to be built around.

## Why each one is worse than it first looks

### A mission that does nothing

`droid exec --mission` with a real prompt, in a real git repository, at `--auto high`, produced `numTurns: 0` and exited 0. The benign explanations were ruled out one by one: the prompt was present, the repository had a committed file, the permission tier cleared the edit, and the requested model was already the default.

An orchestrator that treats exit 0 as "the stage completed" would have marked this stage green and moved on. Every downstream invariant would then be reasoning about work that never occurred.

### A hook that never loads

The most dangerous of the four, because it fails **in the direction of permitting things**. A guard declared in `.factory/hooks.json`, the documented project-scope location, is not read. The declaration is syntactically valid, the file is in the right place, and nothing anywhere reports a problem. Every tool call is simply allowed.

There is no channel through which the platform says "your hook did not load". The only way to know is to make the hook prove it fired, which is why a `matcher: "*"` canary is a non-optional part of any guard rig here. Its absence is exactly what produced a wrong verdict the first time Probe 4 was run.

### Reasoning silently downgraded

`--model claude-haiku-4-5-20251001 -r xhigh` resolved to reasoning effort `off`. Not clamped to `high`, the nearest supported value. Not rejected. **Downgraded to the weakest setting available**, at exit 0, with no warning.

The control run with `-r high` resolved exactly, so this is specific to requesting an unsupported level. The failure is directionally wrong in the worst way: the caller asked for maximum deliberation and received none, and the run looks identical from outside.

For this project it lands directly on invariant #7, explicit degradation. A degradation that the runtime performs and does not report cannot be made explicit by asking the runtime.

### A correct answer from a fully blocked run

The subtlest one. In Probe 2's test T5, a family gate denied **every** tool call in the run. The process still exited 0 with `is_error: false` and returned an answer that looked right.

The model did not fabricate. Its startup context already contained a directory listing, so it answered from what it had been handed before turn 1. The gate worked perfectly and the run reported success anyway.

The uncomfortable version of this: **an orchestrator checking exit codes would conclude the stage passed, and a human reading the output would agree with it.** Only the hook's own log shows that nothing was permitted to happen.

## What follows from it

### Never gate on exit code

The rule is absolute in this repository. See [Debugging](../how-to-contribute/debugging.md) for the mechanics. In order of trustworthiness:

1. **The observed effect.** Did the file change? Compare hashes before and after.
2. **The guard's own log.** A hook that writes its own record is the only component whose report is not mediated by the model.
3. **Per-tool `is_error`** inside the session transcript, not the envelope's top-level `is_error`.
4. **`num_turns` and token counts.** Zero work is visible as zero turns.
5. The process exit code, which distinguishes almost nothing.
6. The agent's own summary text, which is model output.

Note that (4) is what caught the mission no-op, and (2) is what caught the blocked-but-green run. Neither would have been noticed by (5) or (6).

### Prove the control fired

A control that cannot demonstrate it ran is indistinguishable from one that did not load. Every guard in the design carries a positive-confirmation path: a canary during development, and a written log in production. If the orchestrator cannot find evidence that the guard executed, that is a failed stage, not a passed one.

This is the difference between "no violation was reported" and "the guard ran and reported no violation". On this platform those are very different statements.

### Assert the shape, not just the status

Each `run.sh` in `phase-0/evidence/` prints an expected-shape summary rather than only a pass or fail. A stage in the plugin does the same: it declares what a successful result looks like (turns greater than zero, this file changed, this string present in the guard log) and checks against that.

### The security dimension

Silent green is not only a reliability problem. A monitoring system keyed on exit codes would have seen nothing wrong in any of the four cases, including the one where a security control was entirely absent. See [Security](../security.md).

## Scope

All four observations are against `droid` **0.186.0** on macOS. They are behaviours of that version, not permanent properties, and the version pin in every probe header exists so they can be rechecked. Three of the four are recorded as upstream defects in [Open questions](../background/open-questions.md).

The fourth, a blocked run returning a plausible answer, is arguably not a defect at all. The model behaved reasonably given the context it held. That is what makes it the most instructive of the set: **correct component behaviour composing into a misleading system-level result.** No bug report fixes that one. The orchestrator has to be built to expect it.
