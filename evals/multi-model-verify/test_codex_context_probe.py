"""Parser and classifier for the codex context probe (0.17.0, backlog item 4).

The probe exists because preflight 3 has only ever enumerated the reviewed
tree, while every source that hijacked a review on 2026-07-28 lived on the
reviewer's own machine. These tests lock the parser against fixtures whose
SHAPE is copied from the real CLI, so a shape change is a red, never a
silent empty result.

Fixtures are synthetic on purpose. This repo is public, and a raw
`prompt-input` recording carries the author's global AGENTS.md verbatim
plus the whole layout of their home skills directory.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "codex-context-probe.ps1"
FIXTURES = Path(__file__).parent / "fixtures" / "codex-prompt-input"
STUB = Path(__file__).parent / "fixtures" / "stub-codex" / "stub-codex.ps1"

# The script body past param(), so the tests can dot-source the functions
# without triggering the mandatory-parameter prompt. Same slicing the
# attestation tests use.
BODY_START = "function Get-PromptText"
BODY_END = "$toplevel ="


def ps_host():
    """PARALLAX_PS_HOST selects the interpreter. A green suite on one
    Windows host proves ONE interpreter - 0.16.1 shipped a lock that did
    not lock on pwsh because every local run used powershell.exe."""
    return os.environ.get("PARALLAX_PS_HOST", "powershell.exe")


def run_functions(snippet):
    """Dot-source the probe's function block, then run `snippet`."""
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         body + "\n" + snippet],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def bucket_counts(fixture, workdir="C:/fixture/repo"):
    path = (FIXTURES / fixture).as_posix()
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{path}");'
        ' $r = Get-SkillReport $t;'
        ' $b = @{repo=0;"plugin-cache"=0;home=0;unknown=0};'
        ' foreach ($e in $r.Entries) {'
        f'   $b[(Get-SkillScope $e.Path "{workdir}")] += 1 }};'
        ' "{0} {1} {2} {3} {4} {5}" -f $r.BlockPresent, $r.Entries.Count,'
        ' $b["repo"], $b["plugin-cache"], $b["home"], $b["unknown"]'
    )
    parts = out.split()
    return parts[0], [int(p) for p in parts[1:]]


def test_full_fixture_buckets_are_all_asserted():
    # All four counts are named, not just the total. A re-normalized
    # fixture that shifts entries between buckets while keeping the total
    # would otherwise pass unchanged.
    present, counts = bucket_counts("full.json")
    assert present == "True"
    assert tuple(counts) == (60, 0, 31, 29, 0)


def test_the_two_home_sources_are_counted_separately():
    # The fixture contract fixes 24 user-directory entries and 5 built-in
    # ones. Asserting only `home == 29` would let a 23/6 normalization
    # pass.
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "full.json").as_posix()}");'
        ' $r = Get-SkillReport $t;'
        ' $u = 0; $s = 0;'
        ' foreach ($e in $r.Entries) {'
        '   $p = $e.Path.Replace("\\","/");'
        '   if ($p -like "*/.agents/skills/*") { $u += 1 }'
        '   elseif ($p -like "*/.codex/skills/.system/*") { $s += 1 } };'
        ' "{0} {1}" -f $u, $s'
    )
    assert [int(v) for v in out.split()] == [24, 5]


def test_flagged_fixture_has_no_cache_entries():
    present, counts = bucket_counts("flagged.json")
    assert present == "True"
    assert tuple(counts) == (29, 0, 0, 29, 0)


def test_repo_agents_fixture_has_a_repo_scoped_entry():
    _, counts = bucket_counts("repo-agents.json")
    assert counts[1] == 1, "the planted entry must land in the repo bucket"


def test_a_malformed_block_is_present_but_yields_nothing():
    # The false-clean case: BlockPresent True with zero entries. The top
    # level is what must refuse it; here we only prove the parser reports
    # the two facts separately so the caller CAN refuse it.
    present, counts = bucket_counts("malformed-block.json")
    assert present == "True"
    assert counts[0] == 0


def test_suppressed_fixture_has_no_skills_block():
    present, counts = bucket_counts("suppressed.json")
    assert present == "False"
    assert counts[0] == 0


def test_repo_agents_fixture_reports_a_project_doc():
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "repo-agents.json").as_posix()}");'
        ' $r = Get-InstructionReport $t;'
        ' "{0} {1}" -f $r.BlockPresent, $r.ProjectDoc'
    )
    assert out.split() == ["True", "True"]


def test_flagged_fixture_reports_no_project_doc():
    # The both-ways proof that ProjectDoc tracks the repo file rather than
    # always reading true.
    out = run_functions(
        f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / "flagged.json").as_posix()}");'
        ' $r = Get-InstructionReport $t;'
        ' "{0} {1}" -f $r.BlockPresent, $r.ProjectDoc'
    )
    assert out.split() == ["True", "False"]


@pytest.mark.parametrize("path,workdir,expected", [
    ("C:/Users/x/.codex/plugins/cache/p/p/1.0/skills/s/SKILL.md", "C:/repo", "plugin-cache"),
    ("C:\\Users\\x\\.codex\\plugins\\cache\\p\\p\\1.0\\s\\SKILL.md", "C:/repo", "plugin-cache"),
    ("C:/repo/.agents/skills/planted/SKILL.md", "C:/repo", "repo"),
    ("C:/repo/sub/.agents/skills/deep/SKILL.md", "C:/repo", "repo"),
    ("C:/Users/x/.agents/skills/grilling/SKILL.md", "C:/repo", "home"),
    ("C:/Users/x/.codex/skills/.system/imagegen/SKILL.md", "C:/repo", "home"),
    # Fail closed. A path the classifier cannot place is NOT a benign
    # environment note.
    ("skills/relative/SKILL.md", "C:/repo", "unknown"),
    ("../escape/SKILL.md", "C:/repo", "unknown"),
    ("", "C:/repo", "unknown"),
    ("\\\\server\\share\\skills\\s\\SKILL.md", "C:/repo", "unknown"),
])
def test_scope_classification(path, workdir, expected):
    assert run_functions(f'Get-SkillScope "{path}" "{workdir}"') == expected


def test_repo_scope_wins_over_home_when_the_repo_is_inside_home():
    # A checkout under the user profile is the normal case on Windows. If
    # home matched first, a planted repo skill would be filed as an
    # environment note instead of stopping the gate.
    out = run_functions(
        'Get-SkillScope "C:/Users/x/Documents/repo/.agents/skills/s/SKILL.md"'
        ' "C:/Users/x/Documents/repo"'
    )
    assert out == "repo"


def test_a_sibling_directory_sharing_a_prefix_is_not_repo_scoped():
    out = run_functions(
        'Get-SkillScope "C:/w/repo-old/.agents/skills/s/SKILL.md" "C:/w/repo"'
    )
    assert out == "home"


def test_override_uses_forward_slashes_and_literal_strings():
    out = run_functions(
        '$e = @(@{Name="a";Path="C:\\Users\\x\\.agents\\skills\\a\\SKILL.md"});'
        ' New-SkillDisableOverride $e'
    )
    assert out.startswith("skills.config=[")
    assert "\\" not in out, (
        "backslashes make the value fail TOML parsing; codex then rejects"
        " it with `invalid type: string`"
    )
    assert '"' not in out, (
        "Windows PowerShell 5.1 STRIPS embedded double quotes when passing"
        " an argument to a native command, so a double-quoted value"
        " reached codex as {path=C:/...} and was rejected. TOML literal"
        " strings survive both hosts."
    )
    assert "path='C:/Users/x/.agents/skills/a/SKILL.md'" in out
    assert "enabled=false" in out


def test_a_path_containing_a_single_quote_is_refused():
    # A TOML literal string cannot escape its own delimiter, so there is
    # no representation for this path. Emitting a broken override would be
    # worse than stopping.
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         body + '\ntry { New-SkillDisableOverride'
                ' @(@{Name="a";Path="C:/x/o' + "'" + 'clock/SKILL.md"});'
                ' "NO-THROW" } catch { "THREW" }'],
        capture_output=True, text=True,
    )
    assert "THREW" in proc.stdout


def test_unparseable_json_raises_rather_than_returning_empty():
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         body + '\ntry { Get-PromptText "not json" ; "NO-THROW" }'
                ' catch { "THREW" }'],
        capture_output=True, text=True,
    )
    assert "THREW" in proc.stdout, (
        "an unreadable measurement must never return an empty one"
    )


def test_a_known_container_body_is_masked_before_the_unknown_scan():
    # The permitted global AGENTS.md is carried verbatim inside
    # <INSTRUCTIONS>, and a user's own file may contain a line like
    # <role>. Scanning the flattened text would call that a new outer
    # surface and block a review that is fine.
    out = run_functions(
        '$t = "<INSTRUCTIONS>`n<role>x</role>`n</INSTRUCTIONS>";'
        ' (Get-UnknownPromptBlock $t).Count'
    )
    assert out == "0"


@pytest.mark.parametrize("snippet,name", [
    ("<memories_instructions>`nx`n</memories_instructions>", "memories_instructions"),
    ("<agent-context>`nx`n</agent-context>", "agent-context"),
    ("<tool.state>`nx`n</tool.state>", "tool.state"),
    ("<ns:extra>`nx`n</ns:extra>", "ns:extra"),
    ('<beta_block version=`"2`">`nx`n</beta_block>', "beta_block"),
    ("<self_closing/>", "self_closing"),
    ("   <indented_block>`nx`n</indented_block>", "indented_block"),
])
def test_an_unrecognized_outer_block_is_found(snippet, name):
    out = run_functions(f'(Get-UnknownPromptBlock "{snippet}") -join ","')
    assert out == name


@pytest.mark.parametrize("snippet", [
    "<payload text>",
    "<recipient>",
    "Task name: <author>",
])
def test_an_unpaired_tag_in_prose_is_not_a_block(snippet):
    # An opening tag with no matching close is prose, not a surface. The
    # real prompt carries all three of these inside a fenced code block
    # that sits in no container, so requiring the PAIR is what keeps the
    # guard from blocking every genuine review.
    out = run_functions(f'(Get-UnknownPromptBlock "{snippet}").Count')
    assert out == "0"


def test_no_real_fixture_reports_an_unknown_block():
    # `<permissions instructions>` opens with a SPACE, so the grammar
    # reads its name as `permissions` while masking needs the full
    # literal. Two lists, or every real review blocks.
    for fixture in ("full.json", "flagged.json", "suppressed.json",
                    "repo-agents.json", "malformed-block.json"):
        out = run_functions(
            f'$t = Get-PromptText (Get-Content -Raw "{(FIXTURES / fixture).as_posix()}");'
            ' (Get-UnknownPromptBlock $t) -join ","'
        )
        assert out == "", f"{fixture} reported {out!r}"


# --- Task 2: the live CLI, driven through a stub ---------------------------


def run_probe(tmp_path, workdir, fixture, fixture2=None, exit_code=None,
              suppress=True):
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / fixture)
    env["PARALLAX_STUB_LOG"] = str(log)
    if fixture2:
        env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / fixture2)
    if exit_code is not None:
        env["PARALLAX_STUB_EXIT"] = str(exit_code)
    args = [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
            "-WorkDir", str(workdir), "-Json",
            "-CodexCommand", str(STUB)]
    if suppress:
        # -OverrideOut rides with -SuppressSkills everywhere. The probe
        # blocks the pair without it, so a helper that omitted it would
        # fail every suppression test before its own assertion ran.
        args += ["-SuppressSkills", "-OverrideOut",
                 str(tmp_path / "override.txt")]
    proc = subprocess.run(args, capture_output=True, text=True, env=env)
    calls = log.read_text().splitlines() if log.exists() else []
    return proc, calls


def probe_with(tmp_path, fixture_path, fixture2_path=None):
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(fixture_path)
    if fixture2_path:
        env["PARALLAX_STUB_FIXTURE2"] = str(fixture2_path)
    env["PARALLAX_STUB_LOG"] = str(tmp_path / "calls.log")
    return subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(tmp_path / "o.txt"), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)


def localized(tmp_path, fixture):
    """Rewrite the fabricated repo root to this test's tmp_path.

    The fixtures use the literal `C:/fixture/repo`, so no test depends on
    a path that exists only on the author's machine. The probe refuses a
    WorkDir that does not exist, which is what an absolute recorded path
    would have hit on CI.
    """
    out = tmp_path / fixture
    text = (FIXTURES / fixture).read_text(encoding="utf-8")
    out.write_text(text.replace("C:/fixture/repo", tmp_path.as_posix()),
                   encoding="utf-8")
    return out


def with_extra_text(tmp_path, name, base, extra):
    out = tmp_path / name
    doc = json.loads((FIXTURES / base).read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] += extra
    out.write_text(json.dumps(doc), encoding="utf-8")
    return out


def test_a_clean_machine_passes(tmp_path):
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json", "suppressed.json")
    assert proc.returncode == 0, proc.stdout
    report = json.loads(proc.stdout)
    assert report["status"] == "clean"
    assert report["skills_before"] == 29
    assert report["skills_after"] == 0


def test_the_standing_flags_are_on_every_call(tmp_path):
    proc, calls = run_probe(tmp_path, tmp_path, "flagged.json",
                            "suppressed.json")
    assert proc.returncode == 0, proc.stdout
    assert len(calls) == 2, calls
    for call in calls:
        args = json.loads(call)
        assert args.count("--disable") == 2
        assert "plugins" in args and "apps" in args


def test_a_surviving_plugin_cache_skill_blocks(tmp_path):
    # full.json still carries the 31 cache entries, which means the flag
    # did not take effect. That is a transport failure, not a note.
    proc, _ = run_probe(tmp_path, tmp_path, "full.json", "full.json")
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["status"] == "blocked"


def test_a_repo_scoped_skill_blocks(tmp_path):
    fixture = localized(tmp_path, "repo-agents.json")
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(fixture)
    env["PARALLAX_STUB_LOG"] = str(tmp_path / "calls.log")
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(tmp_path / "o.txt"), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 1
    assert "inside the reviewed tree" in json.loads(proc.stdout)["reason"]


def test_an_unplaceable_skill_path_blocks(tmp_path):
    fixture = tmp_path / "weird.json"
    text = (FIXTURES / "flagged.json").read_text(encoding="utf-8")
    fixture.write_text(
        text.replace("C:/fixture/home/.agents/skills/u0/SKILL.md",
                     "../escape/SKILL.md"), encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1
    assert "could not be placed" in json.loads(proc.stdout)["reason"]


def test_a_non_zero_codex_exit_blocks(tmp_path):
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json", exit_code=3)
    assert proc.returncode == 1
    assert "prompt-input exited" in json.loads(proc.stdout)["reason"]


def test_unreadable_output_blocks_rather_than_reading_as_empty(tmp_path):
    garbage = tmp_path / "garbage.json"
    garbage.write_text("<html>not json</html>")
    proc = probe_with(tmp_path, garbage)
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["status"] == "blocked"


def test_a_missing_skills_block_on_the_first_pass_blocks(tmp_path):
    # The plugin and apps blocks are ABSENT here, so nothing else explains
    # the missing skills block and the feature check cannot fire.
    proc, _ = run_probe(tmp_path, tmp_path, "missing-block-plugins-off.json",
                        "suppressed.json")
    assert proc.returncode == 1
    assert "skills block is missing" in json.loads(proc.stdout)["reason"]


def test_a_present_but_malformed_block_blocks_on_the_second_pass(tmp_path):
    # The false clean. The block is PRESENT and parses to zero entries, so
    # a count-only check reads it as a perfect suppression.
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json",
                        "malformed-block.json")
    assert proc.returncode == 1
    assert "still present" in json.loads(proc.stdout)["reason"]


def test_a_surviving_skill_after_suppression_blocks(tmp_path):
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json", "flagged.json")
    assert proc.returncode == 1
    assert "still present" in json.loads(proc.stdout)["reason"]


def test_the_global_agents_md_is_recorded_not_blocked(tmp_path):
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json", "suppressed.json")
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["global_agents_md"] is True, (
        "nothing available removes $CODEX_HOME/AGENTS.md; it is measured"
        " and recorded, never silently dropped from the report"
    )


def test_the_verified_override_is_written_out_for_the_dispatch(tmp_path):
    # THE handoff. The probe proves a zero produced by this exact value,
    # and the review dispatch must carry the same value.
    out = tmp_path / "override.txt"
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "flagged.json")
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(log)
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(out), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stdout
    raw = out.read_bytes()
    assert raw.startswith(b"skills.config=[")
    assert raw.count(b"enabled=false") == 29
    assert not raw.endswith(b"\n"), (
        "no trailing terminator: the second pass was run with the string,"
        " not with the string plus a line ending"
    )
    # BYTE identity against a structured capture of the second call's
    # arguments, not a substring match on a flattened log line.
    second_call = json.loads(log.read_text().splitlines()[1])
    passed = second_call[second_call.index("-c") + 1]
    assert passed.encode("utf-8") == raw

    report = json.loads(proc.stdout)
    assert report["override_file"] == str(out)
    assert report["override_sha256"] == hashlib.sha256(raw).hexdigest()


def test_a_non_ascii_skill_path_survives_the_round_trip(tmp_path):
    # ASCII encoding maps every non-ASCII character to '?', so the file
    # would differ from the value the second pass verified while the hash
    # authenticated the corrupted bytes.
    weird = "C:/fixture/home/.agents/skills/caf\u00e9-na\u00efve/SKILL.md"
    fixture = tmp_path / "nonascii.json"
    text = (FIXTURES / "flagged.json").read_text(encoding="utf-8")
    fixture.write_text(
        text.replace("C:/fixture/home/.agents/skills/u0/SKILL.md", weird),
        encoding="utf-8")
    out = tmp_path / "override.txt"
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(fixture)
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(log)
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(out), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stdout
    raw = out.read_bytes()
    assert weird.encode("utf-8") in raw
    assert b"?" not in raw, "a '?' means the encoder ate a character"
    assert raw.decode("utf-8")
    assert json.loads(proc.stdout)["override_sha256"] == \
        hashlib.sha256(raw).hexdigest()


def test_suppress_without_an_override_target_blocks(tmp_path):
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "flagged.json")
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(tmp_path / "calls.log")
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 1
    assert "OverrideOut" in json.loads(proc.stdout)["reason"]


def test_a_stale_override_artifact_is_refused_before_probing(tmp_path):
    stale = tmp_path / "override.txt"
    stale.write_text("skills.config=[from a previous debate]")
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "flagged.json")
    env["PARALLAX_STUB_LOG"] = str(log)
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(stale), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 2
    assert "already exists" in proc.stdout
    assert not log.exists(), "the check must come before the first codex call"
    assert stale.read_text() == "skills.config=[from a previous debate]"


def test_a_content_chunk_without_text_blocks(tmp_path):
    fixture = tmp_path / "odd-chunk.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"].append({"type": "input_image", "image_url": "x"})
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1
    assert "no text field" in json.loads(proc.stdout)["reason"]


def test_an_unknown_block_appearing_only_on_the_second_pass_blocks(tmp_path):
    second = with_extra_text(tmp_path, "second.json", "suppressed.json",
                             "\n<memories_instructions>\nx\n"
                             "</memories_instructions>\n")
    proc = probe_with(tmp_path, FIXTURES / "flagged.json", second)
    assert proc.returncode == 1
    assert "memories_instructions" in json.loads(proc.stdout)["reason"]


def test_the_apps_block_reappearing_on_the_second_pass_blocks(tmp_path):
    second = with_extra_text(tmp_path, "apps-again.json", "suppressed.json",
                             "\n<apps_instructions>\nx\n"
                             "</apps_instructions>\n")
    proc = probe_with(tmp_path, FIXTURES / "flagged.json", second)
    assert proc.returncode == 1
    assert "apps" in json.loads(proc.stdout)["reason"]


def test_a_long_skill_line_is_not_wrapped_on_the_way_in(tmp_path):
    # `Out-String` formats for a console and wraps at the host width,
    # which inserts newlines into the middle of a skill entry and breaks
    # the line-anchored parse. Every short fixture passed while the first
    # LIVE run failed, so this case exists to make the fixtures able to
    # catch it.
    long_desc = "A fixture skill with a deliberately long description. " * 8
    fixture = tmp_path / "long-lines.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "A fixture skill for tests.", long_desc)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout
    assert json.loads(proc.stdout)["skills_before"] == 29, (
        "a wrapped line loses its `(file: ...)` tail and the entry"
        " disappears from the count"
    )


def test_a_tag_inside_the_global_instructions_body_does_not_block(tmp_path):
    out = tmp_path / "role-in-instructions.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "<INSTRUCTIONS>", "<INSTRUCTIONS>\n<role>reviewer</role>\n")
    out.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, out, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout


# --- Mode-diff review findings, 2026-07-28. Four more false-clean paths
# --- that every earlier review missed.


def test_a_run_with_no_suppression_pass_is_never_clean(tmp_path):
    # THE false clean the whole script exists to forbid, sitting in its own
    # top level: without -SuppressSkills no second pass runs, yet the old
    # report said `clean` and exited 0 while 29 skills were still
    # advertised. A run that verified nothing must not look like one that
    # verified everything.
    proc, _ = run_probe(tmp_path, tmp_path, "flagged.json", suppress=False)
    assert proc.returncode == 1, proc.stdout
    report = json.loads(proc.stdout)
    assert report["status"] == "measured-only"
    assert report["skills_after"] == report["skills_before"] == 29
    assert report["override_file"] == ""
    assert report["override_sha256"] == ""


def test_a_present_but_empty_block_blocks_on_the_first_pass(tmp_path):
    # codex does not render an empty skills block, so PRESENT with zero
    # entries means the entry format changed and this parser can no longer
    # read it. Refusing it only on the second pass left the measurement-only
    # path reporting a zero it invented rather than measured.
    proc = probe_with(tmp_path, FIXTURES / "malformed-block.json")
    assert proc.returncode == 1, proc.stdout
    assert "no entry could be read" in proc.stdout


def test_a_skill_path_containing_a_parenthesis_survives_intact(tmp_path):
    # `C:/Program Files (x86)/...` is an ordinary Windows path. The old
    # capture stopped at the FIRST `)`, producing `C:/Program Files (x86`,
    # which still looks rooted - so it was filed as a harmless home note
    # and the generated disable entry named a file that does not exist.
    real = "C:/Program Files (x86)/codex/skills/vendor/SKILL.md"
    fixture = tmp_path / "parenthesis.json"
    text = (FIXTURES / "flagged.json").read_text(encoding="utf-8")
    fixture.write_text(
        text.replace("C:/fixture/home/.agents/skills/u0/SKILL.md", real),
        encoding="utf-8")
    out = tmp_path / "override.txt"
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(fixture)
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(log)
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(out), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stdout
    raw = out.read_text(encoding="utf-8")
    assert real in raw, (
        "the disable entry must name the whole path, or it disables nothing"
    )
    assert "C:/Program Files (x86'" not in raw


def test_a_skill_path_that_is_not_a_skill_file_is_unplaceable(tmp_path):
    # Fail closed on a shape this parser no longer describes. Every
    # advertised entry names a SKILL.md; anything else is a truncation or a
    # changed rendering, and belongs in the bucket that blocks.
    fixture = tmp_path / "not-a-skill.json"
    text = (FIXTURES / "flagged.json").read_text(encoding="utf-8")
    fixture.write_text(
        text.replace("C:/fixture/home/.agents/skills/u0/SKILL.md",
                     "C:/fixture/home/.agents/skills/u0/README.md"),
        encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1, proc.stdout
    assert "could not be placed" in json.loads(proc.stdout)["reason"]


def test_an_unwritable_override_target_is_never_clean(tmp_path):
    # Reproduced 2026-07-28 before the fix: with the artifact's parent
    # directory missing, the probe printed two PowerShell errors to stderr
    # and then reported `"status":"clean","override_file":null` with a real
    # hash, and exited 0. The caller was told the machine was verified and
    # handed an artifact path that does not exist.
    log = tmp_path / "calls.log"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "flagged.json")
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(log)
    missing = tmp_path / "nope" / "deeper" / "override.txt"
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(PROBE),
         "-WorkDir", str(tmp_path), "-Json", "-SuppressSkills",
         "-OverrideOut", str(missing), "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 1, proc.stdout
    report = json.loads(proc.stdout)
    assert report["status"] == "blocked"
    assert "could not be written" in report["reason"]


def attributed(tmp_path, tag):
    fixture = tmp_path / f"attributed-{tag}.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    text = doc[0]["content"][0]["text"]
    if f"<{tag}>" not in text:
        text += f'\n<{tag}>\nx\n</{tag}>\n'
    doc[0]["content"][0]["text"] = text.replace(
        f"<{tag}>", f'<{tag} version="2">', 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    return fixture


def test_an_attributed_instructions_block_blocks_as_missing(tmp_path):
    # INSTRUCTIONS is the one known container whose attributed form is
    # caught by an OLDER rule first: the exact literal is what the
    # instruction report looks for, so an attributed one reads as a
    # missing block. Different message, same direction, and both are
    # correct. Named separately rather than folded into a looser
    # assertion, so neither rule can be deleted unnoticed.
    proc = probe_with(tmp_path, attributed(tmp_path, "INSTRUCTIONS"))
    assert proc.returncode == 1, proc.stdout
    assert "block is missing" in json.loads(proc.stdout)["reason"]


@pytest.mark.parametrize("tag", [
    "skills_instructions", "apps_instructions", "plugins_instructions",
    "recommended_plugins", "environment_context", "multi_agent_mode",
])
def test_an_attributed_known_block_blocks(tmp_path, tag):
    # A known NAME is not enough. Every dedicated parser matches an exact
    # literal, so `<skills_instructions version="2">` is invisible to them,
    # and the unknown-block guard skipped it for having a known name.
    # Reproduced 2026-07-28: a second pass carrying all 29 entries under
    # that tag reported skills_after 0, status clean, exit 0.
    proc = probe_with(tmp_path, attributed(tmp_path, tag))
    assert proc.returncode == 1, proc.stdout
    assert "exact form this parser reads" in json.loads(proc.stdout)["reason"]


def test_an_attributed_block_on_the_second_pass_blocks(tmp_path):
    # THE reproduced false clean, in its original shape: the suppression
    # pass carries every skill back under an attributed tag, and the old
    # code called that absence and reported skills_after 0 with exit 0.
    proc = probe_with(tmp_path, FIXTURES / "flagged.json",
                      attributed(tmp_path, "skills_instructions"))
    assert proc.returncode == 1, proc.stdout
    assert "exact form this parser reads" in json.loads(proc.stdout)["reason"]


def test_the_permissions_container_keeps_its_legitimate_space(tmp_path):
    # The guard above compares WHOLE literals rather than testing for the
    # presence of attributes, because `<permissions instructions>` is a
    # real container whose name parses as `permissions` with ` instructions`
    # read as an attribute. An attribute test would block every real review.
    proc = probe_with(tmp_path, FIXTURES / "flagged.json",
                      FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout


def test_two_entries_on_one_line_block(tmp_path):
    # The greedy path capture reads two rendered entries on ONE line as a
    # single entry with a merged path, so the FIRST measurement is wrong
    # and no later suppression check repairs it.
    fixture = tmp_path / "merged.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "- userskill1: A fixture skill for tests."
        " (file: C:/fixture/home/.agents/skills/u1/SKILL.md)",
        "- userskill1: A fixture skill for tests."
        " (file: C:/fixture/home/.agents/skills/u1/SKILL.md)"
        " - userskill1b: Another. (file:"
        " C:/fixture/home/.agents/skills/u1b/SKILL.md)", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1, proc.stdout
    assert "whole entry grammar" in json.loads(proc.stdout)["reason"]


def test_an_inline_attributed_known_block_blocks(tmp_path):
    # Round 2's rule was line-anchored, so a known tag with text before it
    # on the line escaped both the exact parsers and the general scan.
    # Reproduced 2026-07-28: a second pass carrying all 29 entries under
    # `prefix <skills_instructions version="2">` reported skills_after 0,
    # status clean, exit 0.
    second = tmp_path / "inline.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "<skills_instructions>", 'prefix <skills_instructions version="2">', 1)
    second.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, FIXTURES / "flagged.json", second)
    assert proc.returncode == 1, proc.stdout
    assert "exact form this parser reads" in json.loads(proc.stdout)["reason"]


def test_a_known_literal_quoted_in_the_global_body_does_not_block(tmp_path):
    # The user's own AGENTS.md is carried verbatim inside <INSTRUCTIONS>,
    # and a house rule may name a marker in prose. With INSTRUCTIONS masked
    # AFTER the other containers, an unpaired `<skills_instructions>` in
    # that prose read as an unterminated container of that name and blocked
    # a legitimate review. Reproduced 2026-07-28; the fix is masking the
    # user-authored container first.
    fixture = tmp_path / "house-rule.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "<INSTRUCTIONS>",
        "<INSTRUCTIONS>\nHouse rule: never emit a `<skills_instructions>`"
        " marker.\n", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout


def test_a_description_mentioning_the_file_marker_is_not_malformed(tmp_path):
    # Skill descriptions are free text. Counting `(file: ` and demanding
    # exactly one rejected a legitimate entry; the LAST marker on the line
    # is the path delimiter.
    fixture = tmp_path / "chatty.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "- userskill2: A fixture skill for tests.",
        "- userskill2: Use when a log line reads (file: something).", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout
    raw = (tmp_path / "o.txt").read_text(encoding="utf-8")
    assert "C:/fixture/home/.agents/skills/u2/SKILL.md" in raw, (
        "the delimiter is the LAST marker, so the real path still wins"
    )


@pytest.mark.parametrize("pass_no", [1, 2])
def test_a_case_variant_known_block_blocks(tmp_path, pass_no):
    # Two rules disagreed about case. The anywhere scan was case-SENSITIVE
    # and missed `<SKILLS_INSTRUCTIONS version="2">`, while the general
    # scan skipped it because PowerShell's `-contains` is
    # case-INSENSITIVE and called the name known. Confirmed mechanically
    # 2026-07-28: for @("skills_instructions"), `-contains
    # "SKILLS_INSTRUCTIONS"` is True and `-ccontains` is False. Name
    # recognition is now loose and the literal allowlist is strict.
    variant = tmp_path / f"case-{pass_no}.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "<skills_instructions>", '<SKILLS_INSTRUCTIONS version="2">', 1)
    variant.write_text(json.dumps(doc), encoding="utf-8")
    if pass_no == 1:
        proc = probe_with(tmp_path, variant)
    else:
        proc = probe_with(tmp_path, FIXTURES / "flagged.json", variant)
    assert proc.returncode == 1, proc.stdout
    assert "exact form this parser reads" in json.loads(proc.stdout)["reason"]


def test_a_quoted_closing_marker_in_the_global_body_does_not_block(tmp_path):
    # The closing-literal counterpart of the opening-literal finding. A
    # global AGENTS.md that QUOTES `</INSTRUCTIONS>` ended the masked span
    # early, leaving the rest of the user's own file to be scanned as
    # outer structure - and the paired tag after it then blocked a
    # legitimate review. Mode-diff round 4, 2026-07-28.
    fixture = tmp_path / "quoted-close.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "<INSTRUCTIONS>",
        "<INSTRUCTIONS>\nHouse rule: never write `</INSTRUCTIONS>` by"
        " hand.\n<role>reviewer</role>\n", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout


def test_a_description_with_a_paren_then_a_dash_is_not_malformed(tmp_path):
    # The joined-entry detector matched any close paren followed by
    # bullet-like prose, so `Use when output is (done) - next: retry.`
    # was marked malformed. It must match a COMPLETE earlier entry.
    fixture = tmp_path / "dashy.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "- userskill3: A fixture skill for tests.",
        "- userskill3: Use when output is (done) - next: retry.", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture, FIXTURES / "suppressed.json")
    assert proc.returncode == 0, proc.stdout
    raw = (tmp_path / "o.txt").read_text(encoding="utf-8")
    assert "C:/fixture/home/.agents/skills/u3/SKILL.md" in raw


def test_a_joined_entry_whose_path_has_parentheses_still_blocks(tmp_path):
    # And the narrowed detector must still catch the real shape, including
    # when the first entry's path carries its own parentheses - which is
    # why the marker match is non-greedy up to the SKILL.md anchor.
    fixture = tmp_path / "joined-parens.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = doc[0]["content"][0]["text"].replace(
        "- userskill4: A fixture skill for tests."
        " (file: C:/fixture/home/.agents/skills/u4/SKILL.md)",
        "- userskill4: A fixture skill for tests."
        " (file: C:/Program Files (x86)/skills/u4/SKILL.md)"
        " - userskill4b: Another."
        " (file: C:/fixture/home/.agents/skills/u4b/SKILL.md)", 1)
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1, proc.stdout
    assert "whole entry grammar" in json.loads(proc.stdout)["reason"]


def test_an_unterminated_known_container_blocks(tmp_path):
    # Masking an unclosed container to end-of-prompt hid every later block
    # from the unknown-surface scan, so one malformed container near the
    # top silently disabled the whole guard.
    fixture = tmp_path / "unterminated.json"
    doc = json.loads((FIXTURES / "flagged.json").read_text(encoding="utf-8"))
    doc[0]["content"][0]["text"] = (
        doc[0]["content"][0]["text"].replace("</INSTRUCTIONS>", "")
        + "\n<memories_instructions>\nx\n</memories_instructions>\n")
    fixture.write_text(json.dumps(doc), encoding="utf-8")
    proc = probe_with(tmp_path, fixture)
    assert proc.returncode == 1, proc.stdout
    assert "never closes" in proc.stdout
