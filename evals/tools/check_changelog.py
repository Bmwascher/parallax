#!/usr/bin/env python3
"""check_changelog.py - tie CHANGELOG.md to the plugin version, and to
Simplified Technical English.

Two readers, one rule. CI (Tier 1d) runs it bare and fails the push when
the newest changelog section is not the version in
`.claude-plugin/plugin.json`, so a bump without notes is caught on the
branch, before it reaches main and a release. The release workflow runs
it with `--version X --print` and publishes what it prints as the
release body, so the notes on a release page are always the section the
checker approved and never a hand-typed second copy.

The file shape is deliberately narrow. Each section is:

    ## vX.Y.Z (YYYY-MM-DD)
    <body, at least one non-blank line, up to the next `## ` heading>

Newest first. The `## ` prefix is the ONLY section delimiter: `###`
headings inside a body belong to that body. A version that appears
twice, a heading without a date, or a body with nothing in it is a
failure, not a warning - every one of those has produced an empty or
wrong release page somewhere.

The whole file is also passed through `ste_lint.py` beside this one,
the mechanically checkable part of ASD-STE100; its findings fail the
check the same way, so an entry that a release would publish is one
that the STE checker has passed. `--no-ste` skips that pass, for a
caller that only wants the version tie.

Exit codes: 0 the checked section exists and is non-empty (and, bare, the
newest one names the plugin version); 1 any rule failure; 2 a file that
cannot be read or parsed at all. Python 3 stdlib only.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
PLUGIN_JSON_PATH = ".claude-plugin/plugin.json"
HEADING_RE = re.compile(r"^## v(\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)\s*$")
ANY_H2_RE = re.compile(r"^## ")


def parse_sections(text):
    """Return ([(version, date, body_lines)...] in file order, [errors])."""
    sections = []
    errors = []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        if ANY_H2_RE.match(line):
            match = HEADING_RE.match(line)
            if not match:
                errors.append("line %d: heading is not '## vX.Y.Z (YYYY-MM-DD)': %r"
                              % (number, line))
                current = None
                continue
            current = (match.group(1), match.group(2), [])
            sections.append(current)
        elif current is not None:
            current[2].append(line)
    seen = set()
    for version, _date, body in sections:
        if version in seen:
            errors.append("version %s has more than one section" % version)
        seen.add(version)
        if not any(ln.strip() for ln in body):
            errors.append("version %s: section body is empty" % version)
    return sections, errors


def section_body(sections, version):
    for found, _date, body in sections:
        if found == version:
            return "\n".join(body).strip("\n") + "\n"
    return None


def _load_ste_lint():
    path = Path(__file__).resolve().parent / "ste_lint.py"
    spec = importlib.util.spec_from_file_location("ste_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ste_findings(text):
    """Every STE finding for the changelog text, as strings."""
    ste = _load_ste_lint()
    return [str(f) for f in ste.lint_text(text, ste.load_allowlist())]


def plugin_version(repo_root):
    with open(repo_root / PLUGIN_JSON_PATH, encoding="utf-8") as handle:
        return json.load(handle)["version"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--version", default=None,
                        help="check this section instead of the newest; "
                             "with --print, print its body")
    parser.add_argument("--print", dest="print_body", action="store_true",
                        help="print the checked section's body to stdout")
    parser.add_argument("--no-ste", dest="ste", action="store_false",
                        help="skip the Simplified Technical English pass")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)

    try:
        text = (repo_root / CHANGELOG_PATH).read_text(encoding="utf-8")
    except OSError as exc:
        print("changelog: cannot read %s: %s" % (CHANGELOG_PATH, exc), file=sys.stderr)
        return 2
    sections, errors = parse_sections(text)
    if not sections and not errors:
        errors.append("no '## vX.Y.Z (YYYY-MM-DD)' section at all")

    if args.version is not None:
        wanted = args.version
    else:
        try:
            wanted = plugin_version(repo_root)
        except (OSError, ValueError, KeyError) as exc:
            print("changelog: cannot read the version from %s: %s"
                  % (PLUGIN_JSON_PATH, exc), file=sys.stderr)
            return 2
        if sections and sections[0][0] != wanted:
            errors.append("newest section is v%s but %s says %s"
                          % (sections[0][0], PLUGIN_JSON_PATH, wanted))

    body = section_body(sections, wanted)
    if body is None:
        errors.append("no section for v%s" % wanted)
    if args.ste:
        errors.extend("STE: %s" % finding for finding in ste_findings(text))

    if errors:
        for error in errors:
            print("changelog: %s" % error, file=sys.stderr)
        return 1
    if args.print_body:
        sys.stdout.write(body)
    else:
        print("changelog: v%s section present (%s)" % (wanted, CHANGELOG_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
