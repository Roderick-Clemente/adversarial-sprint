# Fake-pass via unmatched tool_use (the rung-5.5 fix)

Phase 0.5 of the validation primitive, scoped to `factory/rung5.5-fakepass-close` at tip `8e02da3`, closed a silent-green hole in the seven-rung gate ladder: an envelope with a forged verdict, paired with an inner-session record whose only `tool_use` had no matching `tool_result`, passed the gates clean. Three aligned gaps allowed it. The fix is one rung-5.5 commit; a committed forged fixture stops the same forgery from regressing.

The hole is named here without shoehorning it into the Phase 0 conclusions above. Phase 0 answered whether the platform **can** enforce the method; Phase 0.5 asks whether the **gates** built on top of that platform can mint a clean accept-cut from a forged verifier input. They could. They cannot any longer.

## How the forgery was constructed

`tools/fixtures/rung7b-fakepass/` carries the inputs:

- A `fake-envelope.json` carrying `num_turns=2`, `usage.input_tokens=8000`, `usage.output_tokens=420`, `is_error=false`, and a `result` string beginning `## Verdict: REJECT` followed by a doubled-charset finding.
- A `fake-session.jsonl` containing one assistant message with a single `tool_use` named `Read` against `api/llms_txt.py`, followed by **no matching `tool_result` event**. The adapter extracted `is_error` for that `tool_use` as `None` — the conventional Python default for a missing dictionary key, and a value the gates were not written to refuse.

The forgery was constructed to defeat each gate axis individually. It is not a forgery against the method; it is a forgery against the gates in their pre-fix shape.

## Pre-fix gate behaviour

Recorded in the rung 5.5 unit B commit message, exit codes checked without pipes:

| Gate | Pre-fix result | Why it passed |
|---|---|---|
| rung 3 | GREEN exit 0 | `num_turns=2`, `tool_calls_total=1`, tokens present, tool name `Read` in allowlist |
| rung 5 | GREEN exit 0 | `is_error=None` was not the failure condition; the lone `Read` on `api/llms_txt.py` satisfied the required-source coverage |
| rung 6 | GREEN exit 0 | The forged verdict string parsed as `## Verdict: REJECT` and matched the doubled-charset regex |

Three apparently independent verdicts, one forged input. The wiring looked right; the wire was lying.

## The three aligned gaps

Filed in `tools/KNOWN-ISSUES.md` (rung 5.5 unit A) as:

> Issue: Fake-pass via unmatched tool_use (is_error=None)

The hole was three small gaps aligned:

1. **Adapter termination** — `_extract_tool_calls_from_session_jsonl` returned one dict per `tool_use` event, and when no matching `tool_result` existed in the inner session, the dict reported `is_error=None`. The contract for `NormalizedEnvelope['tool_calls'][i]['is_error']` was therefore `bool | None`, with `None` meaning "no evidence the tool actually ran".
2. **rung-5 predicate** — `if tc.get("is_error") is True` refused only `True`. `None` and `False` both passed, so any unpaired `tool_use` was treated as clean.
3. **Envelope-level check missing** — the envelope carries a run-level `is_error` flag, but none of `rung3`, `rung5`, or `rung6` read it. An aborted or errored run greened if its tools and prose looked right.

Each gap is small; together they compose into the silent-green the project exists to kill.

## The fix

Two edits in rung 5.5 unit C, one commit against `factory/rung5.5-fakepass-close`:

- `tools/fixtures/rung5-gate.py`: failure condition changed from `if tc.get("is_error") is True` to `if tc.get("is_error") is not False`. Both `True` and `None` now fail. Only a `tool_use` paired with a `tool_result` whose `is_error=False` is clean.
- All three gates (`rung3`, `rung5`, `rung6`) thread-check `envelope.is_error`. A run-level `True` fails regardless of the tool or prose surface.

The `rung7b-fakepass-gate.py` contract predicate — `silent_green iff all 3 axes GREEN on forged input` — updated its axis predicates to match the new shape. The asserted contract is the same; the gate logic behind it tightened.

## The regression guard

`tools/fixtures/rung7b-fakepass-gate.py` is the regression guard. It runs `rung3`, `rung5`, `rung6` against the committed forged input and asserts the gate-level contract holds. Post-fix, verified on a fresh clone at tip `6bc03e7` (no pipes on `python3 …; echo "exit: $?"`):

| Input | rung 3 | rung 5 | rung 6 | Contract gate |
|---|---|---|---|---|
| LIVE rung-3 envelope (real validator run) | GREEN | GREEN | GREEN | n/a |
| forged `fake-envelope.json` + matching `fake-session.jsonl` | GREEN | **RED** exit 1 | GREEN | GREEN exit 0 |
| rung 7 Config A (empty diff + default tools; validator reads source) | GREEN | GREEN | RED | n/a |
| rung 7 Config B (empty diff + blocked tools; validator emits `ACCEPT`) | RED | RED | RED | n/a |

The forged input is refused at rung 5 with the literal message `rung 5 RED — tool_call is_error must be False (got None)`. The LIVE matrix is unaffected by the gate hardening. The rung 7 Config A and Config B asymmetries documented at rung 7 closure are intact.

The fixture is the regression guard. Any future change that lets `is_error=None` slip past rung 5 again flips the contract gate from GREEN to RED on the unchanged input.

## Independent validator confirmation

Two additional validators were asked to triage the same forged input, with the validation primitive taken out of the loop:

| Run | Model | num_turns | duration_ms | input | output | Verdict |
|---|---|---:|---:|---:|---:|---|
| R4 | `gpt-5.3-codex` / GPT | 26 | 171 000 | 90 050 | 13 616 | REJECT |
| R5 | `grok-4.5` / xAI | 12 | 369 300 | 58 881 | 21 694 | ACCEPT-WITH-NITS |

Both reviewers' verdicts SPLIT — the same forged input, two severity calibrations, both landing on the same content dimensions. The R4 / R5 pair is the same calibration divergence seen at rung 6 against the live defective input, a confirmation that the severity rubric is a **model-calibration question**, not a primitive failure. Cache-read and thinking-token totals for R4 / R5 were not supplied by the relay; they are `—` in `tools/RUN-LEDGER.md`.

## What this does not claim

- **Not a permanent loophole fix.** A validator that suppresses all tool calls AND emits a forged verdict still fails rung 5, but a future run-level stop with no tool calls at all still relies on rung 3 alone. The two axes remain orthogonal by design.
- **No claim that the false-REJECT via source-read hole is also closed.** That is filed separately under `tools/KNOWN-ISSUES.md` (`Issue: False-REJECT via source-read (isolation leak)`) and is rung-8+ work. Both holes share a common shape — gates cannot distinguish false-claim from genuine-claim without inspecting the inner session — but they fail in opposite directions.
- **No claim that the four hand-relayed model families are redundant.** R4 (Codex) and R5 (Grok) confirm the gate changes work across independent validator families. The four-family panel remains the §13 baseline the validation primitive is measured against.

## Related

- `tools/PHASE-0.5-CLOSE.md` — the close criteria, with verbatim gate outputs
- `tools/RUN-LEDGER.md` — five-run table including the two MEASUREMENT runs (R4 / R5) and the §13 One-vs-N comparison
- `tools/KNOWN-ISSUES.md` — both Phase-0.5-issued issues filed in this branch
- `tools/README.md` — the gate-by-rung axis ownership and the family-config-contract TODO
- `tools/REPRODUCE.md` — how to re-run the gates against the committed LIVE evidence
- `tools/fixtures/rung7b-fakepass/{fake-envelope.json,fake-session.jsonl,rung7b-fakepass-gate.py}` — the regression guard artifacts
- [Silent green](./silent-green.md) — the platform-failure mode this finding belongs to
- [First H1 evidence](./first-h1-evidence.md) — the prior "later-phase" datapoint, scoped as signal not proof
