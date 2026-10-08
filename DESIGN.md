---
name: Patra
description: A client register for Indian CA firms, in ink navy and white, where state is the only colour.
colors:
  ink-navy: "#14213a"
  navy-deep: "#0f1a30"
  navy-raised: "#1d2e4f"
  navy-hover: "#2a3f66"
  rail-text: "#b4bdd0"
  ground: "#f1f3f7"
  surface: "#ffffff"
  surface-sunk: "#f6f7fa"
  line: "#e0e4eb"
  line-strong: "#c7cedb"
  text: "#16223a"
  text-2: "#46516a"
  text-3: "#636c80"
  validated: "#0a6e4b"
  validated-tint: "#e7f3ed"
  validated-bar: "#14865d"
  review: "#85560a"
  review-tint: "#fbf1db"
  review-bar: "#d4922a"
  failed: "#b0241a"
  failed-tint: "#fcebe9"
  failed-bar: "#c93b2e"
  pending: "#566079"
  pending-tint: "#eef0f5"
  pending-bar: "#aab2c4"
typography:
  title:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  panel-title:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.45
  body:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Source Sans 3, Segoe UI, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.45
  identifier:
    fontFamily: "JetBrains Mono, ui-monospace, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  sm: "4px"
  md: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "20px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.ink-navy}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    height: "34px"
    padding: "0 14px"
  button-primary-hover:
    backgroundColor: "{colors.navy-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    height: "34px"
    padding: "0 14px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    height: "34px"
    padding: "0 10px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
  nav-item:
    backgroundColor: "{colors.ink-navy}"
    textColor: "{colors.rail-text}"
    rounded: "{rounded.sm}"
    height: "36px"
  nav-item-active:
    backgroundColor: "{colors.navy-raised}"
    textColor: "{colors.surface}"
  badge-validated:
    backgroundColor: "{colors.validated-tint}"
    textColor: "{colors.validated}"
    rounded: "{rounded.sm}"
  badge-review:
    backgroundColor: "{colors.review-tint}"
    textColor: "{colors.review}"
    rounded: "{rounded.sm}"
---

# Design System: Patra

## Overview

**Creative North Star: "The Client Register"**

Patra looks like the books-of-account software an accountant already trusts: a ruled register of clients, one row each, with a bar showing how many of that client's documents are validated, in review, failed or pending. The screen is organised around the work (which clients are not ready, which documents need a decision), not around a metrics dashboard. Everything is flat, ruled in 1px lines, and set in tabular figures so numbers line up.

The product is Operate-mode software used all day, so the system stays out of the way. The ink-navy rail carries the brand; the work area is white on a cool grey ground; colour appears only to say what state something is in. Controls are the standard ones: buttons, selects, tables, tabs, a native dialog.

**Key Characteristics:**
- One flat surface type, the panel, with a 1px rule and no shadow.
- State colour (green, amber, red, slate) is the only decoration, and each state also has a text label.
- Density first: 14px body, 13px secondary, 34px controls, 36px rows of navigation.
- Figures are tabular. Identifiers (GSTIN, PAN, invoice numbers) are set in mono; nothing else is.

## Colors

A navy brand colour on a cool grey ground, with four state colours that each carry a text, a tint, a rule and a bar fill.

### Primary
- **Ink Navy** (#14213a): the rail, primary buttons, the active tab underline and the focus ring on light surfaces. Taken from the logo.

### Secondary
- **Audit Green** (#0a6e4b, bar #14865d): validated documents and on-track clients only. Never a button colour.

### Tertiary
- **Review Amber** (#85560a text, bar #d4922a): documents and clients that need a human. The sidebar count badge uses a lighter amber (#e9b44c).
- **Failure Red** (#b0241a, bar #c93b2e): failed extraction or rejected documents.
- **Pending Slate** (#566079, bar #aab2c4): uploaded, processing or extracted but not yet validated.

### Neutral
- **Cool Ground** (#f1f3f7): the page behind the panels.
- **Paper White** (#ffffff): panels, inputs, the drawer.
- **Sunk Paper** (#f6f7fa): table headers and the totals row.
- **Rule** (#e0e4eb) and **Strong Rule** (#c7cedb): every divider and input border.
- **Ink**, **Ink 2**, **Ink 3** (#16223a, #46516a, #636c80): text, secondary text, muted text. Muted text still clears 4.5:1 on white.

### Named Rules
**The State-Only Colour Rule.** Green, amber, red and slate mean validated, review, failed and pending, nowhere else. Brand and actions are navy.

**The Label Beside the Colour Rule.** A state is never colour alone: the badge, bar tooltip or row text always says it in words.

## Typography

**Body and Display Font:** Source Sans 3 (with Segoe UI, system-ui)
**Identifier Font:** JetBrains Mono (with ui-monospace, Consolas)

**Character:** A humanist workhorse sans with excellent tabular figures and the ₹ glyph, used at one family and a short scale. Mono is reserved for strings an accountant copies or compares character by character.

### Hierarchy
- **Title** (600, 21px, 1.2, -0.01em): the page name, once per page.
- **Panel title** (600, 16px): the name of a panel, with the count in muted weight 400.
- **Body** (400, 14px, 1.45): table cells, descriptions, form values.
- **Label** (600, 13px): table headers, field labels, badges, secondary lines.
- **Identifier** (400, 12px mono): GSTIN, PAN, invoice and policy numbers.

### Named Rules
**The Tabular Rule.** Every table and total uses tabular numerals so columns of rupees align.

**The No Shouting Rule.** No uppercase tracked labels. Hierarchy comes from weight and size.

## Layout

A fixed 220px navy rail (62px collapsed, collapsed by default under 800px) beside a scrolling main area. Pages use 20px and 28px padding, a 16px gap between panels, and cap at 1480px. The Desk is a two-column grid: the client register takes the remaining width and the attention list is 340px; it stacks under 1180px. Tables scroll horizontally inside their panel, and secondary columns hide when the table is narrower than 760px, for example beside the open drawer. Under 900px the document drawer covers the page.

## Elevation & Depth

Flat. Depth is expressed by 1px rules and tonal steps (ground, paper, sunk paper). The only shadow is the document drawer lifting off the page.

### Shadow Vocabulary
- **Drawer** (`box-shadow: -10px 0 28px -12px rgba(15, 26, 48, 0.22)`): the docked document drawer only.

### Named Rules
**The Border-or-Shadow Rule.** A surface has a 1px border or a shadow, never both. Panels use the border.

## Shapes

Square-ish and quiet: 4px on controls, badges and nav items, 6px on panels and the dialog. No pills except the sidebar count. No avatars or decorative icon tiles. Icons are Lucide at 1.75 stroke, used for navigation and a few buttons only.

## Components

### Buttons
- **Shape:** 4px radius, 34px tall.
- **Primary:** ink navy with white text, 14px 600. One per page, top right.
- **Secondary:** white with a strong rule. **Quiet:** text-only with a hover tint, for table-adjacent actions.
- **Hover / Focus:** hover steps the fill; focus is a 2px navy outline offset 2px (white on the rail).

### Badges
- 1px rule, tinted fill, 13px 600 text in the state colour, 4px radius. The text is the state name.

### Readiness bar
- Signature component. A flex row of segments (validated, review, failed, pending), 8px tall in tables, 2px gaps, 2px radius, grown in proportion to document counts, with an accessible summary. The totals row under the register repeats it as a legend.

### Inputs / Fields
- 34px, white, strong rule, 4px radius; hover darkens the rule, focus turns it navy. Labels sit above in 13px 600. Errors are plain red text under the form.

### Navigation
- Navy rail, 36px items, 17px icons, label and optional count. Active is a raised navy fill with white text. The count badge shows the real number of documents in review.

### Table
- Sunk-paper header, 1px row rules, 11px vertical padding, whole row clickable with the primary cell as the real link.

### Document drawer
- Docked 600px panel with the flagged reason first, tabbed views (extracted data, source file, OCR text, raw data, history), flat sections divided by rules.

## Do's and Don'ts

### Do:
- **Do** lead a document's overview with its review reason when it is flagged.
- **Do** keep one primary button per page and put it top right.
- **Do** show "Not recorded" or "Not found" when a value is missing, never a plausible default.
- **Do** format rupees with Indian grouping (₹1,42,350) and tabular numerals.

### Don't:
- **Don't** add stat-card rows, avatar initials, gradient fills or decorative icon tiles.
- **Don't** use green, amber or red for anything but state.
- **Don't** add controls whose backend does not exist yet; leave them out until they work.
- **Don't** use uppercase tracked micro-labels or emoji.
