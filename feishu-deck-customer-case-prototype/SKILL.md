---
name: feishu-deck-customer-case-prototype
version: "v0.1.0"
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
but misleading demo.

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
3. Identify the most valuable mechanism to prototype.
4. Send the prototype story proposal to the user first.
5. Wait for user approval.
6. Generate the prototype page only after approval.

Minimum story proposal:

- `一句话总述`
- `适合做原型的原因`
- `核心演示机制`
- `左侧过去痛点和证据`
- `右侧交互原型流程`
- `需要模拟的数据`
- `不要讲满/不要模拟的点`

Do not directly generate a polished prototype if the user has not approved the
story direction, unless the user explicitly says to start generation immediately.

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

## Prototype Fidelity

The prototype should feel operational and believable, but it does not need to
fully match the customer's real system.

Prioritize:

- business mechanism clarity
- one strong demo path
- realistic field names and statuses
- readable UI states
- Feishu Deck visual fit

Demote:

- full product completeness
- pixel-perfect customer UI recreation
- large amounts of mock data
- decorative animation

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
- Text does not overlap.
- No cards or backgrounds overlap.
- Metrics band has gutters above and below.
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

