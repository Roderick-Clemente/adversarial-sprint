# Pilot spec — `/llms.txt` for QuantumBank (Tier B, first real adversarial run)

**Status:** DRAFT spec, reconstructed Aug 3 (original was in-context, lost to compaction).
**Repo under change:** `Roderick-Clemente/quantum-bank.git` — a small **Flask** demo bank
(feature-flags via Split.io, SQLite login). Cloned on the **mini**, not the laptop.
**Why this change:** a `/llms.txt` endpoint tells any bot that stumbles on the app what it is —
"simple and mostly invisible but useful" (Rod). Small enough to be a clean first pilot; real
enough to be worth having.

---

## The change (one file added, one route wired, one test)

1. **`api/llms_txt.py`** — new handler `handle_llms_txt()` returning
   `Response(body, mimetype="text/plain; charset=utf-8")`.
   (Mimetype precedent already in the repo: `/metrics` returns plain text.)
2. **`app.py`** — thin route stub `@app.route("/llms.txt")` delegating to the handler
   (matches the repo's existing pattern: `app.py` routes are thin, logic lives in `api/<name>.py`
   with `handle_*` names).
3. **`test/test_public_routes.py`** — behavioral test using the existing `client` fixture
   (`test/conftest.py`).

## `/llms.txt` body content (what the bot reads)

Plain text. Must contain, at minimum:
- The name **"Quantum Bank"**
- A **demo disclaimer** — this is a fictional bank for Rod Clemente & friends' demos, not a real
  financial institution
- A mention of **"Split.io"** (the feature-flag system it showcases)

## Acceptance criteria (GREEN)

- `GET /llms.txt` → **200**
- `Content-Type` is **`text/plain`** (charset ok)
- body contains **"Quantum Bank"**, the demo-disclaimer, and **"Split.io"**

## Valid-RED definition (the gate before any implementation)

The test must **fail with a 404** (route doesn't exist yet) — NOT with an import error, a fixture
error, or a syntax error. A syntax error is not a RED. If the first run errors for the wrong
reason, fix the *test scaffolding* until it fails for the *right* reason, then proceed.

---

## Adversarial seat assignment (family separation — invariant #1)

The whole point: no single model family plans AND reviews, or executes AND validates.
Available families on droid 0.180/0.186: Claude, GPT-5.x, Gemini 3.x, Grok 4.5, Droid Core
(Kimi/GLM/DeepSeek/etc.).

| Seat | Job | Family (must differ as noted) |
|---|---|---|
| **Planner** | GROK: draft analysis, acceptance criteria, risks, test strategy | e.g. Claude Opus |
| **Plan reviewer** | Blind review of the plan — different family from planner | e.g. Gemini or GPT-5 |
| **Test author** | Write the behavioral test (independent of executor) | any family ≠ executor |
| **Executor** | CHUNK+EXECUTE: prove RED, implement GREEN | e.g. GPT-5.4-mini (cheap, cross-family) |
| **Validator** | Fresh-context: sees spec + diff + test output only, NOT executor's reasoning | different family from executor |

**Rule:** plan reviewer ≠ planner's family; validator ≠ executor's family. Test author ≠ executor.

## The manual two-CLI baseline arm (§13 — the honest comparison)

Do the SAME change a second way: one operator, hand-driving two CLIs (no plugin orchestration),
recording **cost, wall-clock, and operator-intervention count**. This is NOT a strawman — if the
manual harness turns out nearly as good as the orchestrated run, *that is a valid finding* and
the PRD explicitly says to record it honestly.

## Assert-on-reality (the non-negotiable from Phase 0)

Every gate checks REALITY, never exit code:
- RED proven = test actually ran and failed with 404 (read the output, not `$?`)
- GREEN proven = test actually ran and passed (read the output)
- Silent-green is Factory's default failure mode — a green exit proves nothing.

## Hard stops

- STOP before merge to main. Human gates the merge.
- STOP before opening a PR.
- No `gh` calls without Rod's explicit OK.
- If BLOCKED (missing dep, interactive tap, etc.): record BLOCKED-with-evidence, do NOT retry-loop.

---

## Open gates before running (Rod decides)

1. **Run mode:** live-orchestrated (~30–60 min, Rod watches the seat handoffs — the showcase) vs
   unattended-bounded (safe but single-seat, not the cross-family demo). These are DIFFERENT runs.
2. **Where the orchestrator lives:** overnight/unattended has no live orchestrator — either a
   scripted harness (that's Phase 0.5, unbuilt) or accept a single-seat run.
3. **Findings doc** `~/work/quantum-bank-findings.md` is on the mini — surface/commit it so this
   spec can be checked against the real repo structure before executing.
