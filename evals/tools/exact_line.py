"""Shared oracle for the frozen "exactly one nonempty line" output contract.

Several eval call sites parse subprocess or file output that the contract
promises is exactly one line: a validator's classification, a builder's
custody line, a login wrapper's `-VerdictOut` file, or a measured type
report. The frozen caller rule is that leading, interior, and extra
trailing blank lines are all REJECTED. "Discard blank lines, then require
one survivor" is a different, weaker check: it silently accepts a reply
with a blank-line separator that the contract requires to fail. Three
independent sweeps for that idiom each missed at least one instance before
this one shared implementation replaced all nine.

accept_exactly_one_nonempty_line() is that one implementation, using the
same anchored regex as tools/new-kimi-lane-home.ps1's `singleLine` pattern:
``\\A([^\\r\\n]+)(\\r\\n|\\n)?\\Z``. ``\\A``/``\\Z`` anchor to the start and
end of the whole string, never to a line boundary the way ``^``/``$`` do -
``$`` matches immediately before a trailing newline even outside multiline
mode, so a pattern built on ``^``/``$`` would silently accept a second
trailing blank line that this one rejects.
"""
import re

_SINGLE_LINE = re.compile(r"\A([^\r\n]+)(\r\n|\n)?\Z")


def accept_exactly_one_nonempty_line(text):
    """Return the single nonempty line in `text`, or None if `text` is not
    exactly one nonempty line optionally followed by exactly one line
    terminator (LF or CRLF). A leading blank line, an interior blank line,
    or more than one trailing terminator are all rejected outright - never
    discarded and then recounted."""
    match = _SINGLE_LINE.match(text)
    return match.group(1) if match else None
