# Probe 6 — Plugin distribution boundary

**Verdict: PASS.** A single plugin carries the droid, the skill and the hook, and all three activate on install with no manual repo setup. This is the probe that makes the design shippable as one installable thing rather than a set of instructions for editing config by hand.

| | |
|---|---|
| Question | Which settings, hooks and Mission artifacts are safely distributable inside a plugin? |
| Invariants at stake | [#2, #3, #5, #6](../method/invariants.md) — indirectly, since the plugin is the vehicle that delivers their enforcement |
| CLI under test | `droid` 0.186.0 · **Host:** macOS (darwin 24.6.0) |
| Scratch repo | `/tmp/probe-6/repo`, fresh `git init`, one commit |
| Plugin under test | `phase-0/evidence/probe-6/plugin/` · **Marketplace:** `phase-0/evidence/probe-6/plugin-marketplace/` |
| Record | `phase-0/evidence/probe-6/README.md` · **Raw:** `phase-0/evidence/probe-6/raw/` · **Reproduce:** `phase-0/evidence/probe-6/run.sh` |

## The rig

A minimal plugin, `probe-guard`, with one of each component, published through a local marketplace and installed at project scope:

```
plugin/
  droids/probe-validator.md      # tools: ["Read", "Grep", "Glob"], model: inherit
  skills/probe-marker/SKILL.md
  commands/probe-hello.md
  hooks/hooks.json               # PreToolUse, matcher "*", runs hooks/canary.py
```

| Component | Ships at | Activates on install? | Evidence |
|---|---|---|---|
| **Hook** (`PreToolUse`) | `hooks/hooks.json` | **Yes** | Canary logged 1 invocation on the run's `Execute` call |
| **Droid** (subagent) | `droids/probe-validator.md` | **Yes** | Appears in the `subagent_type` list; invoked successfully via `Task` |
| **Skill** | `skills/probe-marker/SKILL.md` | **Yes** | Appears by name in the model's available-skills list |
| **Slash command** | `commands/probe-hello.md` | **Untested** | `/name` commands are interactive-only; `droid exec` has no surface for them |
| **MCP server** | `mcp.json` | **Not tested** | No MCP dependency in this design |

Install wrote exactly two things: `enabledPlugins` into the **project's** `.factory/settings.json`, and a cache copy under `~/.factory/plugins/cache/`. Nothing else in the repo was touched.

## T1 — the plugin's `hooks/hooks.json` fires, where a project one does not

This is the load-bearing result. [Probe 4](./probe-4-hook-blocking.md) established that at project scope, `.factory/hooks.json` is **never read** — a `matcher: "*"` canary logged zero invocations from it, and only the `hooks` key in `.factory/settings.json` worked.

A plugin declares its hooks in a file called **`hooks/hooks.json`** — the same filename that does nothing standalone. Inside a plugin it fires:

```json
{"hook_event": "PreToolUse", "tool_name": "Execute", "cwd": "/private/tmp/probe-6/repo",
 "plugin_root_env": "/PLUGIN_ROOT_NOT_EXPANDED_ERROR", "ts": "2026-08-03T00:10:53"}
```

The attribution is clean. The repo's `.factory/settings.json` at that moment contained **only** `{"enabledPlugins": {"probe-guard@mkt": true}}` — no `hooks` key at all. The invocation can only have come from the plugin's own declaration, through a separate loader.

So there are two supported registration channels, and the one a distributable plugin needs is the one that looks broken when tested standalone:

| Where the hook is declared | Fires? |
|---|---|
| `.factory/hooks.json`, project scope (the **documented primary**) | no — Probe 4 |
| `~/.factory/hooks.json`, user scope | no — Probe 4 |
| `.factory/settings.json`, `hooks` key | **yes** — Probe 4 |
| **A plugin's `hooks/hooks.json`** | **yes** — this probe |

Good news and a trap in one result. Good news: **the reference guard from Probes 2, 3 and 4 can ship inside a plugin**, which is what "installable product" requires. The trap: `hooks.json` works in one context and is silently ignored in the other, with no diagnostic either way. A developer who tests a guard standalone in `.factory/hooks.json`, sees nothing fire and concludes hooks are broken will be wrong, as this repo's own first Probe 4 was. Both paths have to be documented together in anything shipped. That is [silent green](../findings/silent-green.md) again: no warning, no error, an unguarded run at exit 0.

### `DROID_PLUGIN_ROOT` is a sentinel, not a path

The hook was declared as `python3 ${DROID_PLUGIN_ROOT}/hooks/canary.py`. It ran, so **substitution into the command string works**. But the script read its own environment and found:

```
DROID_PLUGIN_ROOT=/PLUGIN_ROOT_NOT_EXPANDED_ERROR
```

A literal sentinel. A hook script resolving sibling files at runtime via `os.environ["DROID_PLUGIN_ROOT"]` — an entirely reasonable thing to do, and the pattern the docs' own plugin-root advice invites — gets a path that does not exist. It would fail, or worse, mis-resolve quietly.

**Rule for anything shipped: pass the plugin root as an argument in the `command` string, and never read it from the environment inside the script.**

## T2 — droid and skill register with no manual setup

The plugin's droid appeared in the `subagent_type` registry alongside the built-ins and the machine's personal droids, and the skill appeared by name in the available-skills list. Neither needed a repo-local file or any manual step. From `phase-0/evidence/probe-6/raw/T2-droid-skill.json`:

```
**(1) subagent_type values for the Task tool**
- worker
- explorer
- probe-validator
...
**(2) Skill names available to me**
- probe-marker
- agent-browser
...
```

This closes the gap [Probe 3](./probe-3-context-isolation.md) left between "a custom Droid works from a repo-local `.factory/droids/`" and "a custom Droid works when distributed."

## T3 — the plugin droid's allowlist is enforced by schema omission

Invoking `probe-validator` via `Task` and asking it to attempt a write:

> PLUGIN_DROID_REACHED
> Available tools (exact names): `Read`, `Grep`, `Glob`, `TodoWrite`, `Skill`
> File creation attempt: I did not attempt to create [...] I have no write-capable tool available [...] There is no `Create`, `Edit`, `Write`, or shell/`Execute` tool through which a file could be created.

No file was created. This reproduces [Probe 3](./probe-3-context-isolation.md)'s V9/V10 result — the `tools:` allowlist is enforced by **omission from the tool schema**, not by prompt — and extends it to a plugin-shipped droid, which was not previously established.

One detail to carry into implementation. The declared allowlist was `["Read", "Grep", "Glob"]`, three entries, and the droid received **five** tools: the platform added `TodoWrite` and `Skill`. Neither grants a filesystem write, so isolation held, but **`tools:` is a floor for write capability rather than an exact manifest.** Assert on what the subagent reports about itself, as this probe did, instead of trusting the declaration.

## T4 — install, uninstall, and what is left behind

| Step | Observed |
|---|---|
| `droid plugin marketplace add /tmp/probe-6/mkt` | Registered — **but keyed as `mkt`**, the directory basename, not `probe-mkt` from `marketplace.json` |
| `droid plugin install probe-guard@probe-mkt` | **Failed:** `Marketplace "probe-mkt" not found. Run /marketplace add first.` |
| `droid plugin install probe-guard@mkt --scope project` | Succeeded |
| `droid plugin uninstall probe-guard@mkt --scope project` | Succeeded; `enabledPlugins` emptied; canary logged **0** invocations on a subsequent run |
| `droid plugin marketplace remove mkt` | Succeeded |

### The marketplace naming mismatch is an upstream papercut

The docs describe `marketplace.json`'s `name` as the marketplace identifier, and plugin IDs as `pluginName@marketplaceName`. For a local path source the registry key is the **directory basename** instead, and the two are visibly different in the listing output:

```
mkt  (1 plugin)  local:/tmp/probe-6/mkt  "probe-mkt"
```

The error message compounds it by advising `Run /marketplace add first` for a marketplace that was just added successfully. It points at the wrong cause. Anyone following the docs' own local-testing snippet hits this. Minor, but it costs a debugging cycle and belongs in the upstream report — `run.sh` deliberately runs the failing form first so the mismatch is reproduced rather than described.

### Uninstall is functionally complete but not tidy

The hook stopped firing immediately, which is the part that matters. Three residues:

- `enabledPlugins` left as an empty object `{}` rather than removed
- `"extraKnownMarketplaces": {}` left in `~/.factory/settings.json`, where no such key existed before
- the plugin **cache directory survived** at `~/.factory/plugins/cache/mkt-<hash>/probe-guard-<hash>`

None is active. It is still config drift, and it is distribution-relevant: **plugin operations mutate user-level config, and the cleanup is incomplete.** An enterprise rollout should expect drift across install/uninstall cycles.

The probe therefore did not leave the machine as it found it by default. `run.sh` backs up `~/.factory/settings.json` before the install, deletes the probe's own cache entry, and restores the backup explicitly rather than trusting `uninstall` plus `marketplace remove`. It ends by diffing against the backup and asserting the two are byte-identical.

## Scope semantics

`--scope project` put `enabledPlugins` in the repo's `.factory/settings.json`. In this repo `.factory/` is gitignored as local tool state, so **a project-scoped plugin activation would not be committed** and every clone would need its own install. `--scope user` writes to `~/.factory/settings.json` instead, which is per-machine.

For team distribution the documented path is neither: `extraKnownMarketplaces` plus `enabledPlugins` declared in settings, with install scope following where the setting is defined and org-managed settings installing at org scope. That is the mechanism a real rollout targets, and it is **untested here**.

## Design impact

1. **Ship as one plugin.** Droid, skill and hook all activate from a single install with no repo-local setup. The installable-product question is answered yes, which is what makes the [architecture](../overview/architecture.md) distributable.
2. **Put the reference guard in `hooks/hooks.json` inside the plugin.** It fires there, and shipping it that way avoids asking users to hand-edit `settings.json`. If a repo-local guard is ever needed outside a plugin it must go in `.factory/settings.json` under `hooks`.
3. **Never read `DROID_PLUGIN_ROOT` from the environment.** Pass it as a command argument.
4. **Keep Probe 4's install check.** It is now doubly justified: hook registration has two valid locations and one invalid-looking filename that works only in plugin context. Assert a canary actually fired rather than that a config file exists.
5. **Assert the subagent's real toolset** rather than trusting the `tools:` key, which is a floor. Also fail the install check on a read-only role that declares no `tools:` key at all — a [Probe 3](./probe-3-context-isolation.md) requirement, now checkable at the point of distribution.
6. **Expect config drift.** If the plugin ever writes user config itself, it should be idempotent and clean up after itself, because the platform does not.

Rules 2 through 5 are collected with the rest in [The reference guard](../findings/reference-guard.md).

## Limits

| | |
|---|---|
| Not tested | **Whether plugin hooks fire on a subagent's tool calls.** The canary logged the parent's `Task` call, but `probe-validator` made no tool calls of its own, so subagent hook coverage is **unresolved**. This matters for [invariant #3](../method/invariants.md) — a subagent that escapes a locked-test guard is a hole — and should be settled before anything relies on it. |
| Not tested | Plugin hook precedence against a `settings.json` hook declaring the same event, and whether both run. |
| Not tested | Slash commands. `/name` is interactive-only and `droid exec` offers no way to invoke one, so `commands/` is unverified. Not load-bearing here. |
| Not tested | MCP servers (`mcp.json`). No MCP dependency in the design. |
| Not tested | `--scope user`, and the settings-driven `extraKnownMarketplaces` + `enabledPlugins` team rollout, which is the mechanism an enterprise would actually use. |
| Not tested | Install from a **remote** git marketplace. Local path only, so clean-checkout install is unverified. The docs' own pre-share checklist calls this out, and it is the obvious next step. |
| Unanswerable | Mission artifacts, the other half of the probe's question. No Mission artifact was distributable to test because missions do not execute at this version — see [Probe 1](./probe-1-model-pinning.md). Unanswered by construction. |
| Single sample | One plugin, one install, one machine. |

## Related

- [Probe 4](./probe-4-hook-blocking.md) — the registration-channel result that made `hooks/hooks.json` the headline question here rather than an afterthought
- [Probe 3](./probe-3-context-isolation.md) — the schema-omission result this probe confirms for distributed droids, and the install-check requirement it hands over
- [Probe 2](./probe-2-fallback-safety.md) — the third probe converging on the one guard this plugin delivers
- [Probe 1](./probe-1-model-pinning.md) — why the Mission-artifact half of this question has no answer
- [The reference guard](../findings/reference-guard.md) · [Silent green](../findings/silent-green.md)
- [Probes](./index.md) · [Architecture](../overview/architecture.md) · [Glossary](../overview/glossary.md)
