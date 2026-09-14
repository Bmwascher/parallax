# Fable fix wave: two edits in agents/escalation-implementer.md

Source: the Fable whole-branch review of 65f70c2..1ab7426 (fable-diff-r1-reply.md), Minor 1 and Minor 2, both accepted by the session. Zero-judgment transcription: replace exactly the quoted spans, nothing else. The file is UTF-8, LF line endings.

**Files:**
- Modify: `agents/escalation-implementer.md` (two spans)

- [ ] **Step 1: Drop the parenthetical that lets a reroute record carry decision points (Minor 1)**

Replace this exact span (lines 33-36):

```
The frozen plan (or the consented reroute record) ENUMERATES this
task's open decision points, each with the constraints that bound it.
That list is the whole of your delegated judgment, and it is the one
place the contract above is suspended:
```

with:

```
The frozen plan ENUMERATES this task's open decision points, each with
the constraints that bound it; a consented reroute record enumerates
none. That list is the whole of your delegated judgment, and it is the
one place the contract above is suspended:
```

- [ ] **Step 2: Name the ledger's Lane line in entry route 2 (Minor 2)**

Replace this exact span (lines 54-58):

```
2. Blocked-task reroute: a task the Flash lane blocked reaches you
   only with user consent, recorded in the cycle's SDD ledger before
   you start, and its envelope is EMPTY by construction: the task was
   frozen as zero-judgment, and consent to reroute it is not consent to
   redesign it. Unattended runs fail closed.
```

with:

```
2. Blocked-task reroute: a task the Flash lane blocked reaches you
   only with user consent, recorded in the cycle's SDD ledger before
   you start; the dispatch prompt carries the ledger's line
   `**Lane:** parallax:escalation-implementer (consented reroute, <ledger path>)`,
   and its envelope is EMPTY by construction: the task was
   frozen as zero-judgment, and consent to reroute it is not consent to
   redesign it. Unattended runs fail closed.
```

- [ ] **Step 3: Verify**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py evals/multi-model-verify/test_seat_reshuffle.py -q 2>&1 | grep -E "passed|failed|FAILED"`

Expected: `0 failed` (the pins `only with user consent`, `its envelope is EMPTY by construction`, `enumerated decision envelope`, `DEVIATIONS - must be \`none\`` and `An empty envelope means an empty section` each stay on one physical line).

Byte check (every line must print True):

python -c "import re,pathlib;R=lambda p:pathlib.Path(p).read_text(encoding='utf-8');b=R('C:/Temp/parallax-scratch/2026-09-13-single-implementer/fable-fix-brief.md');k=re.findall(r'```\n(.*?)```',b,re.DOTALL);e=R('agents/escalation-implementer.md');print('span1:',k[1].strip() in e and k[0].strip() not in e);print('span2:',k[3].strip() in e and k[2].strip() not in e);print('crlf free:','\r' not in e)"

- [ ] **Step 4: Commit**

```bash
git add agents/escalation-implementer.md
git commit -m "apply the fable review: a consented reroute record enumerates no decision points, and entry route 2 names the ledger's lane line"
```
