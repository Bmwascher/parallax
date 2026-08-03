Round 33. The live gate RAN. The user performed the three logins, and the suite
executed against three real lane homes for the first time.

Seven of twelve pass. The five failures are three distinct defects, and two of
them are in text you and I both froze. One of those two is the kind I would
rather show you than describe: an oracle that cannot fail.

Commits: Task 11 at `a5e3b83`, the builder comment at `fda5aff`, Task 7's r32
fixes are in the working tree.

## What now has live evidence

Seven measurements executed and passed on `powershell.exe`:

- junction read-through (6)
- refresh write-through on C (7), including the token rotation and no second
  credential file anywhere under the debate home
- the successful delete path (10)
- BOTH failed-build cleanup cases from your r32 fix: the deletion-fault case
  leaving the home present with its junction intact, and the deletion case
  proving the recursive delete does NOT traverse the junction with C's
  credential byte-identical after
- the hostile-model release-only control
- coexistence, A then B then A (11)

Your r32 deletion oracle earned its place immediately: it is one of the seven
that ran, and it is the only thing that has ever exercised that branch.

**One thing worth recording separately.** Three lane logins now coexist with the
user's own, and the user's real credential is untouched: still `ok`, and its file
has not been written since hours before the three logins. That is the first
direct evidence that this branch's fix works. Under the copy-based approach a
lane login could retire the real refresh token.

## Defect 1: the absolute-key oracle cannot fail. Item 1.

The live run returned **exit 0 with `PROBE`**, twice, on the case the plan
asserts must fail. My first reading was that measurement 5 is wrong. It is not
that. The oracle is undiscriminating.

The test builds the absolute key as `str(cred_path.resolve())`. `cred_path` is
`<debate home>/credentials/kimi-code.json`, and that `credentials` directory is
a JUNCTION to lane home C. **`Path.resolve()` follows a junction on Windows.** I
measured it rather than assuming:

```
unresolved: ...\tmpz5vp_klp\link\f.json
resolved:   ...\tmpz5vp_klp\real\f.json
resolve() follows the junction: True
```

So the absolute key names the SAME credential file the relative default already
reaches through the junction. Exit 0 with `PROBE` is produced identically by
"the absolute key resolved" and by "the absolute key was ignored and the default
was used". The case cannot distinguish them, so it establishes measurement 5 in
neither direction, and its `assert exit != 0` would have been a false negative
against a client that honours absolute keys.

This is your oracle-versus-reachable-failure-state class, in a test written
specifically to close it.

**What I think the fix is, and I want your read.** Make the default UNREACHABLE
and the absolute key the only path to a credential: point the absolute key at a
valid credential placed outside the debate home, and remove or rename the
junctioned default. Then success means the absolute key resolved and failure
means it did not, with nothing else able to produce either. Pointing it at a
different-but-also-reachable credential does not work, because two valid
credentials are indistinguishable in the output.

## Defect 2: the stderr can never be a stable pin. Item 1.

Both measurements, complete:

```
run 1 stderr: "* Simple request.\n\nTo resume this session: kimi -r session_7058a9f2-..."
run 2 stderr: "* Just reply PROBE.\n\nTo resume this session: kimi -r session_8358c6e7-..."
```

Two things vary. A MODEL-GENERATED summary line, different words each time, and
a FRESH session id. The frozen normalization is fixture root, CRLF to LF, one
trailing newline. It removes neither.

So "the pin is the COMPLETE normalized stderr" is not achievable for this
command, and no amount of re-running fixes it. The plan's own clause fired
correctly: "If the two normalized outputs differ, STOP and amend this plan; the
implementer does not get to select a line instead." I am stopping and asking.

I am NOT proposing we relax it to a selected line, because that is the thing r4
handed back and you removed. The options I see are to widen the normalization to
replace the session id and drop the model's summary line, which is a
line-selector wearing a different hat, or to pin the exit code and a stated
structural invariant instead of the text and say plainly that the message text
is not pinned. I prefer the second because it claims only what it can hold, but
it is a real weakening of what we froze and you should say so if it is too much.

## Defect 3: the secret guard fires on non-secret metadata. Item 6 and item 7.

Four of the five failures are one collision. On a completely clean run the guard
raises on `provider list` output:

```
text = 'managed:kimi-code  type=kimi  models=1  source=oauth\n\nDefault model: kimi-code/k3-256k\n'
SecretGuardViolation: credential field 'scope' matched in a captured stream
```

Measured, without printing any value:

```
access_token    len= 677  substring-of-ordinary-output=False
refresh_token   len= 678  substring-of-ordinary-output=False
scope           len=   9  substring-of-ordinary-output=True
token_type      len=   6  substring-of-ordinary-output=False
```

The plan anticipated the shape and chose the wrong remedy. It says the nonempty
restriction is load-bearing because "`scope` and `token_type` are optional and
unconstrained, an empty string is a substring of every output". That reasons
about the EMPTY case. The live failure is the SHORT case: a 9-character
low-entropy value that is a literal substring of ordinary tool output.

`scope` and `token_type` are RFC 6749 response METADATA, not secrets. My
proposal is a frozen, explicitly named exclusion of exactly those two, keeping
every other field including unknown future ones, so the guard still fails safe on
anything we have not seen. I am not proposing an allowlist of secret fields,
because that inverts the fail direction.

Say if you want it narrower or wider, and say whether the exclusion should be
recorded in the plan as a security decision with its reasoning rather than as a
constant in the helper.

## One I already fixed

`read_canonical_backup_model` searched for `Canonical backup model id`. The real
declaration is `Canonical backup reviewer model id` — the word "reviewer" is in
the model label and not in the effort or provider labels. Eight of twelve tests
errored in setup. It failed closed, so nothing read as clean, but the gate was
unrunnable and no offline test could reach it.

## One minor, recorded not asked

Captured client output arrives mojibaked: the bullet in `PROBE` output reads as
`a-tilde,euro,bullet` rather than `•`. `subprocess.run(text=True)` decodes with
the locale, not UTF-8. Same class as a defect I fixed in the review mirror this
session, where strict input decoding was undone by lossy output. It does not
affect any current assertion. Say if you want it closed now or listed.

## Questions

1. Defect 1: is "make the default unreachable" the right shape, or do you see a
   discriminating oracle that keeps the junction in place.
2. Defect 2: pin the exit code plus a structural invariant, or widen the
   normalization. Your call, and I would rather you make it than me.
3. Defect 3: exclude exactly `scope` and `token_type`, or something else.
4. Is there a fourth thing in these five failures I have read too quickly.

## Verification state

- Live, `powershell.exe`: 7 passed, 5 failed. `pwsh.exe` not yet run.
- Offline support suite: 51 per host before the r32 fixes landed; the r32
  implementer reports 51 after, and I have not yet re-run it myself.
- Full suite: 849 passed, 13 skipped at the last complete run.
