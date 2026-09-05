# Task 5 timing script output, KitnEssentials, PowerShell 7, 2026-09-05

Copied verbatim from the SDD report (git-ignored) so the numbers in the design's measured section have a retained source.

```text
Full printed output:

```
old build: 137 s, exit 1, built=True
BLOCKED: no client measurement was made (-SkipProbe), so this mirror is not cleared for dispatch and carries no verified override
new build: 87 s, exit 1, built=True
BLOCKED: no client measurement was made (-SkipProbe), so this mirror is not cleared for dispatch and carries no verified override
  .wow-api-reference -> C:\Users\Brandon\Documents\WoW-Dev\wow-api-reference
  .claude\skills\comment-cleanup -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\comment-cleanup
  .claude\skills\lua-quality -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\lua-quality
  .claude\skills\secret-value-diagnose -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\secret-value-diagnose
  .claude\skills\wow-addon-libraries -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\wow-addon-libraries
  .claude\skills\wow-lua-patterns -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\wow-lua-patterns
  .claude\skills\wow-media -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\wow-media
  .claude\skills\wow-midnight-api -> C:\Users\Brandon\Documents\KitnDev\.claude\skills\wow-midnight-api
new link .wow-api-reference: 14884 files through the mirror, 14884 in the target, identical names and hashes: True
new link .claude\skills\comment-cleanup: 1 files through the mirror, 1 in the target, identical names and hashes: True
new link .claude\skills\lua-quality: 1 files through the mirror, 1 in the target, identical names and hashes: True
new link .claude\skills\secret-value-diagnose: 1 files through the mirror, 1 in the target, identical names and hashes: True
new link .claude\skills\wow-addon-libraries: 5 files through the mirror, 5 in the target, identical names and hashes: True
new link .claude\skills\wow-lua-patterns: 1 files through the mirror, 1 in the target, identical names and hashes: True
new link .claude\skills\wow-media: 4 files through the mirror, 4 in the target, identical names and hashes: True
new link .claude\skills\wow-midnight-api: 2 files through the mirror, 2 in the target, identical names and hashes: True
```

No "links overlap" refusal fired (the second `.wow-api-reference` under
```

Confirming count on the reference checkout after cleanup: 14884.
