---
name: feishu-deck-customer-case-prototype
version: "v0.2.6"
description: |
  Feishu Deck-Customer Case Prototype: generate Feishu/Lark-style interactive
  HTML prototype demo pages from CSM/customer-success case documents. Use for
  案例原型, 原型型案例演示, 可交互案例, 客户案例机制演示, 业务流程原型,
  售前演示原型, and case pages where the goal is to demonstrate the core
  business mechanism instead of only laying out screenshots and text.
---

# Feishu Deck-Customer Case Prototype

This is **skill two** in the customer-case system.

It is independent from `feishu-deck-customer-case` and must be maintained,
installed, invoked, tested, and released separately.

Use this skill when the user wants to turn a case document into an interactive
prototype-style demo page:

- not only a static case card
- not a full product system
- not a fabricated customer implementation
- a focused HTML prototype that demonstrates the core business mechanism

## Progressive Execution Order

Use this skill with lightweight progressive disclosure. Do not treat all rules
as equally urgent at the same time. Follow this order:

1. **Confirm branch and dependencies**: verify that the user wants a skill-two
   prototype demo, not a skill-one static evidence card. Read the base Feishu
   Deck skill before generation. If the prototype includes any Feishu / Lark
   product surface, `lark-design-prototype` is mandatory, not optional.
2. **Read and protect the source**: fetch the exact source document first.
   Never replace a blocked or partial source with adjacent materials unless the
   user explicitly agrees.
3. **Pass the business gates before design**: complete the narratability check,
   challenge / unconfirmed-details check, and prototype-fit judgment before
   discussing layout.
4. **Send the story and prototype plan first**: present the overall story, key
   questions, whether the case is `适合` / `勉强适合` / `不适合` for prototype
   generation, the prototype design plan, interaction / motion plan, media plan,
   missing materials, and whether the user can provide those materials. This is
   mandatory before generation. Do not treat a generic request such as
   "开始制作" as permission to skip the plan; skip only when the user explicitly
   says to skip story / prototype-plan confirmation and directly generate.
5. **Only then design the page**: read
   `references/prototype-experience-rules.md`. If the right-side prototype uses
   Feishu / Lark product surfaces, also read
   `references/product-surface-patterns.md` and `lark-design-prototype`; write a
   `product_surface_map` and lightweight `lark_style_recipe` before
   implementation. Then apply the spatial budget, left pain/evidence region,
   right prototype region, metrics rules, Feishu visual style, interaction /
   motion, and zoom rules.
6. **Use the fast production loop**: unless the user asks for open-ended
   exploration, follow `references/fast-production-rules.md`. Build from the
   default Deck skeleton and product-surface patterns, run only scoped visual /
   interaction checks, and avoid restarting the page from scratch after every
   issue.
7. **Verify before handoff**: run the QA checklist for overlap, spacing,
   readability, interaction, zoom behavior, source truthfulness, and local HTML
   execution.

If a later rule conflicts with an earlier gate, the earlier gate wins. For
example, do not build a beautiful prototype when the source is unread, the
mechanism is unclear, or the prototype-fit judgment is `不适合` and the user has
not chosen to continue.

When the user asks to compare outputs with and without progressive disclosure,
keep both outputs inside skill two. The comparison variable is the execution
order only: `未按渐进式披露直接生成` versus `按渐进式披露先判断故事和原型适配后生成`.
Do not compare skill-one static evidence cards against skill-two prototypes
unless the user explicitly asks for that cross-skill comparison.

## Relationship To Skill One

Skill one: `feishu-deck-customer-case`

- output: evidence-led case card
- main proof: source screenshots, before / after, metrics, captions
- job: prove the case really happened and can be explained clearly

Skill two: `feishu-deck-customer-case-prototype`

- output: interactive mechanism demo page
- main proof: a runnable prototype that shows how the workflow changes
- job: make the case mechanism intuitive for presales / CSM storytelling

Do not mix the two outputs unless the user explicitly asks for both.

When using skill two, do not let skill-one screenshot-card rules dominate the
page. Real evidence still matters, but the right side prototype is the visual
anchor.

## Mandatory Base Deck Skill

This skill depends on the same base deck-generation capability as skill one.

Locate and read the available Feishu / Lark deck-generation skill before
generation, editing, rendering, validation, or handoff.

The canonical upstream dependency is:

`https://github.com/FuQiang/feishu-deck-h5`

In this maintainer's local environment, the known path is:

`/Users/bytedance/.codex/skills/Feishu Deck 0613/SKILL.md`

Use that path only when it exists. If it does not exist, search the available
skills for `feishu-deck-h5`, `Feishu Deck 0613`, `feishu-deck`, or an equivalent
Feishu / Lark deck-generation skill.

Inherit the base deck requirements:

- DeckJSON-first workflow when producing deck pages.
- Design-first workflow.
- Raw page support for custom interactive HTML when needed.
- Feishu visual system, type scale, colors, safe zones, page chrome.
- Rendering, screenshot, and visual QA gates.

If no equivalent base deck skill is available, do not continue into generation.
Tell the user to install the base deck skill first.

## Mandatory Feishu Deck Canvas Shell

Skill-two prototype pages are still Feishu Deck pages. Even when using custom
interactive raw HTML, do not generate a standalone responsive website as the
presentation shell.

Required canvas shell:

- Use one fixed `1920px x 1080px` 16:9 deck canvas for each page.
- Design and position all major regions in that fixed canvas coordinate system.
- Scale the whole deck to the browser viewport with a single contain-scale such
  as `min(window.innerWidth / 1920, window.innerHeight / 1080)`.
- The browser body may provide letterboxing, but page content must not use
  `100vw` / `100vh` as the design canvas.
- Never allow tall browser windows to stretch the slide into a vertical poster.
- Keep slide overflow hidden unless a deliberate internal scroll region is part
  of a specific zoomed image or prototype panel.

Required Feishu logo / page chrome:

- Use the official Feishu Deck logo asset from the base deck skill, or the base
  deck `.wordmark` component when available.
- In the maintainer's local environment, the known logo asset is:
  `/Users/bytedance/.codex/skills/Feishu Deck 0613/assets/lark-logo.png`.
- Standard top-right placement should follow the base deck convention: around
  `top: 61px`, `right: 124px`, `width: 160px`, `height: 50px`.
- Do not hand-draw, approximate, recolor, or rebuild the Feishu logo with CSS.
- If the HTML will be shared outside the local machine, copy or inline the
  official logo asset into the output bundle so the logo does not break.
- Page controls may sit outside or above the deck, but they must not change the
  1920 x 1080 content geometry.
- Title and logo must be designed as the same top-row system: keep the logo on
  the title row / visual baseline, not floating in a separate vertical band.
- The subtitle belongs directly under the title with the skill-one default
  rhythm: subtitle `30px`, title-to-subtitle visible gap around `10px`, unless
  the user explicitly overrides it.

Canvas QA:

- Screenshot at a 16:9 viewport such as `1600 x 900`.
- Also check a taller viewport if the user is viewing in an app browser.
- Verify that the slide remains a centered 16:9 canvas, the logo is correct, and
  content is not vertically stretched, cropped, or oversized.
- Verify that title/logo, title/subtitle, metrics band, and main body use the
  intended proportions and do not create a large dead zone above or below the
  main body.

## Reuse From Skill One

Before generating a prototype page, read the current installed skill-one rules:

`/Users/bytedance/.codex/skills/feishu-case/SKILL.md`

Reuse these skill-one principles unless this skill explicitly overrides them:

- Source integrity gate.
- Lark / Feishu exact-source rule.
- Business narratability gate.
- Challenge and unconfirmed-details gate.
- Story review before generation.
- Presales scene framing.
- Title-as-conclusion rule.
- Title / source display rules.
- Spatial budget rules.
- Overlap prevention rules.
- Container and region rules.
- Metrics rules.
- Copy rules.
- Dead-zone audit.
- QA checklist.

Do **not** reuse skill-one behavior that forces the output into a static evidence
card when the user asked for a prototype demo.

## Human Story-Judgment Boundary

This skill accelerates prototype creation, but it does not replace the case
owner's judgment.

The user / case maker still needs to decide:

- what mechanism is truly worth demonstrating
- which business scene matters most
- what can be simulated safely
- what must remain source-backed and cannot be invented
- what the salesperson should say verbally instead of putting into the prototype

If the mechanism is not clear, pause and clarify before building an attractive
but misleading demo. This judgment should be handled in the same review step as
skill-one story validation: first send the overall plan and key questions to the
user, then generate only after the story direction is approved.

When sending the story proposal, explicitly state whether this case is suitable
for skill-two prototype generation. Use one of: `适合`, `勉强适合`, or
`不适合`, and explain the reason in business terms.

## Source And Truthfulness Rules

The prototype may use simplified UI, mock data, and reconstructed interactions,
but the underlying business mechanism must come from the source case.

Allowed:

- simplify a real workflow into 3-5 demo steps
- use mock names, mock rows, and sample values
- reconstruct a product-like interface that demonstrates the mechanism
- use synthetic example data when clearly derived from the source scenario
- label the page as mechanism demo / prototype when needed

Not allowed:

- invent a customer result that is not in the source
- invent a workflow that the case never implies
- present mock data as real customer data
- imply the prototype is the customer's real production system
- overclaim automation scope when humans are still part of the workflow

If the page uses simulated data, keep it visually natural but avoid implying that
the exact values are real.

## Feishu / Lark Product Fidelity Layer

Most source cases are about work happening inside Feishu / Lark. When the
prototype demonstrates Feishu / Lark scenes such as Docx, Wiki, Sheets, Base,
IM, Approval, Minutes, dashboards, Magic Builder, AI agents, or task workflows,
use the available `lark-design-prototype` skill as the mandatory
product-interface design layer before implementing the right-side prototype.

Use this layer to improve visual fidelity only. It does not replace the source
case, business-story judgment, or truthfulness rules.

This layer is a gate, not a style suggestion:

- If a workflow step can be identified as IM / group chat, Base, dashboard,
  Sheets, Docx, Wiki, task, approval, bot card, or another Feishu / Lark
  surface, do not render it as a generic SaaS card or abstract table.
- Before rendering, write a `product_surface_map` with: step name, business
  action, product surface, source evidence, primary visual object, state change,
  and prohibited content for that step.
- If no Feishu / Lark surface is identifiable, state why and use a generic
  prototype only as a fallback.
- The outer Deck shell remains dark / presentation-style; the embedded product
  surface should use light Feishu product UI and must not inherit the Deck's
  gradients, heavy borders, or presentation cards.

When applying this layer:

- Read the `lark-design-prototype` skill if it is installed.
- Write a lightweight `lark_style_recipe`: surface, spacing, typography,
  component strategy, media strategy, and verification focus.
- Prefer Feishu / Lark native product patterns over generic SaaS panels.
- Use Universe Design-style controls for recognizable buttons, inputs, tabs,
  tables, menus, tags, badges, avatars, dialogs, and similar UI slots.
- Keep the interface operationally believable, but do not imply it is the
  customer's exact production system unless the source proves that.
- If source screenshots exist, use them to calibrate layout and object
  semantics; if they are only evidence, do not over-crop them or replace them
  with invented UI.
- After implementation, run a product-surface QA pass: can the audience
  recognize the Feishu tool within three seconds, are the critical objects
  visible by default, and does each flow state show the correct tool state?

If `lark-design-prototype` is unavailable, still follow Feishu-native visual
principles: restrained white / near-white product surfaces, compact controls,
4px-grid spacing, light borders, readable tables, limited accent colors, and no
decorative gradients inside product UI.

## Prototype Experience Reference

Before generating or substantially redesigning a skill-two prototype page, read
`references/prototype-experience-rules.md`.

This reference defines the core skill-two boundary:

- Before images may be used directly as evidence of the old pain.
- After screenshots are usually product-form references for reconstructing a
  clearer Feishu / Lark prototype, not images to paste directly into the page.
- The prototype must map each business step to a concrete Feishu / Lark product
  surface such as IM group, Base, dashboard, bot, task, Docx, or Wiki.
- Flow states must look materially different, not just swap text.
- Scenario media, generated when appropriate, should make frontline actions
  concrete.
- Interactions and light motion should help the presenter demonstrate the
  mechanism.
- Result dashboards should feel like dashboards: metrics, chart, insight, and
  decision context, not only table rows.

## Product Surface Pattern Reference

Before designing the embedded right-side product prototype, read
`references/product-surface-patterns.md` whenever the workflow uses or implies
Feishu / Lark product surfaces.

This reference does not duplicate `lark-design-prototype`. Its job is to map
customer-case steps to Feishu product surfaces and prevent common case-prototype
mistakes:

- using After screenshots as static evidence instead of reconstructing a
  clearer product demo
- making every flow step look visually identical
- showing future-step content in an earlier step
- drawing a generic SaaS table when the story is really about Base
- drawing a generic chat when the story needs Feishu IM / group-chat fidelity
- building a result list when the story needs a dashboard
- adding duplicated internal titles, sidebars, or explanations that waste demo
  space

## Fast Production Reference

Before generating or substantially revising a prototype page, read
`references/fast-production-rules.md`.

This reference is mandatory unless the task is only a tiny text edit. Its job is
to keep case production within a practical time budget without lowering output
quality:

- use a fixed execution budget and stop open-ended redesign loops
- separate discovery, story, UI skeleton, implementation, and QA
- parallelize only independent work, such as source/media analysis versus UI
  skeleton planning
- reuse the default 1920 x 1080 Deck skeleton and IM / Base / Dashboard product
  patterns
- verify scoped changes first instead of repeatedly running full visual passes
- keep one HTML owner; subagents may prepare plans or fragments but must not
  independently write the final page

## Prototype Fit Gate

Do not make every case into a prototype.

Skill two is suitable when the case has:

- a clear business workflow
- clear input signal
- clear AI / automation / system processing step
- clear output or decision
- clear follow-up action or closed loop
- a mechanism that is hard to explain with static screenshots alone

Good examples:

- store feedback -> AI summary -> issue classification -> owner follow-up
- price exception -> AI recognition -> procurement confirmation -> dashboard loop
- qualification material -> AI initial review -> supplier feedback -> approval
- inspection photo -> AI compliance judgment -> issue reminder ->整改 tracking
- group chat / calls -> AI extraction -> report -> action list

Do not use this skill when:

- the case is mainly a static dashboard proof
- the story has no workflow or user action
- the source only has metrics with no mechanism
- the case relies on real screenshots for credibility and a prototype would weaken
  the proof
- the mechanism is too unclear to explain aloud

If the fit is weak, recommend using skill one instead.

## Required Workflow

Default workflow:

1. Read the exact source.
2. Run the business narratability check.
3. Run the challenge and unconfirmed-details check.
4. Judge whether the case is suitable for skill-two prototype generation.
5. Identify the most valuable mechanism to prototype.
6. Send the overall story proposal, key questions, prototype-fit judgment,
   prototype design plan, interaction / motion plan, media plan, and missing
   material request to the user first.
7. Wait for user approval.
8. Generate the prototype page only after approval.

Minimum story proposal:

- `一句话总述`
- `是否适合技能二生成原型`: `适合` / `勉强适合` / `不适合`, with the reason
- `适合做原型的原因`
- `核心演示机制`
- `左侧过去痛点和证据`
- `右侧交互原型流程`
- `原型设计方案`: page split, product surfaces, default state, and each step's
  primary visual object
- `交互 / 动画方案`: what business object moves or changes, what the presenter
  clicks, and the stable end state after the animation
- `素材方案`: which source images are used directly, which source images are
  only references, which realistic scenario assets are still missing, whether
  the user can provide them, and which assets may be generated only if missing
- `需要模拟的数据`
- `不要讲满/不要模拟的点`

If the fit judgment is `不适合`, recommend skill one or a static evidence card
instead, then wait for the user to decide whether to continue with a prototype
anyway.

Do not directly generate a polished prototype if the user has not approved the
story direction, prototype-fit judgment, prototype design plan, and material /
generated-asset plan, unless the user explicitly says to skip this confirmation
step and directly generate.

## Default Page Structure

The default page is one 16:9 Feishu-style interactive prototype page.

Recommended layout:

- Top title / subtitle band: `16% - 20%`
- Core metrics / conclusion band: `8% - 12%`, placed below title and above main
  body, following skill-one metric rules
- Main body: `60% - 70%`, split into left pain/evidence and right prototype
- Bottom safe area: `4% - 6%`

Main body default split:

- Left `32% - 40%`: past pain + proof evidence
- Right `60% - 68%`: interactive prototype

Interpretation:

- The right-side prototype is the dominant visual anchor.
- The left side explains why the prototype matters.
- Metrics support the story and should not crowd the prototype.
- If there is not enough room, reduce explanatory text before shrinking the
  prototype.
- Left and right main-body containers must share the same top edge and bottom
  safe boundary.
- Before / After section labels and headings should share a consistent baseline.
  Flow controls may sit beside the After heading only if they do not push the
  heading or product window out of alignment.
- The first meaningful content on both sides must align visually: pain cards /
  evidence on the left, product demo window on the right.
- Do not use independent absolute-positioned backgrounds that overlap across
  title, metrics, and body regions. Prefer one owned container per region with
  explicit height, padding, and z-index.

## Left Side: Past Pain And Evidence

The left side should show why the old way failed.

Include:

- one short pain title
- 2-3 parallel pain phrases
- one source-backed quote / screenshot / table / chat / process snippet when
  available
- a short caption explaining what the evidence proves

Avoid:

- long paragraphs
- many equal screenshots
- evidence that is too small to read
- decorative images
- trying to prove every detail from the source

If real source evidence is available, use it on the left side. If the evidence
is too dense, show a readable crop or quote, but keep the business object clear.

## Right Side: Interactive Prototype

The right side is the main stage.

It should demonstrate the core mechanism with 3-5 states or steps.

Common interaction patterns:

- segmented mode switch: `过去 / 现在`
- click stepper: `采集 -> AI 识别 -> 生成建议 -> 责任人跟进`
- input panel + AI output panel
- table row selection -> detail card
- dashboard filter -> highlighted exception
- chat / recording snippet -> AI extracted summary
- before / after toggle
- simulated notification / task assignment

Prototype requirements:

- The first screen must already show the core scene; do not hide the value behind
  too many clicks.
- Interactions should be simple enough for a salesperson to demo live.
- Use realistic but safe mock data.
- Use visible state changes: selected row, highlighted exception, generated
  summary, owner assignment, progress update.
- Do not require backend, login, network, external API, or real customer data.
- All interactions must work in the exported HTML.

Do not build:

- full SaaS systems
- complex navigation apps
- multi-screen workflows that exceed presentation time
- decorative dashboards with no narrative action
- prototypes where every button is fake

## Zoom-In Detail Interaction

When a key evidence image, prototype state, table, report, chart, or workflow
panel is important but cannot be read comfortably at page scale, add a simple
zoom-in affordance in a suitable position.

Rules:

- Use the zoom affordance only for important presentation objects, not every
  minor card.
- Make the affordance lightweight and obvious, such as a small corner icon or
  short `点击放大` hint; it must not cover core content.
- On click, open an overlay that occupies the current deck page / viewport.
- The enlarged object should be as large as practical for live presentation,
  centered both horizontally and vertically, with reasonable margins so it does
  not feel cropped or off-balance.
- Prefer showing the full object in the enlarged view. Use internal scroll only
  when the object is inherently too tall or wide to fit, and keep the default
  enlarged state centered and understandable.
- Avoid adding decorative frames or unnecessary white backing that reduces the
  effective display size.
- Clicking the overlay background or the enlarged object should quickly return
  to the original deck page. `Esc` should also close the overlay when possible.
- The zoom overlay must not change slide state, scroll position, or underlying
  page layout after closing.

## Prototype Fidelity

The prototype should feel operational and believable, but it does not need to
fully match the customer's real system.

Prioritize:

- business mechanism clarity
- one strong demo path
- realistic field names and statuses
- readable UI states
- Feishu / Lark product-interface fidelity when the workflow happens inside
  Feishu products
- Feishu Deck visual fit

Demote:

- full product completeness
- pixel-perfect customer UI recreation
- large amounts of mock data
- decorative animation
- generic SaaS UI that does not feel like Feishu / Lark

If using generated UI elements, keep them in Feishu style: restrained panels,
clear typography, light borders, blue/teal accent, compact controls, and stable
spacing.

## Metrics Rules

Reuse skill-one metrics rules.

In prototype pages:

- Put only the most important `2-3` metrics in the top metric band.
- Metrics should explain why the prototype mechanism matters.
- Do not repeat every source number.
- Do not put the metrics at the bottom by default.
- If metrics are weak or unavailable, use scale/context tags instead of
  fabricating numbers.
- Metric cards must have enough breathing room. Default to number on the left
  and explanatory copy on the right, with a clear gutter or divider between
  them. Keep card padding, line-height, and text-to-edge spacing generous enough
  that the card does not feel packed.
- Do not solve crowded metric cards by only shrinking text. First reduce the
  number of metrics, shorten the copy, or increase the metric band height within
  the allowed spatial budget.

## Visual Style

Follow Feishu Deck style:

- clear conclusion title
- no English eyebrow above the title
- no visible source footer by default
- restrained cards and frames
- no overlapping region backgrounds
- no large dead zones
- main content should occupy most of the page
- image radius around `10px` when using evidence screenshots
- subtitle default from skill one when needed: `30px`, visible title-to-subtitle
  spacing `10px`

The prototype UI may use a lighter product surface inside the right panel, but
the page should still read as a Feishu case deck page, not a standalone product
website.

## Interaction QA

Before handoff, verify:

- The prototype is not blank.
- The default state is meaningful.
- Every visible interactive control works.
- There is a clear speaking path from left pain to right mechanism.
- The right prototype is large enough to inspect.
- The embedded product surface is recognizable as the intended Feishu / Lark
  tool within three seconds.
- Every flow state uses the correct product surface and does not show future
  step content too early.
- Shared business objects stay consistent across states: group name, store ID,
  SKU, dataset, owner, date, and status should not randomly change.
- Text does not overlap.
- No cards or backgrounds overlap.
- Metrics band has gutters above and below.
- Important objects that need inspection have a clear zoom affordance.
- Zoomed content is large, centered, readable, and can return to the deck page
  quickly.
- The page does not depend on network calls.
- Mock data does not appear to be real private data.
- If screenshots are used, they are readable and not aggressively cropped.
- The HTML runs locally.

For custom interactive raw pages, use browser screenshot / interaction checks
where available.

## When To Suggest Two Outputs

If the source has both strong real evidence and a strong demonstrable mechanism,
consider suggesting two deliverables:

1. skill-one evidence card
2. skill-two prototype demo

Do not force both into one page unless the user asks.
