# review-tree-removal.ps1 - the one removal path for a review tree, and
# the directory-link guard both callers run before it.
#
# DOT-SOURCED, never run:
#   . (Join-Path $PSScriptRoot "review-tree-removal.ps1")
# from tools/new-review-mirror.ps1 (the -Force rebuild, backlog item 98)
# and tools/write-attestation.ps1 (the reap after a terminal verdict,
# backlog item 106). It defines functions and executes nothing else, so
# dot-sourcing it has no effect until a caller calls one.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.

function Test-PathOrAncestorIsLink($path) {
    # The path itself, then each existing ancestor up to the drive root:
    # is any of them a reparse point? Attributes are read directly
    # rather than after a Test-Path, because a DANGLING junction is a
    # reparse point Test-Path may report as absent; a missing entry is
    # the one condition that skips a level, and it is recognised by the
    # exception type, never by a false from a helper. Returns the
    # offending path or $null.
    $probe = ([string]$path).TrimEnd("\", "/")
    while ($probe -and -not [string]::IsNullOrEmpty([System.IO.Path]::GetFileName($probe))) {
        $pa = 0
        $missing = $false
        try {
            $pa = [int][System.IO.File]::GetAttributes($probe)
        } catch [System.IO.FileNotFoundException] {
            $missing = $true
        } catch [System.IO.DirectoryNotFoundException] {
            $missing = $true
        } catch {
            Write-Output ("ERROR: " + $probe + " could not be read while" +
                " checking for a directory link: " + $_.Exception.Message)
            exit 2
        }
        if (-not $missing -and (($pa -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            return $probe
        }
        $probe = [System.IO.Path]::GetDirectoryName($probe)
    }
    return $null
}

function Remove-ReviewTreeEntries($dir, $depth) {
    # Empties $dir in post-order. Returns $null when every entry beneath
    # it is gone, else the reason, which names the entry that stopped it.
    #
    # NEVER THROUGH A LINK. A directory link is removed with the
    # non-recursive Directory.Delete and a file link with File.Delete;
    # both remove the link and never its target. Measured 2026-09-13 on
    # Windows PowerShell 5.1 and PowerShell 7, intact and dangling. An
    # ordinary directory is emptied by this walk and then removed with
    # the same non-recursive Directory.Delete, which throws when
    # anything survived, so a partial removal cannot read as a whole
    # one. An ordinary file has its read-only bit cleared first, because
    # git marks its object files read-only and File.Delete refuses them
    # as they are (measured the same day).
    if ($depth -gt 128) {
        return ($dir + " sits deeper than 128 levels; the walk stops" +
            " rather than assume the tree ends")
    }
    $entries = $null
    try {
        $entries = [System.IO.Directory]::GetFileSystemEntries($dir)
    } catch {
        return ($dir + " could not be listed: " + $_.Exception.Message)
    }
    foreach ($entry in $entries) {
        $ea = 0
        try {
            $ea = [int][System.IO.File]::GetAttributes($entry)
        } catch {
            return ($entry + " could not be examined: " + $_.Exception.Message)
        }
        $isDir = (($ea -band [int][System.IO.FileAttributes]::Directory) -ne 0)
        $isLink = (($ea -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0)
        try {
            if ($isLink) {
                if ($isDir) {
                    [System.IO.Directory]::Delete($entry)
                } else {
                    [System.IO.File]::Delete($entry)
                }
            } elseif ($isDir) {
                $inner = Remove-ReviewTreeEntries $entry ($depth + 1)
                if ($null -ne $inner) { return $inner }
                # robocopy /DCOPY:DA carries a read-only directory into the mirror; Directory.Delete refuses it as it is (measured 2026-09-13, both hosts).
                if (($ea -band [int][System.IO.FileAttributes]::ReadOnly) -ne 0) {
                    [System.IO.File]::SetAttributes($entry, [System.IO.FileAttributes]::Directory)
                }
                [System.IO.Directory]::Delete($entry)
            } else {
                if (($ea -band [int][System.IO.FileAttributes]::ReadOnly) -ne 0) {
                    [System.IO.File]::SetAttributes($entry, [System.IO.FileAttributes]::Normal)
                }
                [System.IO.File]::Delete($entry)
            }
        } catch {
            return ($entry + " could not be removed: " + $_.Exception.Message)
        }
    }
    return $null
}

function Remove-ReviewTree($root) {
    # Removes the tree at $root. Returns @{ Ok = $true }, or
    # @{ Ok = $false; Reason = <text> } the moment any step fails, with
    # the entry that failed named in the reason. It never exits the
    # caller and never writes output, so the caller decides what a
    # failure costs: the mirror tool refuses to build, the emitter
    # reports a written attestation with an unreaped tree.
    #
    # The root's OWN guards are here; the caller runs the ancestor-link
    # guard (Test-PathOrAncestorIsLink) and its overlap comparisons
    # before ever reaching this, because those are refusals that must
    # cost nothing, while this runs after the emitter has written.
    $full = $null
    try {
        $full = [System.IO.Path]::GetFullPath([string]$root).TrimEnd("\")
    } catch {
        return @{ Ok = $false; Reason = ("the path could not be resolved (" +
            $root + "): " + $_.Exception.Message) }
    }
    $pathRoot = $null
    try {
        $pathRoot = [System.IO.Path]::GetPathRoot($full)
    } catch {
        return @{ Ok = $false; Reason = ("the path has no root (" + $full +
            "): " + $_.Exception.Message) }
    }
    if ((-not $pathRoot) -or ($full.Length -le ([string]$pathRoot).TrimEnd("\").Length)) {
        return @{ Ok = $false; Reason = ($full + " is a filesystem root and" +
            " is never removed") }
    }
    $attr = 0
    try {
        $attr = [int][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        return @{ Ok = $false; Reason = ($full + " does not exist") }
    } catch [System.IO.DirectoryNotFoundException] {
        return @{ Ok = $false; Reason = ($full + " does not exist") }
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be examined: " +
            $_.Exception.Message) }
    }
    if (($attr -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        return @{ Ok = $false; Reason = ($full + " is a link, and a tree is" +
            " never removed through a link") }
    }
    if (($attr -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        return @{ Ok = $false; Reason = ($full + " is a file, not a tree") }
    }
    $failure = Remove-ReviewTreeEntries $full 0
    if ($null -ne $failure) {
        return @{ Ok = $false; Reason = $failure }
    }
    try {
        # robocopy /DCOPY:DA carries a read-only directory into the mirror; Directory.Delete refuses it as it is (measured 2026-09-13, both hosts).
        if (($attr -band [int][System.IO.FileAttributes]::ReadOnly) -ne 0) {
            [System.IO.File]::SetAttributes($full, [System.IO.FileAttributes]::Directory)
        }
        [System.IO.Directory]::Delete($full)
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be removed: " +
            $_.Exception.Message) }
    }
    # THE POSTCONDITION, read back rather than inferred from the absence
    # of an exception. Item 98 is a removal that checked nothing after.
    try {
        [void][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        return @{ Ok = $true }
    } catch [System.IO.DirectoryNotFoundException] {
        return @{ Ok = $true }
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be re-examined" +
            " after removal: " + $_.Exception.Message) }
    }
    return @{ Ok = $false; Reason = ($full + " still exists after removal") }
}
