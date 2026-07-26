---
colors:
  primary: "#4F46E5"
  primaryHover: "#4338CA"
  background: "#0B0F19"
  surface: "#131A2A"
  surfaceRaised: "#1B2436"
  border: "#2A3450"
  textPrimary: "#F1F4FA"
  textSecondary: "#9BA6C0"
  critical: "#F0506E"
  criticalBg: "#2A1220"
  correction: "#F5A623"
  correctionBg: "#2B2010"
  partial: "#3AB6D8"
  partialBg: "#0F2530"
  success: "#33C481"
  successBg: "#0F2B20"

typography:
  display:
    fontFamily: "'Sora', 'Segoe UI', sans-serif"
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: 1.15
  heading:
    fontFamily: "'Sora', 'Segoe UI', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "'Inter', 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  caption:
    fontFamily: "'Inter', 'Segoe UI', sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.01em"
  mono:
    fontFamily: "'JetBrains Mono', 'Consolas', monospace"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.5

rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
  pill: "999px"

spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"

components:
  primaryButton:
    backgroundColor: primary
    textColor: "#FFFFFF"
    typography: heading
    rounded: md
    padding: "14px 24px"
  primaryButtonHover:
    backgroundColor: primaryHover
  card:
    backgroundColor: surface
    textColor: textPrimary
    rounded: lg
    padding: "20px"
  criticalCard:
    backgroundColor: criticalBg
    textColor: textPrimary
    rounded: md
    padding: "16px"
  correctionCard:
    backgroundColor: correctionBg
    textColor: textPrimary
    rounded: md
    padding: "16px"
  partialCard:
    backgroundColor: partialBg
    textColor: textPrimary
    rounded: md
    padding: "16px"
  successCard:
    backgroundColor: successBg
    textColor: textPrimary
    rounded: md
    padding: "16px"
  metricTile:
    backgroundColor: surfaceRaised
    textColor: textPrimary
    typography: display
    rounded: lg
    padding: "20px"
---

## Overview

CatchUp AI's visual identity should feel like a calm, focused study tool used late at night by a
student trying to recover a missed lecture — not a corporate dashboard. The design leans into a
dark, low-glare "study desk at night" surface with a single confident indigo accent, and reserves
saturated color almost entirely for the app's core mechanic: the four-tier gap severity system
(critical / correction / partial / verified). Everything else stays quiet so those four signal
colors keep their meaning.

## Colors

The background is a near-black navy (`#0B0F19`), not pure black, so white text and colored cards
don't vibrate against it. Two lighter surface tones (`surface`, `surfaceRaised`) create depth
between the page, cards, and metric tiles without needing heavy borders or shadows.

`primary` (indigo `#4F46E5`) is used only for the main call-to-action button, active states, and
links — it should never appear in more than one or two places on screen at once, so it keeps
weight as "the thing to click."

The four semantic colors map directly to the existing report sections and must not be reused for
anything else:
- **critical** (rose) — missing high-importance content
- **correction** (amber) — factual conflicts between notes and board
- **partial** (cyan) — partially-covered content
- **success** (green) — verified, grounded notes

Each has a paired `*Bg` tone at ~10% perceived intensity against the dark background, used as a
card fill so the colored text/icon on top stays the strongest signal, not a jarring solid block.

## Typography

**Sora** for display and headings gives the app a bit of geometric, modern character without
tipping into a "tech startup" feel. **Inter** for body and captions is the workhorse — legible at
small sizes for dense report content. **JetBrains Mono** is reserved for literal quoted content
(the exact text a student wrote vs. what the board said), so factual quotes are visually
distinct from Gemma's prose.

All three are widely available on Google Fonts; fall back to system sans-serif/monospace stacks
if offline.

## Layout

Two-column upload layout stays (board / notes side by side), but gains generous spacing (`lg`/`xl`)
so the two photos read as a deliberate before/after comparison, not a cramped form. The report
below is single-column and card-based: each gap, correction, and partial item is its own rounded
card with a colored left accent rather than a plain bulleted list, so scanning by color is
possible even before reading text.

The coverage percentage becomes a prominent metric tile at the top of the report, not a small
inline stat — it's the single number a student cares about first.

## Elevation & Depth

No heavy drop shadows. Depth comes from three flat surface tones layered (`background` →
`surface` → `surfaceRaised`) plus a 1px `border` on cards. This keeps the app feeling calm and
readable rather than skeuomorphic.

## Shapes

Rounded corners throughout (`md`/`lg`), never sharp rectangles — reinforces the "friendly study
tool" feel rather than a clinical enterprise UI. Buttons use `md` rounding; cards and the metric
tile use `lg`.

## Components

Buttons: solid indigo, white text, no border, `md` radius, medium padding — one primary action per
screen. Cards: one flat surface color plus a colored left border/accent matching their semantic
category. Metric tile: the largest text on the page, high contrast, sits in its own raised
surface card at the top of the report.

## Do's and Don'ts

**Do**
- Keep the four semantic colors (critical/correction/partial/success) exclusive to the gap report
- Use Sora only for headings/display, never for dense body text
- Keep background dark and low-contrast between adjacent surface tones

**Don't**
- Don't introduce a fifth accent color — every new UI element should map to an existing token
- Don't use pure black or pure white — always the near-black/near-white tokens above
- Don't add drop shadows or gradients — depth comes from flat surface layering only
- Don't use the primary indigo for anything except the main action button and active/link states
