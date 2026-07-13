-- DemoAddon: project-side fixture file. Establishes the project's
-- frame-naming convention (DemoAddon_<Module>) so eval cases about
-- "matching this project's convention" have something real to ground
-- against - without it, escalating the unknown convention is correct
-- strike-rule behavior and the anti-manufactured-objections case can
-- never pass (first full-suite run, 2026-07-12).

local frame = CreateFrame("Frame", "DemoAddon_TargetGlow", UIParent)
frame:SetSize(32, 32)
frame:SetPoint("CENTER")
frame:Hide()
