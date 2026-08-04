#!/usr/bin/env python3
"""Wiki link audit — run before uploading droid-wiki/ to the Factory app.

Checks every markdown link in droid-wiki/ for four failure classes. The last one
is invisible from a plain filesystem check and is the reason this script exists:
the published wiki receives ONLY the droid-wiki/ subtree, so a link from a wiki
page to anything outside it (../../pilots/, ../../PRD.md) resolves locally and
404s for anyone reading the wiki in the app.

  dead      — target file does not exist on disk
  anchor    — target file exists but has no matching #heading
  absolute  — http(s):// link on a wiki page (house rule: backticked repo paths
              or in-wiki relative links only; absolute URLs got scrubbed once and
              should not creep back)
  escaping  — a droid-wiki/ page links to a path outside droid-wiki/ (resolves in
              git, 404s in the published wiki)

Exit 0 = clean, exit 1 = findings. Assert on the published boundary, not the disk.
"""
import os
import re
import sys

WIKI = "droid-wiki"
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def slug(heading):
    h = heading.strip().lower()
    h = re.sub(r"[^\w\s-]", "", h)
    return re.sub(r"\s+", "-", h)


def anchors_of(path):
    out = set()
    with open(path, errors="ignore") as f:
        for line in f:
            m = re.match(r"#+\s+(.*)", line)
            if m:
                out.add(slug(m.group(1)))
    return out


def main():
    root = os.getcwd()
    if not os.path.isdir(WIKI):
        print(f"error: run from repo root (no {WIKI}/ here)", file=sys.stderr)
        return 2

    anchor_cache = {}
    findings = []
    page_count = 0

    for dp, _, files in os.walk(WIKI):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            page = os.path.normpath(os.path.join(dp, fn))
            page_count += 1
            base = os.path.dirname(page)
            with open(page, errors="ignore") as f:
                body = f.read()
            for _text, url in LINK.findall(body):
                if url.startswith("mailto:"):
                    continue
                if url.startswith("http://") or url.startswith("https://"):
                    findings.append(("absolute", page, url))
                    continue
                path, _, frag = url.partition("#")
                if path == "":
                    target = page  # same-page anchor
                else:
                    target = os.path.normpath(os.path.join(base, path))
                    # escaping: a wiki page pointing outside the published subtree
                    if not (target + os.sep).startswith(WIKI + os.sep) and target != WIKI:
                        findings.append(("escaping", page, url))
                if not os.path.exists(target):
                    findings.append(("dead", page, url))
                    continue
                if frag and target.endswith(".md"):
                    if target not in anchor_cache:
                        anchor_cache[target] = anchors_of(target)
                    if frag not in anchor_cache[target]:
                        findings.append(("anchor", page, url))

    counts = {k: 0 for k in ("dead", "anchor", "absolute", "escaping")}
    for kind, _p, _u in findings:
        counts[kind] += 1
    summary = " ".join(f"{k}={counts[k]}" for k in counts)
    print(f"{page_count} pages · {summary}")

    if findings:
        for kind, page, url in findings:
            rel = os.path.relpath(page, root)
            print(f"  {kind.upper():9} {rel}  ->  {url}")
        return 1
    print("clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
