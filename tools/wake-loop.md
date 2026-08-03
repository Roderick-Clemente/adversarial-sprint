# Wake-loop — async orchestrator/worker pattern

A hand-run instance of the command-orchestrated design this repo is building. An
**orchestrator** (a reviewer model, e.g. Claude/Opus) sleeps, wakes on a timer, polls a
**worker** (the `droid` running probes), cross-reviews any new work adversarially, and steers
it through an async channel — without a human babysitting either side.

It was built ad hoc to run Phase 0 overnight. In hindsight it is a **live simulation of the
Phase 1 architecture**: orchestrator ≠ worker, different model families, a fresh-context
reviewer inspecting the worker's committed output, feedback delivered out-of-band. Same
separation the reference guard enforces in code, run by hand here. Keep it — it is both a
useful tool and a working proof of the method.

> **This may be the product.** The PRD's own line — "if the manual harness is nearly as good,
> that is a finding" — points here. This pattern (orchestrator + worker + async steering,
> hand-run) already produced a full adversarial Phase 0. If the plugin build stalls, the
> wake-loop *is* the fallback, and it is a small one. Do not treat it as scaffolding to throw
> away.

## The two roles

| Role | Who | Does |
|---|---|---|
| Worker | `droid exec` / TUI | runs the actual work, commits **each unit** (commit = the baton), re-reads `STEER.md` at the top of each unit |
| Orchestrator | reviewer model (Opus) | sleeps on a timer, wakes, polls for new commits, cross-reviews as a fresh adversary, appends verdict/steering to `STEER.md`, re-arms the timer |

Neither edits the other's working tree. **Commits are the only baton.** The orchestrator writes
*only* to `STEER.md` (gitignored, worker-owned channel) — never to tracked files while the
worker is live (shared-worktree collision rule, see the repo `AGENTS.md`).

## Mechanism

The self-wakeup runtime gate is often off, so use a detached `sleep` as the timer. When it
exits, the harness re-invokes the orchestrator via a task-completion notification — that IS the
wake.

```bash
# arm one timer (10 min). run_in_background so it detaches and re-invokes on exit.
sleep 600; echo "WAKE 10m"
```

On each wake the orchestrator runs:

```bash
cd <repo> && git fetch <remote> --quiet
git log --all --oneline -1                                   # new commit since last wake?
find ~/.factory/sessions -type f -newermt '-12 minutes'      # worker still writing? (empty = idle)
ls phase-0/evidence/<expected-new-dir>/ 2>/dev/null          # expected artifact landed?
```

- **New commit / fresh evidence** → read it, cross-review adversarially (try to *refute* the
  finding), append a dated verdict + any steering to `STEER.md`, re-arm.
- **Nothing new** → re-arm, no nudge.
- **Idle at a known STOP point** → stand the loop down; nothing left to catch.

## Hard-won rules

1. **ONE timer.** Re-arming faster than timers drain gives you duplicates firing out of sync.
   Kill strays with `TaskStop` before arming a fresh one.
2. **"No session write for N min" is NOT a reliable stall signal.** Work can sit finished-but-
   uncommitted. During Phase 0 this produced a false "Probe 6 stalled" alarm — the droid had
   finished and just hadn't committed. Cheapest fix is on the worker side: tell it to commit
   *eagerly*, each unit. Don't escalate on idle alone; confirm with process CPU + last commit.
3. **Interval:** 10 min is the working default (5 is aggressive, 30 is a long heartbeat for a
   known-slow phase). Work if there's something, sleep if not.
4. **Steer via `STEER.md` only.** The worker acknowledges a note in its next commit message, not
   by editing the reviewer's text. Append under a dated heading; never rewrite history.
5. **Never touch tracked files while the worker is live.** `STEER.md` is the one safe write.
6. **Re-orient on wake.** If the orchestrator's context compacted between wakes, the wake message
   must carry enough to re-derive the job (repo path, remote, what "new" looks like, the STOP
   condition). Bank durable state in project memory, not just in-context.

## Worker-side prompt ingredients

The worker needs, up front: commit-each-unit, re-read `STEER.md` at the top of each unit,
per-unit branch, push to the dev remote only (main untouched), record BLOCKED-with-evidence
rather than retry-looping, and an explicit **STOP** condition (e.g. "draft the go/no-go, then
stop — do NOT start building"). Unsupervised building is the anti-pattern this project exists to
disprove; the worker plans and probes, the human gates the build.

## Standing it up / down

- **Up:** confirm the worker is live (`ps` for the droid + a recent session write), open/append
  `STEER.md`, arm one `sleep` timer.
- **Down:** `TaskStop` the timer when the worker hits a known STOP or the human takes over live.
  Leave `STEER.md` in place as the record of the run.
