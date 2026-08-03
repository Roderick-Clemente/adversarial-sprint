# Tooling

Deliberately minimal. There is no package manager, no lockfile, no build tool, and no third-party library anywhere in the repository — a probe that needs an install step is a probe that will not reproduce in a year. Everything below is either the CLI under test or a POSIX-standard tool.

| Tool | Used for |
|---|---|
| `droid` | The subject of every probe. Pinned at **0.186.0** in the records. |
| `python3` | Hook scripts and JSON parsing. Standard library only. |
| bash | `run.sh` reproduction scripts. |
| `git` | Branching, handoff, and throwaway fixture repositories inside rigs. |
| `jq`, `python3 -c` | Reading result envelopes and session transcripts. |
| `shasum`, `diff`, `sed`, `grep` | Verifying effects and scrubbing captures. |

## The `droid` CLI

Pin the version in anything you record: `droid --version`. A verdict recorded against no version cannot be rechecked later.

### `droid exec`

Non-interactive execution — the workhorse of every probe.

```bash
droid exec -o json --auto high --cwd "$REPO" --model claude-opus-5 -r high "prompt"
```

| Flag | Notes from the probes |
|---|---|
| `-o json` / `--output-format json` | Result envelope: `type, subtype, is_error, duration_ms, num_turns, session_id, result, usage`. `usage` carries `factory_credits`, so cost is attributable per run. **No model field.** |
| `--auto low\|medium\|high` | Autonomy tier. At `--auto low`, `Execute` is effectively read-only. Denial is `num_turns: 0`, `exit 1`, `is_error: true`. |
| `--model <id>` | Explicit IDs resolve exactly and invalid IDs fail closed, so pinning is trustworthy. `--model auto` delegates to the router and can cross model families. `custom:<name>` selects a BYOK model; untested here. |
| `-r` / `--reasoning-effort` | An unsupported value **silently resolves to `off`** rather than erroring. Read the effort back from the transcript. |
| `--cwd <dir>` | Sets the working directory, which also determines the session transcript's directory slug. |
| `--list-tools` | Exact tool names, needed to write a correct hook matcher. Combine with `-o json`. |
| `--disabled-tools` / `--enabled-tools` / `--additional-tools` | Tool schema control. Note `--disabled-tools Edit` does **not** protect a file — the agent uses the shell instead. |
| `--mission` | A no-op at 0.186.0; see [Probe 1](../probes/index.md). The per-role model flags are `--mission`-only, which is why the design uses one `droid exec` per role. |

`droid exec --help` also lists every available model with its supported reasoning-effort values. Probe 2 captured that output verbatim in `phase-0/evidence/probe-2/raw/model-ids-0.186.0.txt`, which is the reference for what a model ID resolved to at the recorded version.

### `droid search`

Semantic code search, available as a tool to agents. It matters here as a **leak path**: an agent with search or grep can read another agent's session transcript out of `~/.factory/sessions/`, so an isolation guard has to inspect command strings to cover it. See [Security](../security.md).

### `droid plugin`

Used by Probe 6 to test whether the design ships as one installable thing.

```bash
droid plugin marketplace add /tmp/probe-6/mkt
droid plugin marketplace list
droid plugin install probe-guard@mkt --scope project
droid plugin list
droid plugin uninstall probe-guard@mkt --scope project
droid plugin marketplace remove mkt
```

Three papercuts worth knowing before you use these:

- A local marketplace is keyed by its **directory basename**, not the `name` field in `marketplace.json`. Installing with the manifest name fails with a misleading `Run /marketplace add first`.
- `${DROID_PLUGIN_ROOT}` expands inside a hook's `command` string, but the environment variable handed to the script is the literal sentinel `/PLUGIN_ROOT_NOT_EXPANDED_ERROR`. Pass the plugin root as an argument; never read it from the environment.
- Uninstall stops the hook but leaves `enabledPlugins: {}`, `extraKnownMarketplaces: {}`, and a stale plugin cache. Back up `~/.factory/settings.json` before plugin work and restore it explicitly.

Details in [Probe 6](../probes/probe-6-plugin-boundary.md).

## `python3` for hooks

Hooks are single-file `python3` scripts with no imports beyond the standard library — `json`, `sys`, `os`, `pathlib`, `hashlib`, `datetime`. They read the hook payload as JSON on stdin, append a JSONL log line, and communicate their verdict through the exit code:

| Exit | Meaning |
|---|---|
| `0` | Allow |
| `2` | Deny, with the message on **stderr**, which the agent receives as a tool result while the run continues |

Two reference implementations:

- `phase-0/evidence/probe-4/reverify/rig/hook-canary.py` — logs every invocation, never blocks. Copy this into any hook experiment.
- `phase-0/evidence/probe-4/reverify/rig/hook-protect2.py` — the fail-closed guard that inspects both `file_path` and `command`, and denies on anything it cannot interpret.

`python3` is also the JSON reader of choice where `jq` would need a heredoc anyway; Probe 4's `run.sh` embeds `python3 - "$@" <<'PY'` blocks to print run summaries.

## bash for `run.sh`

Reproduction scripts are bash with `set -uo pipefail`, one optional positional argument for the working directory, and no dependencies. What one has to do to count as evidence is in [Testing](./testing.md#what-a-runsh-must-do-to-count-as-evidence).

## `git`

Two distinct roles. As the handoff mechanism between agents, covered in [Development workflow](./development-workflow.md). And inside the rigs: each probe `git init`s a throwaway repository under `/tmp/probe-<n>/repo` with an explicit identity so it cannot pick up yours:

```bash
git -c user.email=probe@local -c user.name=probe commit -qm "init: locked test fixture"
```

## Reading captures

```bash
# result envelope
python3 -c "import json;o=json.load(open('run.json'));print(o['num_turns'],o['is_error'],o['session_id'])"

# resolved model
grep -o '"modelId":"[^"]*"' ~/.factory/sessions/*/<session-id>.jsonl | sort -u

# hook log
python3 -c "
import json
for l in open('/tmp/probe-4/hooklog/protect2.jsonl'):
    r=json.loads(l); print(r['tool_name'], r['verdict'], r['why'])"
```

More of these, in context, in [Debugging](./debugging.md).

## Where Factory configuration lives

```text
<repo>/.factory/            project scope — gitignored here
  settings.json               the hooks key is the ONLY hook location the CLI reads
                              (.factory/hooks.json is NOT read; a plugin's
                               hooks/hooks.json is)

~/.factory/                 user scope
  settings.json               user settings; plugin install/uninstall mutates this
  sessions/<cwd-slug>/        session transcripts, <session-id>.jsonl — where the
                              resolved model and per-tool is_error actually live
  droids/                     custom Droid definitions
  plugins/cache/              installed plugin copies; not fully cleaned on uninstall
  logs/, cache/, temp/        local tool state
```

`.factory/` is gitignored in this repository as local tool state, which is why probe evidence is committed to `phase-0/evidence/` instead of the `.factory/adversarial-sprints/<run-id>/` path the spec nominates. `PRD.md` §9 permits another configured artifact path, and the reasoning is recorded in `phase-0/evidence/README.md`. A consequence to keep in mind: **a rig that writes into `.factory/` writes something git will never show you.**

Full detail in [Configuration](../reference/configuration.md) and [Dependencies](../reference/dependencies.md).
