# Handoff: Ada Gu Portfolio — Pages v3

## Overview
A personal product design portfolio website showcasing Ada Gu's work on AI-driven enterprise tools and design systems. The site presents six screens: a homepage with project cards, five case studies with distinct visual narratives, and a style guide documenting the visual system.

## About the Design Files
The files in this bundle are **design references created in HTML** — high-fidelity prototypes showing the intended look, layout, typography, spacing, colors, interactions, and behavior. These are not production code to copy directly. Your task is to **recreate these HTML designs in your target codebase** (React, Next.js, Vue, etc.) using its established patterns, component libraries, and build systems. Apply the design tokens and layout structure defined here, but adapt implementation to your framework's conventions.

## Fidelity
**High-fidelity (hifi)**: Pixel-perfect mockups with final colors, typography, spacing, interactions, and animations. Recreate the UI exactly as shown, using your codebase's design system or the tokens defined below.

## Screens / Views

### 1. Homepage
**Purpose**: Hero introduction, project portfolio showcase, lab section, contact form, and footer.

**Layout**: 
- Nav: sticky top, horizontal flex, logo (38px) left, three links right (Work, Lab, About)
- Hero section: centered column, padding 172px top / 148px bottom, max-width container
  - Kicker: 11px uppercase, letter-spacing .14em, color #8A8D96
  - H1: clamp(34px, 5vw, 58px), font-weight 600, line-height 1.06, letter-spacing -.03em, max-width 15em
    - Contains inline highlighted text with background-color inset shadow (rgb(210, 213, 222))
  - Subtitle: clamp(16px, 1.6vw, 19px), color #787B84, max-width 30em
- Project grid: 5 cards, responsive columns, 32px gap
  - Each card: image (16/10 aspect), title, description, keyword chips
  - Image scale on hover: 1 to 1.035, 620ms cubic-bezier(.2,.7,.2,1) transition
  - Keyword chips: Style C (default) — #F3F4F8 background, 10.5px bold uppercase, .06em tracking, #5C5F68 color
  - Alternative keyword styles available: Style A (muted text), Style B (outlined pills)
- Lab section: heading + grid of items
- Contact form: centered form with email input
- Footer: links and metadata

**Typography**:
- Font: Instrument Sans (400, 500, 600, 700 weights)
- Body: 16px, line-height 1.65
- Nav/button: 14–15px
- H1: variable (see layout)
- Small caps/kickers: 10–11px, uppercase, letter-spacing .12em–.14em

**Colors**:
- Background: #FAFAFC
- Ink/text: #0F1014
- Body text: #2A2B2D
- Muted: #8C8E92, #8A8D96, #787B84
- Hairline/divider: #DADAD6
- Chip fill: #F3F4F8, #E2E2DD
- Link hover: #0F1014

**Interactive States**:
- Card image: hover scale 1.035, 620ms transition
- Links: color #0F1014 on hover
- Buttons: background #FAFAFC when active, text #0F1014; transparent bg and muted text when inactive

---

### 2. Cognite Atlas AI Case Study
**Purpose**: "Designing for a system that guesses" — narrative of designing an AI system with memory and knowledge constraints.

**Accent Color**: #6C2BF2 (purple)

**Layout**: 
- Sticky left rail (200px): meta (dl with role, tools, timeline), scroll-spy TOC
- Content column (960px, max 640px prose)
- Gap: 56px
- Section structure:
  - Numbered band (01 FRAMEWORK, etc.): 150px top margin, 44–96px eyebrows
  - Colored eyebrow (accent)
  - H3: 29px
  - Prose text
  - Figures: up to 960px width; data-r="bleed" extends to viewport edge

**Sections**: Framework / Memory / Knowledge / Freedom / Takeaway

**Next Case**: Links to Halliburton InnerVue

---

### 3. Halliburton InnerVue Case Study
**Purpose**: "A pipeline is not a tube" — enterprise tool for pipeline visualization.

**Accent Color**: #DD0F26 (red)

**Layout**: Same as Cognite (left rail, content column, 56px gap)

**Next Case**: Links to Ashley TNT

---

### 4. Ashley Furniture TNT Case Study
**Purpose**: "Seven taps to three" — reducing friction in mobile UX.

**Accent Color**: #D24700 (orange)

**Structure**: Problem / Design / Outcome

**Next Case**: Links to P&G Artwork

---

### 5. P&G Artwork Case Study
**Purpose**: "A model's capability is not a product" — enterprise design tool.

**Accent Color**: #0B5BFF (blue)

**Structure**: Problem / Time / Meaning / Outcome

**Next Case**: Links to WayHome

---

### 6. WayHome Case Study
**Purpose**: "When the real problem is acquisition" — growth strategy for mobile app.

**Accent Color**: #0B7D74 (teal)

**Structure**: Constraint / Funnel / Product / Takeaway

**Next Case**: Links back to Cognite (circular)

---

### 7. Style Guide
**Purpose**: Visual system documentation for the portfolio brand.

---

## Interactions & Behavior

**Navigation**:
- Preview bar (top sticky): Buttons to switch screens
- Active button: white background (#FAFAFC), black text (#0F1014)
- Inactive button: transparent, muted text (#ACAFB8)
- Smooth scroll on navigation: window.scrollTo(0, 0)

**Case Study Scroll Spy**:
- Left rail TOC links highlight when section scrolls into view
- Threshold: section top less than 160px from viewport top
- Updates on scroll event

**Card Hover**:
- Project card image scales 1 to 1.035 over 620ms cubic-bezier(.2,.7,.2,1)
- Resets on mouse leave

**Keyword Chip Switcher** (homepage):
- Three style options: A (text only), B (outlined), C (filled background, default)
- Active state: black background, white text
- Inactive: transparent, muted text

**Next Case Button**:
- Full-width band with title and arrow
- Background transitions 0.25s ease
- Hover: background #F2F3F7
- Accent color on hover (varies per case study)

**Animations** (reduced-motion respected):
- Strip animation: 9s steps(1,end) infinite (paused by default, plays on hover)
- Bar animation: scaleX 0 to 1, 9s linear
- Beam animation: conic-gradient rotation, 3.6s linear infinite
- All respect prefers-reduced-motion

---

## State Management

**Screen State** (single source of truth):
- Current screen: 'home' | 'cognite' | 'case' | 'ashley' | 'pg' | 'wayhome' | 'style'
- Displays/hides appropriate screen div
- Updates preview bar button styles

**Card Hover State** (homepage):
- Tracks hovered card key: null | 'Cog' | 'Hal' | 'Ash' | 'Pg' | 'Way'
- Applies scale transform to image

**Keyword Style State** (homepage):
- kw: 'A' | 'B' | 'C' (default 'C')
- Controls keyword chip appearance

**Scroll Spy State** (case studies):
- Active TOC link index
- Updates on scroll and screen change

---

## Design Tokens

### Colors
```
Primary Background: #FAFAFC
Primary Text/Ink: #0F1014
Body Text: #2A2B2D
Muted: #8C8E92, #8A8D96, #787B84, #6B6D71, #5C5F68, #5F6165
Hairline/Border: #DADAD6, #E6E8EE, #C9C9C4, #C3C3BE
Chip Fill: #F3F4F8, #E2E2DD

Accents (per case study):
  Cognite: #6C2BF2 (purple)
  Halliburton: #DD0F26 (red)
  Ashley: #D24700 (orange)
  P&G: #0B5BFF (blue)
  WayHome: #0B7D74 (teal)
```

### Typography
```
Font Family: Instrument Sans (fallback: -apple-system, sans-serif)
Weights: 400, 500, 600, 700

Sizes:
  Body: 16px
  Small/button: 11–14px
  Kicker/label: 10–11px
  H3 (case study): 29px
  H1 (hero): clamp(34px, 5vw, 58px)

Line Heights:
  Body: 1.65
  Heading: 1.06–1.1

Letter Spacing:
  Body: default
  Uppercase labels: .06em–.14em
  H1: -.03em
  H3: -.025em
```

### Spacing
```
Gap (grids/flex): 6px–32px (context-dependent)
Padding (containers): 24px–56px
Margin (sections): 150px (numbered bands), 22px–56px (elements)
```

### Borders & Shadows
```
Border Radius: 3px (buttons), none (cards, text)
Shadows: Inset highlights, subtle box-shadows on hover
Hairlines: 1px solid
```

### Responsive Breakpoints
```
960px: Small layout adjustments
820px: Major layout changes (1-column grid, hide rail TOC, reflow metadata)
```

---

## Assets

- **Logo**: uploads/logo.png (38×38px)
- **Case study imagery**: Currently placeholders with dashed borders
  - Cognite: /images/cognite-atlas/ (9 images)
  - Halliburton: /images/halliburton-innervue/ (12 images)
  - Ashley: /images/ashley-furniture/
  - P&G: /images/pg-artwork/
  - WayHome: /images/wayhome/

---

## Files

- **portfolio.html** — **the source of truth. Edit this directly.**
  All seven screens, standalone, no build step, no dependencies except Google
  Fonts (Instrument Sans).

- **Portfolio Pages v3.dc.html** — the original Claude Design export. Historical
  only; it needs a `support.js` runtime that was never shipped, so it does not
  run on its own.

- **convert.py** — **retired 2026-08-09, do not run.** It converted the export
  above into `portfolio.html`. Design authority has moved to Figma, so changes
  now go straight into `portfolio.html`; re-running this would overwrite them.

### Where the design lives now

Figma is the source of truth for layout and visual design:
https://www.figma.com/design/tgnob0hWLMhIgU3QzIp7R1/Ada-Gu-Portfolio-v3

Animations are the exception — they are built as standalone HTML/CSS/JS in
`website-asset/`, and Figma only carries a `Motion Placeholder` marker
recording frame size, trigger, state flow, and source file.

---

## Implementation Notes

1. **Screen switching**: Use state to toggle visibility of screen divs
2. **Scroll spy**: Attach passive scroll listener; calculate section positions and update active TOC
3. **Responsive**: Use CSS media queries at 960px and 820px
4. **Animations**: Implement keyframes with prefers-reduced-motion support
5. **Next case linking**: Each case study bottom band links to next in cycle
6. **Form handling**: Contact form on homepage (wire up to email service as needed)

---

## Contact
Ada Gu · wanyinggu8@gmail.com · Austin, TX
