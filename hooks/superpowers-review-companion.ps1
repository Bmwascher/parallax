# PostToolUse hook (Task|Agent), two checks, both warn and never block.
#
# 1. Build lane (backlog item 110): every frozen-plan task is built by
#    parallax:flash-implementer unless the plan, or a consent the session
#    recorded in the SDD ledger, names another lane for THAT task. The
#    evidence is a `Lane:` line in the dispatch prompt carrying the
#    dispatched subagent_type (references/frozen-plan-format.md). An
#    implementer dispatch IS the build, so no other state is consulted;
#    a payload with no subagent_type falls through.
# 2. Review companion: when the superpowers requesting-code-review skill
#    dispatches its code-reviewer subagent, inject a reminder to run the
#    multi-model-verify skill's diff mode on the same commit range.
#    Fingerprint: the rendered code-reviewer.md template (superpowers
#    6.3.0) always contains the literals "Senior Code Reviewer" and "Git
#    Range to Review"; both must be present. Re-check the template after
#    superpowers updates - if the fingerprint rots, this check silently
#    stops firing (fails open, never blocks).
#
# Output contract: silent exit 0 = nothing to add; JSON additionalContext =
# non-blocking context injection.

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
} catch {
    exit 0
}

# Echo the INCOMING event name: this script serves PostToolUse and
# PostToolUseFailure, and the output contract requires hookSpecificOutput
# to name the actual event (Sol holistic MAJOR, 2026-07-13).
$eventName = $payload.hook_event_name
if (-not $eventName) { $eventName = 'PostToolUse' }

$subagent = [string]$payload.tool_input.subagent_type
if ($subagent -and $subagent -imatch 'implementer' -and $subagent -cne 'parallax:flash-implementer') {
    # The field is written as `**Lane:** <agent>` on ONE line in the
    # frozen task text; leading list or emphasis markers are tolerated,
    # nothing crosses a line break, and the agent name is matched exactly
    # and must end at a blank or the end of that line (Astra plan R1,
    # finding 4: `\s*` crossed a newline and `(?![\w-])` accepted
    # `parallax:escalation-implementer:other`).
    $laneLine = '(?m)^[ \t*_>-]*Lane:\**[ \t]*' + [regex]::Escape($subagent) + '(?=[ \t]|\r?$)'
    $promptText = [string]$payload.tool_input.prompt
    if ($promptText -cmatch $laneLine) { exit 0 }
    $warn = @{
        hookSpecificOutput = @{
            hookEventName     = $eventName
            additionalContext = ("parallax: this dispatch went to $subagent, and the " +
                "build lane for every frozen-plan task is parallax:flash-implementer. " +
                "A task the plan routes elsewhere carries the field " +
                "'**Lane:** $subagent' in its task text; a consented reroute of a " +
                "task the Flash lane blocked carries the SDD ledger's line " +
                "'**Lane:** $subagent (consented reroute, <ledger path>)'. This " +
                "prompt carried neither. Either add the line from the plan or the " +
                "ledger, or route the task to parallax:flash-implementer. " +
                "Measured 2026-09-13: 122 of 128 build dispatches in five days went " +
                "to a lane the plan never named (backlog item 110).")
        }
    }
    $warn | ConvertTo-Json -Compress -Depth 5
    exit 0
}

$prompt = $payload.tool_input.prompt
if (-not $prompt) { exit 0 }

$hasReviewer = $prompt -match 'Senior Code Reviewer'
$hasRange = $prompt -match 'Git Range to Review'
if (-not $hasReviewer -and -not $hasRange) { exit 0 }

if ($hasReviewer -ne $hasRange) {
    # Exactly one fingerprint literal matched: this looks like the
    # superpowers code-reviewer dispatch after a template change - the
    # diff gate may be rotting. Warn NOW instead of failing open until
    # the weekly drift check notices (Sol holistic improvement 3).
    $warn = @{
        hookSpecificOutput = @{
            hookEventName     = $eventName
            additionalContext = ("parallax: this dispatch matches only PART of the " +
                "superpowers code-reviewer fingerprint - the template may have " +
                "changed and the multi-model-verify diff gate may be inert. Run " +
                "tools/check-drift.ps1 and re-fingerprint " +
                "hooks/superpowers-review-companion.ps1. If this was a final " +
                "pre-merge code review, run multi-model-verify mode diff manually " +
                "on the review's base/head range.")
        }
    }
    $warn | ConvertTo-Json -Compress -Depth 5
    exit 0
}

$base = ''
$head = ''
if ($prompt -match '\*\*Base:\*\*\s*([^\s`\r\n]+)') { $base = $Matches[1] }
if ($prompt -match '\*\*Head:\*\*\s*([^\s`\r\n]+)') { $head = $Matches[1] }
$range = if ($base -and $head) { "base $base head $head" } else { 'the same base/head range the review used' }

$context = "A superpowers code review just ran on this branch ($range). " +
    "If that was the final pre-merge review (requesting-code-review), also run " +
    "the multi-model-verify skill in mode diff on the SAME range now - " +
    "cross-model spec-fidelity and port-fidelity verification is a separate " +
    "gate from single-model code review. If it was an intermediate per-task " +
    "review, defer multi-model-verify until the final review. Skip only if " +
    "mode diff already ran for this exact range."

$out = @{
    hookSpecificOutput = @{
        hookEventName     = $eventName
        additionalContext = $context
    }
}
$out | ConvertTo-Json -Compress -Depth 5
exit 0
