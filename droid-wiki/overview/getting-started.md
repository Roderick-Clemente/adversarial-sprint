# Getting started

There is nothing to build or install. This repository holds a specification and executed probe evidence. "Running" it means **re-running a probe and checking whether its recorded verdict still holds**.

## Prerequisites

| Requirement | Notes |
|---|---|
| `droid` CLI | The probes were recorded against **0.186.0**. Check with `droid --version`. A different version invalidates the recorded verdicts until you re-run. |
| Python 3 | Hook scripts are plain `python3`, no packages required |
| `git` | Probe rigs create throwaway repositories |
| A POSIX shell | `run.sh` scripts are bash |
| macOS or Linux | Probes were recorded on macOS (darwin 24.6.0); Probe 4's superseded record was taken on Linux |

No package manager, lockfile, or dependency install step exists. See [Dependencies](../reference/dependencies.md).

## Reading the repository

Start here, in this order:

```bash
cat README.md            # the pitch and the four core properties
cat PRD.md               # full spec — invariants in §4, workflow in §5
cat phase-0/README.md    # the eight probes and their verdicts
cat phase-0/GO-NO-GO.md  # the Phase 0 decision
```

## Re-running a probe

Every probe directory carries a `run.sh` that reproduces every measurement in its record. This is the repository's equivalent of a test suite.

```bash
bash phase-0/evidence/probe-4/reverify/run.sh   # hook blocking: 11 droid exec runs
bash phase-0/evidence/probe-8/run.sh            # self-declared risk: 7 runs
bash phase-0/evidence/probe-2/run.sh            # fallback safety: 9 runs
bash phase-0/evidence/probe-6/run.sh            # plugin distribution: 4 runs
```

Each script prints its `droid --version` first, then an expected-shape summary at the end so you can tell at a glance whether the verdict still holds.

### Before you run anything

**These scripts cost real model credits.** Probe 4's rig makes 11 `droid exec` calls at `--auto high`. Probe 2 makes 9. Budget accordingly.

**They write outside the repository.** All rigs build throwaway fixtures under `/tmp/probe-<n>/`, which they delete and recreate on each run.

**Probe 6 mutates user-level configuration.** It registers a plugin marketplace and installs a plugin, which writes to `~/.factory/settings.json` and `~/.factory/plugins/cache/`. The script backs the settings file up first and restores it byte-identical at the end, but read the cleanup section before running it on a machine you care about. Uninstall does not fully clean up after itself — see [Probe 6](../probes/probe-6-plugin-boundary.md).

### Finding the evidence for a probe

Probe evidence is spread across branches. To see Probe 3, which is not on the main chain:

```bash
git show factory/probe-3-context-isolation:phase-0/evidence/probe-3/README.md
git checkout factory/probe-3-context-isolation
```

The branch layout is explained in [Architecture](./architecture.md#content-is-distributed-across-branches).

## Reading a probe record

Each record follows the same shape, defined in `phase-0/evidence/README.md`:

| Element | Why it is required |
|---|---|
| Verdict and date | The claim being made |
| `droid --version` | A "no" recorded against no version cannot be rechecked later |
| Resolved model IDs | Where the probe touches model selection, the *resolved* ID matters, not the requested one |
| Exact commands and exit codes | So the reasoning can be contested |
| `raw/` | Captured stdout, hook logs, secret-filtered |
| `rig/` | The scripts and configs actually under test |
| `run.sh` | If a probe cannot be re-run from its own directory, it is a claim rather than evidence |

## Interpreting results — read this before trusting a green run

The most important operational lesson from Phase 0 is that **an exit code of 0 means very little on this platform**. Four separate probes produced runs that looked successful and were not. See [Silent green](../findings/silent-green.md) and [Debugging](../how-to-contribute/debugging.md).

When re-running a probe, assert on:

- the **hook's own log**, not the agent's summary
- **per-tool `is_error`** inside the session transcript
- the **observed effect** — did the file actually change? compare hashes
- **never** the process exit code alone

A concrete example: in Probe 2's test T5 the family gate denied every single tool call, and the run still exited 0, `is_error: false`, with a correct-looking answer that the model produced from its startup context.

## Verifying a resolved model

The `droid exec -o json` result envelope does **not** contain the model that ran. To find it, read the session transcript:

```bash
SESSION=$(python3 -c "import json;print(json.load(open('run.json'))['session_id'])")
grep -o '"modelId":"[^"]*"' ~/.factory/sessions/*/$SESSION.jsonl | sort -u
```

This method came out of Probe 3's addendum and is used by every probe from 3 onward. Details in [Probe 2](../probes/probe-2-fallback-safety.md).

## Contributing a change

Read `AGENTS.md` first — it binds humans and agents equally, and it has a hard rule about what must never be committed here. Then see [How to contribute](../how-to-contribute/index.md).
