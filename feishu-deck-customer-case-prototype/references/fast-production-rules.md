# Fast Production Rules

Read this reference before generating or substantially revising a skill-two
customer-case prototype page.

The goal is to reduce production time while preserving story quality, Feishu
Deck quality, product-surface fidelity, interaction clarity, and QA discipline.

## 1. Why Generation Becomes Slow

The usual causes are:

- reading every related skill and reference repeatedly instead of loading only
  the branch required by the current task
- entering layout implementation before the story and prototype-fit judgment are
  stable
- building the Deck shell, product UI, interaction, and visual polish from
  scratch every time
- using source screenshots as late-stage design inputs instead of classifying
  them before layout
- repeatedly fixing overlap after implementation instead of reserving fixed
  geometry for each region first
- running full-page visual passes after every small edit
- using subagents without a single-writer merge rule, causing duplicated work or
  conflicting edits

Do not solve speed by skipping source reading, story validation, product-surface
mapping, or visual QA. Solve it by reducing rework.

## 2. Default Time Budget

Use this target unless the user explicitly asks for deeper exploration:

- source fetch and media classification: `4-6 min`
- story / prototype-fit / material-gap plan: `4-6 min`
- layout skeleton, product-surface map, and prototype-motion plan: `4-6 min`
- first working HTML: `12-18 min`
- scoped QA and one correction pass: `6-10 min`

If the page is still not acceptable after one correction pass, stop and report
the exact blocker or request a targeted choice. Do not keep redesigning the page
silently for another long loop.

## 3. Progressive Disclosure For Speed

Load only the references needed for the current case:

- Always read `SKILL.md`, the base Feishu Deck skill, and skill-one rules.
- Read `prototype-experience-rules.md` for any generation or substantial
  redesign.
- Read `product-surface-patterns.md` only when the right-side prototype uses or
  implies Feishu / Lark product surfaces.
- Read `lark-design-prototype` only for the embedded product UI, not for the
  whole dark Deck shell.
- Do not read all Lark product skills unless the source requires those APIs or
  product operations.

When editing an existing page, read the local HTML and only the rule branch that
explains the issue. For example, an overlap fix needs Deck geometry rules; an
IM fidelity fix needs the IM pattern rules.

## 4. Parallel Work Rules

Parallelize independent work when the environment supports subagents or
parallel tool calls:

- Source/media lane: fetch document, download assets, classify images as Before
  evidence / After reference / Result proof / Weak.
- Story lane: extract one-sentence story, pain, mechanism, value, open
  questions, prototype-fit judgment, and material gaps that need user
  confirmation.
- Product lane: draft `product_surface_map`, primary visual object per step,
  interaction / motion per step, generated-media candidates, and prohibited
  content per step.
- QA lane after implementation: inspect screenshot, check console/resource
  issues, and list overlap/readability/interaction problems.

Single-writer rule:

- Only one owner writes the final HTML file.
- Subagents may return plans, snippets, or review findings, but they must not
  independently patch the same HTML.
- Merge in this order: story contract -> skeleton -> product states ->
  interactions -> visual QA fixes.

Do not parallelize dependent work. Product UI should not be implemented before
the story contract, prototype design plan, material plan, and product-surface
map are stable and approved.

## 5. Reusable Skeleton First

Start from the same page skeleton instead of inventing layout each time:

- Copy `assets/prototype-page-skeleton.html` into the run output folder when
  starting a new one-page prototype, then replace content and product states.
- Copy the official Feishu logo into `output/assets/lark-logo.png` before
  rendering, because the skeleton references that local path.
- fixed `1920 x 1080` stage
- title/subtitle band: `16% - 20%`
- metrics band: `8% - 12%`
- metric cards: default to number on the left, copy on the right, with generous
  padding, clear gutter / divider, and short explanations. If cramped, remove or
  shorten metrics before shrinking text.
- main body: `64% - 72%`
- bottom safe area: `2% - 4%`
- left panel: Before pain / evidence
- right panel: After Feishu solution / embedded product demo
- official Feishu logo in the title row
- `点击放大` overlay for the product window
- flow controls beside the After heading when space allows
- no page number by default; add pagination only when the user explicitly asks
  for it or a multi-page delivery requires it

Create this skeleton before writing detailed content. If the skeleton already
violates spacing, fix geometry before adding richer UI.

## 6. Product Pattern Reuse

Choose one primary product pattern per step:

- IM / group chat for reminders, store feedback, photo / voice replies, and bot
  cards
- Base / multidimensional table for structured records, AI validation,
  attachment recognition, owner tracking, and write-back
- Dashboard for result verification, trends, comparisons, and management views
- Form / Magic Builder page for frontline submission and lightweight workflows

Do not draw generic cards when a recognizable Feishu product surface is implied.
Use the product pattern as a reusable component family, then change fields,
messages, rows, charts, and state tags for the case.

## 7. Interaction Scope

Every prototype page should include at least one meaningful interaction or
motion, but keep the scope small:

- `演示当前`: replays the current step's local animation.
- `自动演示`: runs the 3-5 step demo sequence when useful.
- Step click: changes the product state and triggers that step's small motion.
- Zoom: enlarges the product window or key evidence without changing state.

Use short, stable animations: message arrival, upload progress, AI scan line,
row highlight, status tag change, chart growth. Avoid full autoplay flows that
hide content or make the presenter wait.

When a step depends on a concrete business object such as a transfer screenshot,
store photo, receipt, shelf image, voice message, or bank-flow snippet, use the
real source media if available. If it is missing, ask the user whether they can
provide it before generating an illustrative bitmap. Do not generate scenario
media silently.

## 8. Scoped Verification

Run the smallest useful check first:

- static HTML/resource check for missing local assets and obvious syntax issues
- screenshot at `1600 x 900` for Deck geometry
- one screenshot of the most crowded state
- console/DOM check only when interaction fails
- final click-through only for visible controls that changed

Do not take screenshots of every step after every text or CSS adjustment. After
small edits, verify only the affected state. Run broader verification at
handoff.

## 9. Stop Conditions

Stop implementation and ask or report when:

- source access or image download is blocked
- the business story is still unclear after the narratability check
- the case is not suitable for a prototype and the user has not approved
  continuing anyway
- the required product surface is unknown
- one correction pass still leaves a major layout conflict
- a requested fidelity level requires unavailable assets or a real product
  session

When stopping, state the exact blocker and the smallest decision needed to
continue.

## 10. Fast Handoff Checklist

Before handoff, confirm:

- source story and metrics are not invented
- page uses the fixed Feishu Deck canvas
- title/logo, metrics, body, and bottom safe area keep the required proportions
- Before evidence is readable and not misleading
- right prototype is the visual anchor
- each step has a distinct product state
- at least one meaningful animation or interaction works
- zoom opens and closes quickly
- no obvious overlap, clipping, or large dead zone remains
- output runs locally without network dependencies
