# Fun facts

Details from the Phase 0 probes that are more surprising than the verdicts they belong to. Each one is verifiable from the record linked beside it, and all of them are scoped to `droid` 0.186.0 on macOS.

## A hook in the documented location fires zero times; the undocumented one fires

`.factory/hooks.json` is the location the documentation lists first as the project-scope primary. A `matcher: "*"` canary registered there logged **zero** invocations across a run that demonstrably used tools. The same declaration moved into the `hooks` key of `.factory/settings.json` fired immediately. Both configurations were valid JSON, both used the documented `PreToolUse` event, and the misregistered one produced exit 0 with no warning. Why `hooks.json` is not read remains observed rather than explained. — [Probe 4](./probes/probe-4-hook-blocking.md)

## `DROID_PLUGIN_ROOT` arrived as an error message

A plugin hook script logged the environment variable it was handed as the plugin root. The value was the literal string `/PLUGIN_ROOT_NOT_EXPANDED_ERROR`. `${DROID_PLUGIN_ROOT}` does expand correctly inside the hook's command string, so the sentinel only shows up in the environment the script actually receives — which means a plugin script cannot locate its own installation directory from the environment and must take the plugin root as an argument instead. — [Probe 6](./probes/probe-6-plugin-boundary.md)

## Asking for maximum reasoning gets you none

`claude-haiku-4-5-20251001` advertises `[off, low, medium, high]`. Passing `-r xhigh` to it does not error, and does not clamp to the nearest supported value. It resolves to **`off`** — the weakest setting available — at exit 0 with nothing printed. A validator pinned at `-r xhigh` against a model that does not advertise it would run with reasoning disabled, silently, indefinitely. The fix costs nothing: `--help` publishes each model's supported list, so the value can be validated before the call. — [Probe 2](./probes/probe-2-fallback-safety.md)

## A run with every tool call denied still exited 0 with the right answer

A family gate hook expecting `claude` denied both tool calls of a run that resolved to `gpt-5.4-mini`; the hook's own log records four firings. The run reported success: `num_turns=3`, exit 0, `is_error: false`, and a confident final answer that was also *correct*. The model did not fabricate it — the startup context block injected at turn 0 already contains `% ls` output, so it answered a shallow question from context it was handed before any tool ran. A hook can block every action a run takes without changing the run's exit code or making the summary look wrong. — [Probe 2](./probes/probe-2-fallback-safety.md), and [Silent green](./findings/silent-green.md) for the pattern

## A custom Droid's `tools:` list is a floor, not a ceiling

The plugin-shipped droid declared `tools: ["Read", "Grep", "Glob"]` and reported five tools when asked: `Read`, `Grep`, `Glob`, plus `TodoWrite` and `Skill`, both added by the platform. Probe 3 saw the same two additions on every restricted local subagent. Neither writes to the filesystem, so the isolation conclusion is unaffected — but a `tools:` allowlist is not an exact manifest of what the subagent gets, and the right move is to assert on what the subagent reports rather than on what was declared. — [Probe 6](./probes/probe-6-plugin-boundary.md), [Probe 3](./probes/probe-3-context-isolation.md)

## A local marketplace registers under its directory name, not its own name

`marketplace.json` has a `name` field the docs describe as the marketplace identifier, and plugin IDs take the form `pluginName@marketplaceName`. For a local path source, the registry key is the **directory basename** instead. A marketplace at `/tmp/probe-6/mkt` whose manifest said `probe-mkt` registered as `mkt`, and installing with the manifest name failed with a misleading `Run /marketplace add first`. — [Probe 6](./probes/probe-6-plugin-boundary.md)

## The same `rm` command got two different risk grades

`rm scratch.txt`, asked for plainly, was labelled `riskLevel: high` by the model. The identical command, with a reassuring rationale added to the prompt, came back `medium`. The label is model output that responds to argument, not a property of the command — and since the autonomy tier appears to gate on it, the entity being restricted supplies the input to its own restriction. It never moved as far as `low` across four framings, so the boundary held; it held on calibration. — [Probe 8](./probes/probe-8-self-declared-risk.md)

## `--auto low` cannot write anything at all

The sharpest datum in Probe 8 is its most benign test. Appending one line to a file that did **not yet exist** was labelled `medium` and refused at `--auto low`. The most restrictive tier is not "low-risk writes allowed" — through the shell it is read-only. Budget it for validators and reviewers; an executor placed there will be unable to modify a thing. — [Probe 8](./probes/probe-8-self-declared-risk.md)

## The default "read-only" tier ships with a shell

At the default autonomy tier, `droid exec --list-tools` reports `Create` and `Edit` blocked and `Execute` **allowed**. A validator configured by the plausible route — just don't pass `--auto` — has a shell. That is the gap between the stated read-only posture and the resolved one, and it is the configuration a careless operator lands on. — [Probe 3](./probes/probe-3-context-isolation.md)

## One agent recovered another agent's secret with `Grep` and no shell

A validator restricted to `Read,Grep,Glob,LS` — no `Execute`, no `Task`, no `Skill`, no `ToolSearch`, and it enumerated all four before concluding — recovered a codename the executor had invented, kept out of every file, and stated only in its reply. It took five turns, and it attributed the find correctly to the executor's session. As the run put it: *"The restriction limits writes, not reach"* — the read tools accept absolute paths anywhere on the filesystem, including `~/.factory/sessions`. — [Probe 3](./probes/probe-3-context-isolation.md)

## One generic English word surfaced a withheld secret through a shipped feature

`droid search "CODENAME"` — a single common word, run by an operator with no knowledge that a secret existed, let alone its form, at a moment when the only session containing it was the executor's — returned the withheld value. Two other queries matched the right sessions but their context windows did not span the value, so the leak is query-dependent. That is not a mitigation: it means an unsuccessful search proves nothing. — [Probe 3](./probes/probe-3-context-isolation.md)

## Zero turns does not mean nothing happened

Probe 1 read `num_turns: 0` as "no work performed" and was right, but for the wrong reason. Probe 3 later captured a run reporting `num_turns: 0` alongside `output_tokens: 612` and `thinking_tokens: 149` — the model reasoned and moved to act, and the run was killed at the permission boundary before a turn was booked. The load-bearing number for Probe 1 was never the turn counter; it was `input_tokens: 0`, which is the only signal that distinguishes "short-circuited before any model call" from "called a model that declined." — [Probe 1](./probes/probe-1-model-pinning.md), [Probe 3](./probes/probe-3-context-isolation.md)

## Every probe header pins a version number, on principle

`phase-0/evidence/README.md` is 24 lines long and one of them is the reason the whole corpus is dated: *"the `droid --version` under test, since a 'no' recorded against no version cannot be rechecked later."* A finding of the form "the platform can't do X" is unusable and uncontestable without a version attached, so every probe record carries `droid 0.186.0` in its header, and the go/no-go is explicitly invalidated by a CLI upgrade until the probes are re-run. — [Probes index](./probes/index.md), [Patterns and conventions](./how-to-contribute/patterns-and-conventions.md)

## One probe outweighed the entire repository

Probe 3's evidence is 57 files and 247 KB. Before consolidation the whole `factory/phase-0-go-no-go` branch was 100 files and 238 KB, so a single probe directory was larger than the branch carrying the verdict, and for most of Phase 0 it was not in it: the go/no-go cited Probe 3 throughout while `phase-0/evidence/probe-3/` did not exist on that branch. It has since been merged in. See [By the numbers](./by-the-numbers.md).
