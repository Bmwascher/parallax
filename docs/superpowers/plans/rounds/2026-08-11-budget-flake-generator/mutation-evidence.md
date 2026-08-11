# Retained mutation evidence, 0.23.0 backlog item 9

**Why this file exists.** The frozen plan required, for both
generated modules, that the failing output NAMING THE KILLING CASE
be retained for every mutant. It was not, and the diff debate's
round 1 raised it as an unmet retention requirement rather than as
an unverifiable chronology. This is that output.

**What it does and does not prove.** It proves that with one
defensive clause removed, a NAMED generated case disagrees with the
frozen oracle. It does NOT prove the parser is correct, and it does
not prove the matrix is complete: a mutant no case kills is reported
as a coverage hole by the same test, and two such holes were found
and closed during the build.

Each run stops after three killers per mutant, so the lists below are
the first three, not every case that would have caught it.

Regenerate with the two commands below; the killers are printed by
the tests themselves, so `-s` is required and no post-processing is.

## A. Route parser, `test_route_parser_shapes.py`

```
python -m pytest evals/multi-model-verify/test_route_parser_shapes.py::test_every_defence_is_killed -q -s
```

Ten mutants, ten killed, 0 survivors. Run 2026-08-11 against the
post-rebuild matrix: 122 sweep-A cases, 360 frozen sweep-B cells and
16 declared extras, 498 cases in all. The 360 and the 16 are sweep B
alone; sweep A is a separate enumeration and most of the killers below
come from it.

```
1-ansi-not-stripped-before-locating killed by: A[coloured,rules=2,decoy=False,eol=lf] (expected True, got False); A[coloured,rules=2,decoy=False,eol=crlf] (expected True, got False); A[coloured,rules=2,decoy=True,eol=lf] (expected True, got False)
2-rule-length-floor-dropped killed by: A[below-floor,rules=2,decoy=False,eol=lf] (expected False, got True); A[below-floor,rules=2,decoy=False,eol=crlf] (expected False, got True); A[below-floor,rules=2,decoy=True,eol=lf] (expected False, got True)
3-rule-shape-loosened killed by: A[dash-prefixed-text,rules=2,decoy=False,eol=lf] (expected False, got True); A[dash-prefixed-text,rules=2,decoy=False,eol=crlf] (expected False, got True); A[dash-prefixed-text,rules=2,decoy=True,eol=lf] (expected False, got True)
4-no-block-searches-whole-output killed by: A[exactly-8,rules=0,decoy=False,eol=lf] (expected False, got True); A[exactly-8,rules=0,decoy=False,eol=crlf] (expected False, got True); A[exactly-8,rules=1,decoy=False,eol=lf] (expected False, got True)
5-last-two-rules-instead-of-first-two killed by: A[exactly-8,rules=3,decoy=False,eol=lf] (expected True, got False); A[exactly-8,rules=3,decoy=False,eol=crlf] (expected True, got False); A[exactly-8,rules=3,decoy=True,eol=lf] (expected True, got False)
6-label-count-dropped killed by: X[model,valid-plus-bare-label] (expected False, got True); X[provider,valid-plus-bare-label] (expected False, got True); X[reasoning effort,valid-plus-bare-label] (expected False, got True)
7-counts-loosened-to-at-least-one killed by: B[model,twice,well-formed,esc=none,eol=lf] (expected False, got True); B[model,twice,well-formed,esc=none,eol=crlf] (expected False, got True); B[model,twice,well-formed,esc=in-label,eol=lf] (expected False, got True)
8-first-match-wins killed by: B[model,twice,well-formed,esc=none,eol=lf] (expected False, got True); B[model,twice,well-formed,esc=none,eol=crlf] (expected False, got True); B[model,twice,well-formed,esc=in-label,eol=lf] (expected False, got True)
9-sandbox-not-compared killed by: B[sandbox,absent,well-formed,esc=none,eol=lf] (expected False, got True); B[sandbox,absent,well-formed,esc=none,eol=crlf] (expected False, got True); B[sandbox,absent,well-formed,esc=in-label,eol=lf] (expected False, got True)
10-patterns-unanchored killed by: X[model,name-appears-mid-line] (expected True, got False); X[provider,name-appears-mid-line] (expected True, got False); X[reasoning effort,name-appears-mid-line] (expected True, got False)
```

Note which cells do the work: mutants 7 and 8 are killed by
`presence=twice` cells, and mutant 9 by a `presence=absent` cell.
The pre-rebuild matrix DID kill all three, using hand-added cases that
sat outside any specified enumeration. So the rebuild did not create
these shapes; it moved equivalent inputs inside the frozen product and
gave them product case IDs. That is a smaller claim than 'the old
matrix could not have caught this', and it is the true one.

## B. `Get-SkillReport`, `test_skill_report_shapes.py`

```
python -m pytest \
  evals/multi-model-verify/test_skill_report_shapes.py::test_every_defence_is_killed \
  evals/multi-model-verify/test_skill_report_shapes.py::test_every_fallback_defence_is_killed_under_the_fault \
  -q -s
```

Five direct mutants and three fallback mutants, all eight killed, 0
survivors. The three fallback mutants run under the DECLARED
fail-open fault model: the ambiguity fallback is unreachable while
the masking guard holds, so the guard is failed open first and the
fallback is then mutated. A separate test shows the fallback
classifying correctly under the fault alone, which is what stops
this arrangement from making a decorative fallback look
load-bearing.

```
1-body-sliced-from-masked-text killed by: o1c1/opener-first/inside/quoted-none/lf.entries (expected 1, got 0); o1c1/opener-first/inside/quoted-none/crlf.entries (expected 1, got 0); o1c1/opener-first/inside/quoted-one-opener/lf.entries (expected 1, got 0)
2-close-before-open-accepted killed by: o1c1/closer-first/inside/quoted-none/lf.ambiguous (expected True, got False); o1c1/closer-first/inside/quoted-none/crlf.ambiguous (expected True, got False); o1c1/closer-first/inside/quoted-one-opener/lf.ambiguous (expected True, got False)
3-only-openers-counted killed by: o1c2/opener-first/inside/quoted-none/lf.ambiguous (expected True, got False); o1c2/opener-first/inside/quoted-none/crlf.ambiguous (expected True, got False); o1c2/opener-first/inside/quoted-one-opener/lf.ambiguous (expected True, got False)
4-zero-and-one-collapsed killed by: o1c0/opener-first/inside/quoted-none/lf.ambiguous (expected True, got False); o1c0/opener-first/inside/quoted-none/crlf.ambiguous (expected True, got False); o1c0/opener-first/inside/quoted-one-opener/lf.ambiguous (expected True, got False)
5-heading-searched-in-whole-text killed by: o1c1/opener-first/inside/quoted-one-opener/lf.entries (expected 1, got 0); o1c1/opener-first/inside/quoted-one-opener/crlf.entries (expected 1, got 0); o1c1/opener-first/inside/quoted-opener-and-closer/lf.entries (expected 1, got 0)
6-unreadable-entry-dropped-silently killed by: entries/no-file-marker.malformed (expected True, got False); entries/no-file-marker/crlf.malformed (expected True, got False)
7-joined-entries-not-detected killed by: entries/joined-on-one-line.entries (expected 0, got 1); entries/joined-on-one-line/crlf.entries (expected 0, got 1)
8-known-containers-not-masked killed by: o0c0/opener-first/inside/quoted-one-opener/lf.present (expected False, got True); o0c0/opener-first/inside/quoted-one-opener/crlf.present (expected False, got True); o0c0/opener-first/inside/quoted-opener-and-closer/lf.present (expected False, got True)
```

Host: the interpreter `PARALLAX_PS_HOST` selected for this run. CI's
`powershell-hosts` job re-runs the module under both Windows
PowerShell 5.1 and PowerShell 7; a green run here is ONE
interpreter.

