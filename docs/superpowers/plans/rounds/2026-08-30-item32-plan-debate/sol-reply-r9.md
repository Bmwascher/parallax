## 1. The four requested changes

1. Independent expected-directory and expected-round binding is specified in the executable Poll order, and the named test covers both mismatches separately. However, the pinned contract region places LAUNCH UNKNOWN before `receipt-not-expected`, contradicting the executable requirement that the mismatch be checked before any directory opens. Its proposed test uses a completed old directory, so the wrong order can still return `receipt-not-expected`; “assert no artifact was read” has no concrete observation mechanism. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:52-53`, `:72-73`, `:118-127`, `:193-210` — **DOES NOT CLOSE**

2. The schema and exit mapping are now explicit and have named tests, but the classification is internally inconsistent: an unreadable receipt is `no-receipt`/exit 1, while an “unreadable argument” is also named as exit 2 without distinguishing the two. More importantly, the mapping deliberately gives `running` exit 0, producing the ninth completion hole below. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:55-58`, `:74-75`, `:120` — **DOES NOT CLOSE**

3. The old “LAUNCH UNKNOWN first” wording was changed, but it is stale again. After adding `receipt-not-expected`, the executable order is NO RECEIPT, RECEIPT NOT EXPECTED, then LAUNCH UNKNOWN; Task 2 and Task 9 still declare LAUNCH UNKNOWN second. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:118-123`, `:193-210`, `:271-277`, `:749-751` — **DOES NOT CLOSE**

4. The negative oracle now correctly identifies the catch as step 7 and identifies step 5 as the PID/start-time write. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:112-114`, `:133-136` — **CLOSES**

## 2. Ninth-instance sweep

I used the requested eight-of-eight base rate. The plan itself says unfinished rounds must never be readable as complete and instructs implementers to treat the class as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:21-26`

I found a ninth instance: **`running` exits successfully, leaving completion safety dependent on prose.**

- Input: a live wrapper has already created a nonempty reply but has not written its exit file. Task 8 deliberately constructs this arrangement with a stub that writes the reply and then sleeps. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:714-716`
- Sequence: Poll correctly detects matching PID/start time and returns `running` without inspecting terminal artifacts, but exits 0. A caller or shell control flow using conventional exit status proceeds down its success path unless it separately obeys the Markdown instruction to inspect `state`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-58`, `:125`, `:230-231`, `:430-434`
- Artifact exposed as this act’s result: the still-being-written reply file. The current per-site tests assert that the Poll command exists, but do not test a caller branch that refuses to read the reply when Poll exits 0 with `state=running`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:342-349`, `:509-521`

The phrase “EXIT 0 IS NOT A RESULT” is therefore the same shape this cycle was created to eliminate: a safety rule written beside a command rather than made fail-closed by the command. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:23-26`, `:230-231`

Smallest correction: exit 0 only for `reply-present`; assign `running` a distinct exit code such as 3 meaning UNFINISHED. Keep 1 for classified transport failures and 2 for invocation/internal errors. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:54-58`

## 3. Do the new rules have real oracles?

- **Receipt schema: partial.** The named test covers every missing field, every empty string, unparsable ticks, one wrong JSON type, and an extra field. It does not require a wrong-type case for each field or explicitly cover a non-object top-level JSON value, despite the contract requiring an object and typed fields. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:56`, `:74`
- **Exit mapping: mechanically pinned, but unsafe.** One case per state will catch an implementation that differs from the specified mapping. The problem is that the test deliberately locks `running → 0`, so the oracle protects the ninth hole rather than closing it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57`, `:75`
- **`receipt-not-expected`: comparison presence is pinned; ordering is not.** The three mismatch cases catch omission of either comparison. Because R1 is a completed directory, an implementation may open and inspect it first and still eventually return `receipt-not-expected`. Add a mismatched receipt pointing to a nonexistent or uncommitted directory and require `receipt-not-expected`; that makes checking LAUNCH UNKNOWN first observably fail. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-73`, `:120-123`

There is one additional prose-without-mechanism claim: the receipt is required to live outside the dispatch directory, but the interface accepts an arbitrary `-ReceiptPath`, and neither the launch steps nor a named test rejects an equal or descendant path. Either enforce the resolved-path separation and test it, or stop claiming the tool guarantees it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-50`, `:66-81`, `:108-114`

## 4. Contradiction sweep

I found three:

1. **State order:** Task 1 says NO RECEIPT → RECEIPT NOT EXPECTED → LAUNCH UNKNOWN; the pinned region and Task 9 say NO RECEIPT → LAUNCH UNKNOWN → RECEIPT NOT EXPECTED. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:118-123`, `:193-210`, `:273`, `:751`
2. **Unreadable input:** an unreadable receipt is classified `no-receipt`/exit 1, while “an unreadable argument” is listed under exit 2. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:55-57`, `:120`
3. **Exit semantics:** the plan says its codes match `new-review-mirror.ps1`, whose zero means “built and clean,” while assigning zero to an unfinished `running` round. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-58`; `tools/new-review-mirror.ps1:17-22`

The convergence grep cannot catch the state-order contradiction; it searches stale names and counts, not their ordering. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:753-766`

## 5. Freeze decision

The plan is not ready to freeze. The smallest sufficient changes are:

1. Put `receipt-not-expected` second everywhere and add the nonexistent/uncommitted-directory ordering regression.
2. Make `running` exit with a distinct UNFINISHED code; reserve zero for `reply-present`.
3. Specify that unreadable receipt content is `no-receipt`/exit 1 and narrow exit 2 to parameter-binding or internal execution failures.
4. Enforce and test that the resolved receipt path is outside the resolved dispatch directory, or withdraw that guarantee.
5. Expand the schema test so each field’s wrong type and a non-object top-level value are refused.

The real two-host detachment, delayed exit publication, and non-ASCII round binding remain future measurements in Task 8 rather than facts currently verified in this mirror. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:704-728`

**FIX**