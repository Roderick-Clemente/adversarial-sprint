# Dependencies

Short page, because there are almost none. This is a specification and evidence repository; the only executable artifacts are probe rigs written against the Python standard library.

## Runtime

| Dependency | Version | Why |
|---|---|---|
| `droid` CLI | **0.186.0** | the subject under test; every Phase 0 verdict is scoped to it |
| `python3` | any 3.x with `pathlib` | hook rigs; **standard library only** |
| `bash` | any | each `run.sh` is `#!/usr/bin/env bash` |
| `git` | any | branch-per-probe workflow, and `git init` for scratch repos inside `run.sh` |
| `shasum` | system | hash-locking test files in the Probe 4 rig |
| `jq` | optional | convenience for reading `raw/*.json` captures by hand; no script requires it |

Every import across every rig in `phase-0/evidence/`: `hashlib`, `json`, `os`, `re`, `sys`, `datetime`, `pathlib`. Nothing to install.

JSON validation inside the probes uses `python3 -m json.tool` rather than `jq`, so a machine with the CLI and a Python 3 can reproduce Phase 0 with nothing added.

## No package manifest

Verified absent from the whole tree: `package.json`, `package-lock.json`, `yarn.lock`, `requirements.txt`, `pyproject.toml`, `setup.py`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, and any `*.lock`.

No lockfile, no vendored code, no `node_modules`, no virtualenv. There is nothing to audit for supply chain here, which is worth stating plainly rather than leaving a reader to infer it from an empty search.

## Why the CLI version is pinned

Every probe record carries `CLI under test: droid 0.186.0` and `Host: macOS (darwin 24.6.0)` in its header, and the Phase 0 go/no-go is explicitly version-scoped. This is not ceremony. Several of the findings are **undocumented or contra-documented behaviour**, which is exactly the class of behaviour that changes without a release note:

- `.factory/hooks.json` is not read at project scope, while the `hooks` key in `.factory/settings.json` is. The documentation describes the working path as a fallback. Nobody outside the CLI knows *why*, so nobody can predict which side an upgrade lands on.
- `DROID_PLUGIN_ROOT` arrives as the literal `/PLUGIN_ROOT_NOT_EXPANDED_ERROR`. That is a bug, and a fixed bug changes behaviour too.
- A local marketplace registers under its directory basename rather than its declared `name`.
- The `-o json` envelope has no model field, so model attribution reads an undocumented session-store field.
- `droid exec --mission` performed no work, which is the finding the whole command-orchestrated design is a response to.

### What invalidates the verdict

Any of these means Phase 0 has to be re-measured rather than cited:

| Change | Effect |
|---|---|
| A different `droid` version | every table on [Configuration](./configuration.md) is unverified again |
| A different host OS | the superseded Probe 4 record ran on Linux and reached the opposite conclusion; platform is a live variable |
| Interactive mode instead of `droid exec` | all Phase 0 runs used `exec`; hook loading in an interactive session is untested |
| A change to hook loading | the enforcement primitive the design rests on |
| A change to model IDs or the default model | the family gate reads `modelId` and fails closed on an unknown value |

The practical consequence for the product: the plugin's install check must **assert liveness at install time** — register a canary hook and confirm it logged — rather than trusting a config file it wrote. Configuration being present is not evidence of enforcement. See [The reference guard](../findings/reference-guard.md).

## Model IDs at 0.186.0

Captured in `phase-0/evidence/probe-2/raw/model-ids-0.186.0.txt`. `claude-opus-5` is the default.

| ID | Name |
|---|---|
| `auto` | Auto Model |
| `claude-fable-5` | Fable 5 |
| `claude-opus-5` | Opus 5 — **default** |
| `claude-opus-5-fast` | Opus 5 Fast Mode |
| `claude-opus-4-8` | Opus 4.8 |
| `claude-opus-4-8-fast` | Opus 4.8 Fast Mode |
| `claude-opus-4-7` | Opus 4.7 |
| `claude-opus-4-6` | Opus 4.6 |
| `claude-opus-4-5-20251101` | Opus 4.5 |
| `claude-sonnet-5` | Sonnet 5 |
| `claude-sonnet-4-6` | Sonnet 4.6 |
| `claude-sonnet-4-5-20250929` | Sonnet 4.5 |
| `claude-haiku-4-5-20251001` | Haiku 4.5 |
| `gpt-5.6-sol` | GPT-5.6 Sol |
| `gpt-5.6-terra` | GPT-5.6 Terra |
| `gpt-5.6-luna` | GPT-5.6 Luna |
| `gpt-5.5` | GPT-5.5 |
| `gpt-5.5-fast` | GPT-5.5 Fast Mode |
| `gpt-5.5-pro` | GPT-5.5 Pro |
| `gpt-5.4` | GPT-5.4 |
| `gpt-5.4-fast` | GPT-5.4 Fast Mode |
| `gpt-5.4-mini` | GPT-5.4 Mini |
| `gpt-5.3-codex` | GPT-5.3-Codex |
| `gpt-5.3-codex-fast` | GPT-5.3-Codex Fast Mode |
| `gpt-5.2` | GPT-5.2 |
| `gemini-3.1-pro-preview` | Gemini 3.1 Pro |
| `gemini-3.5-flash` | Gemini 3.5 Flash |
| `gemini-3-flash-preview` | Gemini 3 Flash |
| `glm-5.2` | GLM-5.2 (Droid Core) |
| `glm-5.2-fast` | GLM-5.2 Fast (Droid Core) |
| `kimi-k3` | Kimi K3 (Droid Core) |
| `kimi-k2.7-code` | Kimi K2.7 Code (Droid Core) |
| `kimi-k2.6` | Kimi K2.6 (Droid Core) |
| `nemotron-3-ultra` | Nemotron 3 Ultra (Droid Core) |
| `deepseek-v4-pro` | DeepSeek V4 Pro (Droid Core) |
| `minimax-m3` | MiniMax M3 (Droid Core) |
| `minimax-m2.7` | MiniMax M2.7 (Droid Core) |
| `minimax-m2.5` | MiniMax M2.5 (Droid Core) |
| `grok-4.5` | Grok 4.5 |

The same capture records per-model reasoning support and defaults, which matters because reasoning effort is not uniform: `claude-opus-5` defaults to `high`, `gpt-5.4-mini` to `high`, `gpt-5.2` to `low`, `claude-opus-4-5-20251101` and `claude-haiku-4-5-20251001` to `off`. A role definition that pins a model without pinning effort inherits whatever that model's default happens to be.

This list is also the input to the family map. `PRD.md` §4 is explicit that family provenance is a curated file with an owner and a review date, not something the runtime can infer — several IDs above are hosted models whose upstream base family is not declared anywhere. An unmapped model resolves to `unknown`, and `unknown` stops the run rather than being optimistically admitted.

## Platform surfaces depended on

Each row is a Factory capability the design needs, with the probe that established what it actually does.

| Surface | Used for | Verified by |
|---|---|---|
| `droid exec` (`-o json`, `--model`, `--auto`, `-s`, `--fork`) | one invocation per role; the orchestration substrate | [Probe 2](../probes/probe-2-fallback-safety.md) |
| `PreToolUse` hooks | the enforcement primitive: locked tests, isolation, family gate | [Probe 4](../probes/probe-4-hook-blocking.md) |
| Custom Droids (`tools:` allowlist, `model:`) | read-only reviewer and validator roles | [Probe 3](../probes/probe-3-context-isolation.md), [Probe 6](../probes/probe-6-plugin-boundary.md) |
| Plugins and local marketplaces | shipping the guard, Droids and skills as one installable unit | [Probe 6](../probes/probe-6-plugin-boundary.md) |
| Session transcripts under `~/.factory/sessions/` | model attribution and after-the-fact evidence | [Probe 2](../probes/probe-2-fallback-safety.md), [Probe 3](../probes/probe-3-context-isolation.md) |
| `usage.factory_credits` | per-role cost attribution | [Probe 2](../probes/probe-2-fallback-safety.md) |
| Autonomy tiers (`--auto`) | operational default, **not** a boundary for an untrusted role | [Probe 8](../probes/probe-8-self-declared-risk.md) |

Missions are conspicuously absent. `droid exec --mission` is what Phase 0 expected to depend on and what it stopped depending on; see [Architecture](../overview/architecture.md).

`PostToolUse`, `Stop`, `SubagentStop`, MCP servers, and interactive slash commands are all unexercised. Nothing here depends on them yet, and `SubagentStop` is the one most likely to be needed next.

## Related

- [Configuration](./configuration.md) — the settings surface at this version
- [Data models](./data-models.md) — the shapes these surfaces emit
- [Probes](../probes/index.md) — the full evidence record
- [Debugging](../how-to-contribute/debugging.md) · [Security](../security.md)
