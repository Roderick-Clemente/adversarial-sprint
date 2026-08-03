# Cross-version validation (0.180.0)

Every other page in this wiki is scoped to `droid` **0.186.0**. This one is the exception, and it exists to answer a question that scoping raises: how much of Phase 0 is a property of the platform, and how much is a property of *one patch release* of the platform.

The Phase 0 primitives were re-run on `droid` **0.180.0**, six patch releases older, on macOS Darwin 25.5.0. Evidence in `phase-0/evidence/canary-0.180.0/`.

**The verdict holds.** The two primitives the [GO/NO-GO](./index.md#the-verdict) rests on both work on the older CLI with no rescue modifications. But the run also found that one of Phase 0's headline defects is a **regression** rather than a standing bug, and that finding only exists because there were two versions to compare.

## What was checked, and what happened

This was a cross-validation, not a replication. The goal was not to re-derive Phase 0's findings but to confirm the load-bearing primitives still exist, and to surface any delta in either direction.

| # | Primitive | Expected at 0.186.0 | Observed at 0.180.0 |
|---|---|---|---|
| 1 | Plugin `hooks/hooks.json` fires on `PreToolUse` | Fires | **Holds** — one log entry on the run's `Execute` call |
| 2 | `settings.json` `hooks` key blocks a hash-locked test edit | Blocks, exit 2, `SPEC_OR_TEST_BLOCKED` | **Holds** — file hash unchanged, contract delivered, run continued |
| 3 | `.factory/hooks.json`, the documented project path | Silently never read | **Opposite — it fires** |
| 4 | `Execute` bypass against an `Edit\|Create\|ApplyPatch` matcher | Bypass succeeds | **Bypass succeeds**, under a cross-family executor |

Rows 1 and 2 are the result that matters most and the least interesting to read: the plugin hook loads and fires from inside the package, and the hash-locked test block holds. Neither needed a workaround to work on the older CLI. The enforcement layer the design depends on is not a 0.186-only artifact.

Row 4 reproduced the Probe 4 A4 bypass. Its interpretation belongs to [the reference guard](./reference-guard.md), which is where the structural fix is specified.

## The regression, and why direction matters

Row 3 is the substantive finding, and it is worth being careful about what it says.

Phase 0 recorded that `.factory/hooks.json`, the documented project-scope location, is **silently never read** at 0.186.0 — a hook registered there produces no error and no effect. It is [defect #2](../background/open-questions.md) and one of the four instances of [silent green](./silent-green.md).

At 0.180.0, that same path **works**. The hook fires.

```
0.180.0 (older)  →  .factory/hooks.json fires
0.186.0 (newer)  →  .factory/hooks.json silent
```

So this is not a standing bug that has always been there. It is a **regression introduced between the two versions**, and it moved in the direction of losing a working loader.

The methodological point is worth keeping, because it generalises. Read on its own, the 0.180.0 run says *Phase 0 got this wrong — the documented path works fine.* Read against the Phase 0 evidence, it says *Phase 0 was right, and the platform broke this recently.* Same observation, opposite conclusions, and the only thing separating them is having both versions on record. A single-version finding cannot distinguish "this never worked" from "this stopped working," and those imply different things about whether to expect a fix.

Nothing here changes the [five non-optional rules](../method/invariants.md). Rule 1 already says register through `.factory/settings.json` or a plugin, and that rule remains correct at both versions. What changes is the framing for an upstream report: this is a regression with a known-good prior version, not a documentation error.

## A second drift, stated carefully

The `droid exec -o json` envelope at 0.180.0 carries no `usage.factory_credits` field. At 0.186.0 the field is present and integer-valued.

This is flagged as **drift worth an upstream note, not a confirmed regression**, and the distinction is deliberate:

- It is a **single sample**, from one sanity-check run on one model. The hooks.json regression was an explicit A/B against a matching rig; this was not.
- Only the `usage` sub-dict was inspected. No broader envelope diff between the versions was produced, so "absent from `usage`" is not the same as "absent from the envelope."
- The field could have been added, renamed, or moved. The run establishes it was not in `usage` at 0.180.0 and nothing more.

It matters because Phase 0 leaned on that field. `factory_credits` being per-run is what makes one `droid exec` per role attribute cost cleanly, which is what [partially unblocks Probe 7](../probes/index.md) and what makes H3, the cheaper-executors hypothesis, measurable at all. PRD §13 asks for real numbers rather than "roughly 50% cheaper," and a field name that is not stable across a six-patch spread is a thin foundation for that.

The practical rule, which the evidence directory states as a version-stamp requirement: a cost-attribution test should record the **envelope field name** it relied on, not just the value. Field names turned out not to be stable.

## What this does and does not change

**Unchanged.** No verdict in `phase-0/GO-NO-GO.md` moves. The recommendation is still GO, still command-orchestrated rather than Mission-native, and every invariant status in [the scorecard](./index.md#the-verdict) stands.

**Strengthened.** The plugin-hook and hash-lock primitives now have evidence at two versions instead of one. That is the difference between "this works" and "this has worked across a six-patch spread," which is the claim a build decision actually needs.

**Sharpened.** One defect is reclassified from standing bug to regression, with a known-good version attached.

**Newly uncertain.** Per-role cost attribution rests on a field observed absent at an older version, from one sample.

## Limits

- **One older version, not a matrix.** 0.180.0 and 0.186.0. Nothing between them was tested, so "introduced between the two" does not identify which release broke it.
- **A different host.** Darwin 25.5.0 here against 24.6.0 for Phase 0, and a different pilot directory. The host is a confound that was not controlled for.
- **A subset of probes.** Four primitives, not eight invariants. Probes 1, 2, 3 and 8 were not re-run at 0.180.0.
- **Model availability differs between the versions**, which constrained which executor could be used. Recorded in `phase-0/evidence/canary-0.180.0/model-availability.md`.
- **No upstream report has been filed.** A draft exists in the evidence directory and is explicitly marked not sent.

## Related

- [The reference guard](./reference-guard.md) — the structural fix, and where the row-4 bypass is interpreted
- [Silent green](./silent-green.md) — the failure mode the hooks.json defect belongs to
- [Probe 4](../probes/probe-4-hook-blocking.md) — the hook-blocking rig this re-ran
- [Probe 6](../probes/probe-6-plugin-boundary.md) — the plugin primitive this re-ran
- [Open questions](../background/open-questions.md) — the defect list this reclassifies one entry in
- [Invariants](../method/invariants.md) — the five rules, unchanged by this run
