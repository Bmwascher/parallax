-- DemoWidget: synthetic reference addon for crosscheck behavioral evals.
-- Deliberately small and boring: a frame that shows the player's target
-- name and hides out of combat. Contains one quirk on purpose (the
-- OnUpdate runs unconditionally) so debates have something real to find.

local frame = CreateFrame("Frame", "DemoWidgetFrame", UIParent)
frame:SetSize(160, 24)
frame:SetPoint("CENTER", 0, -180)

local text = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
text:SetAllPoints(frame)

local elapsed = 0
frame:SetScript("OnUpdate", function(_, dt)
    elapsed = elapsed + dt
    if elapsed < 0.2 then return end
    elapsed = 0
    if UnitExists("target") then
        text:SetText(UnitName("target"))
    else
        text:SetText("")
    end
end)

frame:RegisterEvent("PLAYER_REGEN_ENABLED")
frame:RegisterEvent("PLAYER_REGEN_DISABLED")
frame:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_REGEN_DISABLED" then
        frame:Show()
    else
        frame:Hide()
    end
end)
