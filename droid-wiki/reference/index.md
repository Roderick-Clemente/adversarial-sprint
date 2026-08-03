# Reference

Lookup material rather than narrative: the configuration surface as measured, the structured shapes involved, and the very short dependency list. All of it is scoped to `droid` 0.186.0 on macOS (darwin 24.6.0), the version and host every Phase 0 probe ran against.

| Page | What it covers |
|---|---|
| [Configuration](./configuration.md) | Where hooks actually register, the `PreToolUse` payload and output channels, config file locations, custom Droid frontmatter, plugin and marketplace layout, autonomy tiers |
| [Data models](./data-models.md) | The `droid exec -o json` envelope, session transcript JSONL, hook log shapes, and the finding, RED, chunk and run-artifact schemas `PRD.md` specifies |
| [Dependencies](./dependencies.md) | The four runtime tools, the absence of any package manifest, why the CLI version is pinned, and the model IDs available at 0.186.0 |

Start with [Configuration](./configuration.md) if you are implementing anything — it carries the hook registration matrix, which is the single result most likely to cost you an afternoon.

For the reasoning behind these facts rather than the facts themselves, see [Probes](../probes/index.md) and [The reference guard](../findings/reference-guard.md). For terms used without definition here, see the [Glossary](../overview/glossary.md).
