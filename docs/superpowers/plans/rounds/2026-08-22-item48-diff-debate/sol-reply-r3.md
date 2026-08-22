Two findings remain.

1. Tenth instance: the new split gives `test_lock_protocol_live.py:400` the wrong description. [The bullet says it is “the same test as :381”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:901). It is actually inside the separate [`test_measurement_20_a_failed_host_invocation_never_reads_as_divergence`](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lock_protocol_live.py:393). The record later correctly says this test checks the fail-closed helper, is not bilateral, and can be rewritten for `pwsh` without losing its purpose. Thus the record again asserts and refutes the same characterization. The row remains `must-change`; only its description is wrong.

2. The structural count rule still has an uncovered live row total. [The new introduction states “83 rows, 83 one-line entries” and “3 bullets for 3 rows”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:764) without a commit binding. Those figures are true at this head, but they are not survey exit-code invariants and would move if migration values or rows changed. They also cannot inherit the preceding `a13d3c3` binding: at that commit the 83 rows existed, but the list still had only 50 bullets. Bind these list figures to `b1e9cfa` or remove the absolute totals.

Other results:

- Exit-predicate change passes. `skipped` now correctly makes the gate fail. A tracked binary, gitlink, broken symlink, missing file, or permission-denied file would fail visibly; that is appropriate because the survey cannot support its completeness claim over an unscanned path. The current tree has zero skipped paths and zero gitlinks.
- Independent live scan: 5592 bare / 1344 host / 572 launch = 7508, zero skipped. No current `7508` claim appears in the record.
- Positional-citation class is closed on the current editable surface: zero `run.py:<n>`, zero `entry-points.tsv:<n>`, and zero alternate “line N”/“row N” spellings into the record, survey, TSV, re-exec, or missing-pwsh artifacts.
- The 83-bullet multiset exactly matches the 83 TSV `must-change` rows, including duplicate counts for all five family pairs.
- Description sample: **36 newly split source lines checked; 35 correct, 1 wrong**—the `:400` finding above.
- The commit-bound residual count at `b416508` is 34, and the classification table at `a13d3c3` reproduces exactly.
- The corrections-versus-misses wording and removal of the duplicated `survey.py` quote are correct.
- The five-condition CONDITIONAL verdict remains sound.

FIX