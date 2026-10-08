---
version: 1
slug: "frontend-src-pages-dashboardpage-tsx"
primary_target: "frontend/src/pages/DashboardPage.tsx"
related_targets: ["frontend/src/components/layout/AppShell.tsx"]
---

# Desk and app shell

Mode: Operate. Scope: the whole Patra frontend (shell, Desk, Clients, Documents, Filings, Settings, document drawer). Audience: CAs and audit teams in Indian firms, working all day on dense client records under filing deadlines. Task: see which clients are ready to file, clear flagged documents, upload new ones. Proof and content: real seeded clients, documents, review reasons and filings from the API; nothing invented. Constraints: desktop first, high density, no fake data, no controls that do nothing.

## Direction contract

THESIS: A client register, like the books-of-account software accountants already use, where readiness is read from a segmented bar per client and flagged documents are one click away. It refuses the stat-card dashboard, avatar rows, and decorative icons.

OWN-WORLD: Ink navy (#14213a) rail on a cool grey ground, white 1px-ruled work panels, no shadows except the drawer. Green means validated, amber means needs review, red means failed, slate means pending. Source Sans 3 at 14px with tabular numerals, JetBrains Mono only for GSTIN, PAN and IDs. Square-ish 4px controls, 6px panels.

STORY: The accountant opens Patra, sees in one sentence what needs them, scans the register for clients that are not ready, and opens the flagged document to read the exact reason and the extracted fields beside the source file.

FIRST VIEWPORT: Left navy rail (220px) with five items and the firm name at the foot. Main area: page title "Desk" with Upload document at right; one sentence stating what needs review; below, the client register (about 70% width) with columns client, open filing, documents bar, status, and a sticky totals row with the colour legend; at right a "Needs your attention" list (about 30%) showing filename, client and the real review reason. Primary action: Upload document, top right.

FORM: Client Register, the user's pick from the familiar hand (round 3 of the decision page). Seed key a9347b68.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
