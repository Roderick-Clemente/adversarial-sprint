# Configuration

Everything on this page was measured against `droid` 0.186.0 on macOS (darwin 24.6.0) during Phase 0. It is a record of observed behaviour, not a restatement of vendor documentation — and in the one place the two disagree, the observation wins and the disagreement is called out.

## Hook registration

This is the headline configuration result of Phase 0, from [Probe 4](../probes/probe-4-hook-blocking.md). The same hook declaration, the same `matcher: "*"` canary, and the same one-line prompt were placed at four locations:

| Location | Scope | Canary invocations | Reads? |
|---|---|---:|---|
| `.factory/hooks.json` | project — the documented primary | 0 | no |
| `~/.factory/hooks.json` | user | 0 | no |
| `.factory/hooks/hooks.json` | project, documented legacy | 0 | no |
| **`.factory/settings.json`, `hooks` key** | project | **1** | **yes** |
| **`<plugin>/hooks/hooks.json`** | plugin | **1** | **yes** ([Probe 6](../probes/probe-6-plugin-boundary.md)) |

The documentation describes the `settings.json` key as a fallback for when `hooks.json` is absent. Observed behaviour inverts that: the fallback is the only standalone channel that works, and the documented primary is silent.

The last row is the awkward one. A file literally named `hooks.json` is ignored at project scope and honoured inside a plugin, loaded by a different path. A developer who prototypes a guard in `.factory/hooks.json`, sees nothing fire, and concludes hooks are broken has reproduced this repository's own first Probe 4 result. Both channels have to be documented together.

A misregistered hook produces no warning, no error, and `exit 0`. The run simply proceeds unguarded — the silent-green failure shape that recurs throughout Phase 0.

### The shape that works

`.factory/settings.json` — from `phase-0/evidence/probe-4/reverify/rig/settings-hooks-WORKING.json`:

```json
{ "hooks": { "PreToolUse": [
  { "matcher": "Edit|Create|ApplyPatch|Execute",
    "hooks": [ { "type": "command", "command": "python3 /tmp/probe-4/hook-protect2.py", "timeout": 10 } ] } ] } }
```

### The shape that does not

`.factory/hooks.json` — from `phase-0/evidence/probe-4/reverify/rig/hooks-NOT-READ.json`. Note that it is valid JSON, uses absolute script paths, and uses the documented `PreToolUse` event. Nothing about the file is wrong; the location is.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "*",
        "hooks": [ { "type": "command", "command": "python3 /tmp/probe-4/hook-canary.py", "timeout": 10 } ] },
      { "matcher": "Edit|Create|ApplyPatch",
        "hooks": [ { "type": "command", "command": "python3 /tmp/probe-4/hook-protect.py", "timeout": 10 } ] }
    ]
  }
}
```

Two details carry over to anything you write:

- The outer `hooks` wrapper is present in both files. Inside a plugin's `hooks/hooks.json` it is **absent** — the event name is the top-level key (see [Plugin layout](#plugin-and-marketplace-layout) below).
- A `matcher: "*"` canary alongside the real guard is what distinguishes "the matcher did not match" from "no hook was loaded." Without it, those two failures look identical, which is exactly how Probe 4 first reached the wrong verdict.

## Hook payload contract

The payload arrives as a single JSON object on the hook process's **stdin**. Keys read by the Phase 0 rigs (`phase-0/evidence/probe-4/reverify/rig/hook-canary.py`, `rig/hook-protect2.py`, `phase-0/evidence/probe-8/rig/hook-observe.py`):

| Key | Notes |
|---|---|
| `hook_event_name` | e.g. `PreToolUse` |
| `tool_name` | e.g. `Edit`, `Execute`, `LS` |
| `tool_input` | object; **keys differ per tool** |
| `cwd` | the resolved working directory, e.g. `/private/tmp/probe-4/repo` |
| `permission_mode` | the autonomy tier as a string, e.g. `auto-low` |
| `session_id` | UUID matching the `session_id` in the `-o json` envelope |
| `transcript_path` | path to the session JSONL, e.g. `~/.factory/sessions/-private-tmp-probe-4-repo/b971b2c2-….jsonl` |

`transcript_path` is the key that makes [the reference guard](../findings/reference-guard.md) possible: a hook can read what actually happened in the session rather than trusting configuration or the prompt.

### `tool_input` keys per tool

Observed, not documented:

| Tool | `tool_input` keys |
|---|---|
| `Edit` | `file_path` (plus the edit content) |
| `Execute` | `command`, `riskLevel`, `riskLevelReason`, `summary` |

This asymmetry is the Probe 4 A4 bypass in one line. A guard that reads `tool_input.file_path` is blind to every shell write, because `Execute` never supplies a path. The fixed guard checks `file_path`, `path`, `target_file`, **and** the `command` string, and denies anything it cannot parse:

```python
try: p = json.loads(raw or "{}")
except Exception as e:
    print(f"SPEC_OR_TEST_BLOCKED: unparseable hook input, failing closed: {e}", file=sys.stderr)
    sys.exit(2)
```

`riskLevel` and `riskLevelReason` are supplied **by the model** about its own command. They are useful observability and a poor security input; see [Probe 8](../probes/probe-8-self-declared-risk.md).

## Hook output channels

Both denial channels were verified, and both keep the run alive:

| Channel | Mechanism | Result |
|---|---|---|
| exit 2 + stderr | write the contract to stderr, `sys.exit(2)` | edit denied, **stderr text delivered to the agent**, run continues at exit 0 |
| JSON at exit 0 | emit an object with `hookSpecificOutput.permissionDecision: "deny"` | edit denied, reason delivered, run continues at exit 0 |
| exit 0, no output | — | allow |

The exit-2 channel is what the Phase 0 rigs use, because it is the smaller contract and it was the first one verified. Either is acceptable; what matters is that a hook never exits 0 silently on a payload it did not understand.

Contrast with two mechanisms that are **not** substitutes:

- `--disabled-tools Edit` did not protect a file. The agent used the shell and reported success at exit 0.
- The autonomy tier denies and then **terminates** the run: `num_turns: 0`, exit 1, `is_error: true`. Deterministic, but nothing the run can act on.

## Config file locations

| Path | Scope | Contents observed |
|---|---|---|
| `.factory/settings.json` | project | `hooks`, `enabledPlugins` |
| `~/.factory/settings.json` | user | includes `trustedFolders` |
| `~/.factory/sessions/<cwd-slug>/<session-id>.jsonl` | user | session transcripts |
| `~/.factory/droids/` | user | machine-personal custom Droids |
| `~/.factory/plugins/cache/` | user | installed plugin cache |

`.factory/` is **gitignored in this repository**, treated as local tool state. That is why probe evidence is written to `phase-0/evidence/` rather than the PRD §9 default path, and why hook rigs log to `/tmp/…/hooklog/` — a location the orchestrator owns outright, deliberately outside `.factory/`. See [Architecture](../overview/architecture.md).

Installing a plugin at project scope wrote exactly two things: `enabledPlugins` into the project's `.factory/settings.json`, and a cache copy under `~/.factory/plugins/cache/`. Nothing else in the repository was touched.

Session transcripts living under `~/.factory/` and outside the repository is also a confidentiality issue — any later agent with `Grep` can read a prior agent's transcript. See [Security](../security.md).

## Custom Droid frontmatter

A Droid definition is a Markdown file with YAML frontmatter. Real example, `phase-0/evidence/probe-6/plugin/droids/probe-validator.md`:

```markdown
---
name: probe-validator
description: Phase 0 probe droid. Reports whether it was reachable as a subagent and what tools it has.
model: inherit
tools: ["Read", "Grep", "Glob"]
---
You are a probe validator shipped inside a plugin. When invoked, state
"PLUGIN_DROID_REACHED" and list the tool names you actually have available.
Do not attempt to write files.
```

| Field | Notes |
|---|---|
| `name` | the `subagent_type` used to invoke it via `Task` |
| `description` | shown in the subagent registry |
| `model` | a model ID, or `inherit` |
| `tools` | allowlist, enforced by **omission from the tool schema** |

The `tools` allowlist is real enforcement, not a prompt instruction: with `["Read", "Grep", "Glob"]` the droid had no write-capable tool and could not create a file even when asked to.

**It is a floor, not an exact manifest.** The droid above reported five tools, not three — the platform added `TodoWrite` and `Skill`. Neither grants filesystem writes, so read-only isolation held, but do not treat `tools:` as the complete list. Assert on what the subagent reports.

## Plugin and marketplace layout

The probe plugin, `phase-0/evidence/probe-6/plugin/`:

```text
plugin/
├── .factory-plugin/
│   └── plugin.json
├── commands/
│   └── probe-hello.md
├── droids/
│   └── probe-validator.md
├── hooks/
│   ├── canary.py
│   └── hooks.json
├── skills/
│   └── probe-marker/
│       └── SKILL.md
└── README.md
```

`.factory-plugin/plugin.json`:

```json
{
  "name": "probe-guard",
  "description": "Phase 0 probe: minimal plugin carrying a droid, a skill, a command and a hook.",
  "version": "0.1.0",
  "author": { "name": "adversarial-sprint phase 0" },
  "license": "MIT",
  "keywords": ["probe"]
}
```

`hooks/hooks.json` — note the **event name is the top-level key**, with no outer `hooks` wrapper, unlike `settings.json`:

```json
{
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [ { "type": "command", "command": "python3 ${DROID_PLUGIN_ROOT}/hooks/canary.py", "timeout": 10 } ]
    }
  ]
}
```

A marketplace is a directory with `.factory-plugin/marketplace.json` and the plugin directories beside it. From `phase-0/evidence/probe-6/plugin-marketplace/.factory-plugin/marketplace.json`:

```json
{
  "name": "probe-mkt",
  "description": "Local marketplace for Phase 0 probe 6",
  "owner": { "name": "adversarial-sprint phase 0" },
  "plugins": [
    { "name": "probe-guard", "description": "Phase 0 probe plugin", "source": "./probe-guard" }
  ]
}
```

Commands and skills follow the same frontmatter pattern as Droids — `commands/probe-hello.md` carries only `description`, and `skills/probe-marker/SKILL.md` carries `name` and `description`. Of the five component types tried, hooks, Droids and skills all activated on install; slash commands are interactive-only so `droid exec` gave no surface to test them, and MCP servers were out of scope.

### Two papercuts to plan around

**A marketplace registers under its directory basename, not the `name` in `marketplace.json`.** Adding `/tmp/probe-6/mkt` registered it as `mkt`; `droid plugin install probe-guard@probe-mkt` failed with `Marketplace "probe-mkt" not found`, and `probe-guard@mkt` succeeded. The `marketplace list` output shows both values side by side, which is the only hint you get:

```text
mkt  (1 plugin)  local:/tmp/probe-6/mkt  "probe-mkt"
```

**`${DROID_PLUGIN_ROOT}` expands in the `command` string but the environment variable is poisoned.** The hook ran, so substitution works. The script then read its own environment and found the literal sentinel:

```text
DROID_PLUGIN_ROOT=/PLUGIN_ROOT_NOT_EXPANDED_ERROR
```

So pass the plugin root as an argument in the `command` string. Never read it from the environment inside the script — a path that does not exist is the good outcome there; silent mis-resolution is the other one.

## Autonomy tiers

`droid exec --auto low|medium|high`, with no flag meaning read-only planning mode, and `--skip-permissions-unsafe` as the isolated-environment escape hatch. The tier surfaces to hooks as `permission_mode` (e.g. `auto-low`).

| Tier | Permits | Measured |
|---|---|---|
| default (no flag) | read-only planning and analysis | — |
| `low` | `Execute` calls the model labels `riskLevel: low`; denies `medium` and `high` | [Probe 8](../probes/probe-8-self-declared-risk.md) |
| `medium` | intended for development tasks — install, test, fix | not exercised |
| `high` | production operations — commit, push, deploy | Probe 8 control |

**`--auto low` is read-only in practice.** The sharpest datum: appending one line to a file that did not yet exist was self-labelled `medium` and refused. Not "low-risk writes allowed" — no shell writes at all. Budget `low` for validators and reviewers, never for an executor expected to write.

Denial at a tier is terminal, not actionable:

```text
Exec ended early: insufficient permission to proceed. Re-run with --auto medium
or --auto high. For destructive commands, use --skip-permissions-unsafe.
```

The label-to-permission mapping is deterministic and independent of the model. The **label itself** is not: it comes from `tool_input.riskLevel`, which the model writes about its own command. So the tier is a strong operational default and a weak boundary for a role you are treating as untrusted. That distinction is drawn out in [Security](../security.md).

## Related

- [Data models](./data-models.md) — the JSON shapes these settings produce and consume
- [Dependencies](./dependencies.md) — why every statement here is scoped to 0.186.0
- [Probe 4](../probes/probe-4-hook-blocking.md) · [Probe 6](../probes/probe-6-plugin-boundary.md) · [Probe 8](../probes/probe-8-self-declared-risk.md)
- [The reference guard](../findings/reference-guard.md) — the one hook these rules describe
- [Debugging](../how-to-contribute/debugging.md) · [Glossary](../overview/glossary.md)
