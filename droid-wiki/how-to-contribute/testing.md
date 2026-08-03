# Testing

There is no unit test suite, no test runner, and no CI. **The tests are the probes.** A probe is a controlled experiment against the `droid` CLI whose result is committed as a record; re-running it is how you check whether a recorded verdict still holds against a new CLI version.

## Re-running a probe

Four probes ship an executable reproduction script:

```bash
bash phase-0/evidence/probe-4/reverify/run.sh   # hook blocking and registration matrix
bash phase-0/evidence/probe-2/run.sh            # model pinning and the family gate
bash phase-0/evidence/probe-6/run.sh            # plugin distribution boundary
bash phase-0/evidence/probe-8/run.sh            # autonomy tier vs self-declared risk
```

Each takes an optional working directory: `bash phase-0/evidence/probe-2/run.sh /tmp/my-run`.

Probes 1, 3, 5 and 7 have no `run.sh`. Probe 1 is BLOCKED and Probe 3 lives on its own branch — see [Probes](../probes/index.md).

Every script prints its `droid --version` first and an expected-shape summary at the end, so a re-run tells you at a glance whether anything moved.

## Read this before you run anything

**These cost real model credits.** The scripts make live `droid exec` calls at `--auto high`:

| Script | `droid exec` runs |
|---|---|
| `phase-0/evidence/probe-4/reverify/run.sh` | 11 |
| `phase-0/evidence/probe-2/run.sh` | 9 |
| `phase-0/evidence/probe-8/run.sh` | 7 |
| `phase-0/evidence/probe-6/run.sh` | 4 |

**Blast radius is `/tmp/probe-<n>/`.** Every rig builds its fixtures — a throwaway git repository, a hook log directory, a `raw/` capture directory — under `/tmp/probe-<n>/`, and `rm -rf`s it at the start of each run. Nothing is written inside the repository. Rigs that hard-code the default path into hook scripts rewrite it with `sed` when you pass a different workdir, so an alternate workdir stays self-consistent.

**Two probes touch configuration outside `/tmp`:**

- `phase-0/evidence/probe-6/run.sh` mutates **user-level** config. Installing a plugin writes `enabledPlugins` and `extraKnownMarketplaces` into `~/.factory/settings.json` and a cache copy under `~/.factory/plugins/cache/`. The script copies `~/.factory/settings.json` to `$WORK/USER-SETTINGS-BACKUP.json` first, diffs against the backup before and after, and restores it byte-identical at the end — because uninstall does **not** fully clean up after itself. Read the cleanup section before running it on a machine you care about.
- `phase-0/evidence/probe-4/reverify/run.sh` creates `~/.factory/hooks.json` for one negative control and removes it afterward, backing up any pre-existing file first.

## What a `run.sh` must do to count as evidence

The standard is in `phase-0/evidence/README.md`: *if a probe cannot be re-run from what is in its directory, it is a claim rather than evidence.* Concretely, a script must:

1. **Print the CLI version under test**, first line: `droid --version | sed 's/^/droid version: /'`. A verdict recorded against no version cannot be rechecked later.
2. **Reproduce every measurement in the record** — not the interesting one, all of them, including the negative controls.
3. **Write raw captures** to a `raw/` directory, one file per run, so a claim can be traced to the bytes that support it. Secret-filter and replace `/Users/<user>` with `~` before committing them.
4. **Print an expected-shape summary** at the end: the per-test outcome, the hook invocation counts, the resolved model IDs. A reader who has never seen the record should be able to compare the summary to the README and see whether the verdict held.
5. **Be idempotent.** Delete and recreate the workdir; do not depend on leftovers from a previous run.
6. **Restore anything it changed outside the workdir**, and verify the restore rather than assume it.

## What to assert on

Never the process exit code. The platform's default failure mode is reporting exit 0 for work that did not happen — four independent instances across Probes 1, 2 and 4. See [Silent green](../findings/silent-green.md).

Assert on, in order of trustworthiness:

| Signal | Why |
|---|---|
| **The hook's own log** | The hook is your instrument. If it wrote a `deny` line, a deny happened. Probe rigs append JSONL from every hook invocation. |
| **The observed effect** | Did the file actually change? `shasum -a 256` before and after. Probe 4 pins the locked test's hash in `phase-0/evidence/probe-4/reverify/rig/locked-test.sha256`. |
| **Per-tool `is_error`** | Inside the session transcript, each `tool_result` block carries `is_error`. A run can exit 0 with every tool call denied. |
| The agent's summary text | Weakest. Whether a block message reaches the final `result` is up to the model — Probe 4's agent quoted `SPEC_OR_TEST_BLOCKED` verbatim, Probe 2's never mentioned `MODEL_FAMILY_VIOLATION` at all. |
| The process exit code | Not evidence of anything. |

The demonstration is Probe 2's test T5: `num_turns=3`, `is_error=False`, exit 0, a correct-looking answer — with **every** tool call denied by the family gate. See [Probe 2](../probes/probe-2-fallback-safety.md).

## One variable per pair

A single observation is a story. Every load-bearing claim comes from an A/B pair differing in **exactly one variable**, and a new test should be designed as a pair from the start:

- Hooks load from `settings.json` and not `hooks.json` — same declaration, same canary, four config locations.
- The family gate follows the resolved model — same gate, `gpt-5.4-mini` versus `claude-opus-5`.
- A path guard fails open on shell writes — same prompt, matcher with and without `Execute`.

Related: if the agent could have complied out of good manners, you measured manners, not the control. Force the bypass or label the result behavioral. Details in [Patterns and conventions](./patterns-and-conventions.md#force-the-bypass-or-you-are-measuring-manners).

## Always register a canary

Every hook test needs a second hook alongside the one under test: `matcher: "*"`, logs its payload, **never blocks**.

```json
{ "hooks": { "PreToolUse": [
  { "matcher": "*",
    "hooks": [ { "type": "command", "command": "python3 /tmp/probe-4/hook-canary.py", "timeout": 10 } ] },
  { "matcher": "Edit|Create|ApplyPatch|Execute",
    "hooks": [ { "type": "command", "command": "python3 /tmp/probe-4/hook-protect2.py", "timeout": 10 } ] } ] } }
```

The reference implementation is `phase-0/evidence/probe-4/reverify/rig/hook-canary.py`. It logs `hook_event_name`, `tool_name`, `permission_mode`, `transcript_path`, and `sorted(tool_input.keys())` — the last of which is what tells you which payload shape your real guard has to handle.

Without a canary, "the hook logged nothing" is ambiguous between **the matcher did not match** and **no hook was loaded at all**. That ambiguity produced a wrong verdict once: the original Probe 4 rig registered its hook at `.factory/hooks.json`, saw zero invocations, and concluded that hooks do not fire. The re-verification added a canary, moved the identical declaration to the `hooks` key in `.factory/settings.json`, and it fired immediately. The observation was right; the conclusion was wrong, because the rig could not tell the two cases apart. See [Probe 4](../probes/probe-4-hook-blocking.md).

Anything that ships a hook should carry the same assertion as an install check: register a canary, make one trivial tool call, assert the canary logged, fail if it did not. A misregistered hook fails silently at exit 0, and configuration being present is not evidence that enforcement is live.
