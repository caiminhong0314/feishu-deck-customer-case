# Prototype Experience Rules

Read this reference whenever generating or substantially redesigning a
skill-two customer-case prototype page.

## 1. Source Image Role

Classify source images before design:

- `Before evidence`: real screenshots that prove the old pain, such as messy
  chats, complex Excel sheets, scattered dashboards, manual forms, or unclear
  handoff records. These may be shown directly on the page.
- `After reference`: screenshots of the improved Feishu / Lark workflow,
  dashboards, tables, group chats, documents, bots, or reports. Use these mainly
  as product-form references to reconstruct a clearer prototype. Do not paste
  them as the main After visual by default.
- `Result proof`: real screenshots that prove a measured outcome. Use directly
  only when the screenshot itself is the proof and remains readable.
- `Weak / decorative`: duplicated, unreadable, generic, or story-irrelevant
  images. Omit them.

Default rule:

- Before can use real source images directly to make the old pain concrete.
- If there is no true Before screenshot or quote, do not force an image into the
  Before region. Use a pain summary, old-process sketch, or short quote instead.
- Never use an After screenshot as Before evidence just because the page needs a
  visual; this weakens the contrast and misleads the story.
- After should usually be a reconstructed Feishu-style prototype based on the
  source screenshot's tool, layout, fields, and workflow.
- Do not fill the After side with original document screenshots when a runnable
  prototype would better explain the mechanism.
- Do not display internal design reasoning on the case page, such as
  `prototype说明`, `新版After不再贴原截图`, `素材角色`, `设计逻辑`, or similar
  meta-explanations. The page only contains customer story content.

## 2. Feishu Tool Mapping

Before building the prototype, write a `product_surface_map`.

For each workflow step, map:

- business action
- Feishu / Lark product surface, such as IM group, Base, Sheets, Docx, Wiki,
  dashboard, bot, approval, task, or Magic Builder page
- source screenshot or source text that implies this surface
- primary visual object that must be visible by default
- prototype state to show
- user action or automatic system action
- prohibited content, especially content that belongs to a later workflow step

The prototype should look like the specific Feishu tool being used, not a
generic SaaS table. Examples:

- `门店回传` should look like a Feishu group chat or mobile submission scene.
- `AI验收` should show an AI result card, pass / fail status, image recognition
  evidence, and automatic write-back.
- `多维表格追踪` should look like a Base table with views, fields, tags,
  records, owners, and status colors.
- `结果看板` should look like a dashboard: headline metrics, trend or comparison
  chart, funnel / bar / line / ranking modules, and highlighted result deltas.
- If `AI验收` means image / attachment recognition and structured write-back,
  Base / multidimensional table is usually the primary surface. The main visual
  should be records, fields, status tags, attachments, image translation,
  validation result, feedback result, voice reason, and automatic action. A
  right detail drawer may support the story, but the table is the main visual.
- If `门店上传` is a group feedback action, it should show the store message,
  photo upload, optional voice message, transcript, and recorded / write-back
  card in sequence. Do not show upload proof in the earlier `10:00预警` step.
- If `原因归因` follows a store reply, do not repeat the same voice collection
  screen as the main point. Show structured analysis, reason tags,
  responsibility owner, and at least one data visualization or summary result.
- If `结果看板` is used, it must contain dashboard structure: metrics, chart,
  filter / period, and insight / decision. A plain list is not enough.

When using `lark-design-prototype`, use it to reconstruct the product surface
semantics from the source screenshot. Do not stop at generic borders, panels,
and tables.

If the source screenshot is a recognizable Feishu / Lark surface, mirror that
surface category in the prototype:

- IM / group-chat screenshots should become Feishu-style chat UIs with avatars,
  timestamps, message bubbles, bot cards, and action affordances.
- Base / table screenshots should become Base-like workspaces with side
  navigation, views, fields, status tags, highlighted rows, and owners.
- Dashboard screenshots should keep the source dashboard's broad structure:
  title / toolbar, filters, chart/table split, and the same key comparison
  pattern when available.

Keep the same business object across steps unless the source explicitly changes
it: group name, store ID, SKU, dataset name, owner, date, and status should form
one coherent demo path.

## 2.1 Deck Shell And Embedded Product Prototype

Skill-two pages are not full-screen product prototypes. They are customer-case
Deck pages with an embedded Feishu / Lark product demo window.

Use a two-stage composition:

1. Use the Feishu Deck skill to design the outer case page: title, subtitle,
   metrics, Before pain, narrative structure, Feishu logo, dark / presentation
   background, and spatial placeholder for the demo.
2. Use `lark-design-prototype` only inside the reserved demo area to generate a
   Feishu / Lark product surface such as IM, Base, Sheets, dashboard, task, or
   AI result panel.
3. Insert that product surface into the Deck as a self-contained
   `product-demo-window` / embedded prototype region. The product window should
   use its own light product UI style and should not inherit the outer Deck's
   dark cards, blue gradients, thick borders, heavy weights, or decorative
   presentation effects.

Default embedded-product rules:

- The product demo region is the right-side visual anchor and should be as large
  as the Deck layout reasonably allows.
- If the demo region is still too small for live reading, add a `点击放大` affordance
  to enlarge the entire product window, not every small card inside it.
- Flow controls can stay in the Deck layer above or beside the product window.
  Clicking a flow step should update the product window's internal state.
- The product window should feel like a real Feishu / Lark workspace: white /
  near-white surfaces, top bar, sidebar or toolbar when useful, light borders,
  6-10px radius, 14px body text, 400/500 font-weight rhythm, restrained blue
  states, and no gradients inside the product UI.
- Keep the outer Deck page and inner product prototype visually separated. The
  Deck explains the story; the embedded product window demonstrates the
  mechanism.

## 2.2 Deck Geometry And Alignment

Use the Feishu Deck shell as fixed geometry, not a free-flow webpage.

Required proportions:

- Title / subtitle band: `16% - 20%`.
- Metrics / conclusion band: `8% - 12%`, directly between title and body.
- Main body: `64% - 72%`.
- Bottom safe area: `2% - 4%`.

Alignment rules:

- Title and logo are one top-row system. They should feel horizontally aligned,
  with the logo on the same visual row as the title.
- Subtitle sits close to the title; do not create a separate blank band between
  title and subtitle.
- Metrics must not overlap the title or main body. If metrics crowd the page,
  reduce the number of metrics before shrinking the product demo.
- Left Before container and right After container must share the same top edge.
- Before / After labels, section headings, and first content blocks should align
  by baseline or top edge.
- Flow controls can sit beside the After heading, but they must not force the
  heading to wrap awkwardly or push the product window down.
- Avoid independent absolute-positioned background rectangles. Each region owns
  its own background, padding, border, and height; backgrounds from title,
  metrics, and body must not overlap.
- If the right product window needs more space, remove duplicated internal
  title rows, redundant sidebars, or explanatory text before reducing the
  product UI.
- Do not show page numbers by default. Page numbers consume limited lower-right
  space and should appear only when the user explicitly asks for them, or when a
  multi-page case needs page navigation for delivery. If page numbers are used,
  keep them inside the bottom safe area and never reserve a large footer band
  only for pagination.
- Outer Deck Before / After section titles should stay smaller than the main
  page title and metrics. Use `22px - 26px` by default, with `26px` as the
  normal upper bound for one-line section conclusions. If a Before / After
  title wraps awkwardly or competes with the product window, shorten the copy or
  reduce the size within this range before moving regions or shrinking the demo.

## 2.3 Metric Card Breathing

Metrics are a scanning aid, not a dense data table.

Default metric-card structure:

- Keep `2-3` metrics only.
- Put the large number / result on the left.
- Put the metric name and short explanation on the right.
- Use a visible gutter or subtle divider between number and copy.
- Preserve generous inner padding on all sides; copy should not sit close to
  card borders.
- Keep title and explanation line-height comfortable enough for projection.

Crowding fixes, in order:

1. Shorten the metric explanation.
2. Remove the weakest metric.
3. Increase the metric band height within the allowed `8% - 12%` budget.
4. Only then reduce font size slightly.

Do not create cards where numbers, labels, and explanatory copy feel compressed
against each other or against card edges. When a card feels crowded, treat it as
a layout failure even if text technically fits.

## 3. Step Differentiation

Every step in a prototype flow must visibly differ from the previous step.

Before implementation, define each step's `primary visual object`. Examples:

- `10:00预警`: bot notification card in the Feishu group.
- `门店上传`: store photo / voice reply and recorded confirmation.
- `AI验收`: Base record row with attachment, AI recognition status, and feedback.
- `原因归因`: reason summary, owner assignment, and analysis chart.
- `结果看板`: dashboard metrics and comparison chart.

For each step, change at least three of:

- active product surface or region
- highlighted data row / card
- visible status tag
- chat message or notification
- image / media state
- AI output
- chart / KPI state
- responsibility owner or next action

Do not make five tabs that only swap copy while the screen still looks the same.
If steps cannot be made visually distinct, reduce the number of steps and keep
only the strongest 3-4 states.

Do not use a step label as the only difference. The product window itself must
show a changed state that a presenter can point to.

For process-driven prototypes, prefer a process-step schematic over plain tabs.
The flow control should help the presenter explain the mechanism, such as
`预警 -> 上传 -> AI验收 -> 归因 -> 看板`, and clicking each node should update the
corresponding prototype state.

## 4. Scenario Media

Use scenario media when a business action needs physical context.

Examples:

- `门店回传照片`: show a realistic shelf / product display / package photo.
- `巡店检查`: show a realistic store shelf, freezer, poster, terminal display,
  factory floor, or inspection object.
- `客服 / 门店语音`: show a voice message chip, transcript, and AI extraction.
- `转账 / 回款 / 支付凭证`: show a realistic transfer-success screenshot,
  receipt, bank-flow snippet, or payment confirmation rather than a generic card
  when the business point is "someone uploaded proof of money received".

Media sourcing order:

1. Use the exact source image when it is available, readable, and safe to show.
2. If the source implies a concrete object but the image is missing or unusable,
   ask whether the user can provide the required material before generating.
3. Generate a realistic illustrative bitmap only when the material is missing,
   the user has approved the prototype plan / material plan, and the image is
   clearly used as an illustrative demo asset rather than customer proof.
4. Use a neutral UI placeholder only when the media object is not important to
   understanding the workflow.

Generated bitmap images are allowed when:

- the source implies the physical scene but does not provide a usable photo
- the source provides a partial or low-quality reference, and a clearer simulated
  object would make the prototype easier to explain
- the image is clearly illustrative and does not claim to be real customer proof
- it helps the audience understand what is being submitted, checked, or acted on

Generated scene images should be natural, presentation-safe, and restrained. Do
not make them decorative hero images. In the prototype, label them as example
uploads or simulated examples when needed.

Do not generate images silently. The story / prototype plan must list:

- what source media exists
- what media is missing
- whether the user can provide it
- what generated image would be produced if the user does not provide it
- where the generated image will appear in the prototype

## 4.1 Default Visibility

Critical content for the current state must be visible without scrolling.

- `10:00预警`: the bot reminder card is visible; do not include later upload
  photos in this state.
- `门店上传`: the uploaded photo, optional voice message, transcript, and recorded
  confirmation should be visible together where possible. If a single chat
  column cannot fit them, use a split view rather than hiding the main proof
  below an internal scroll.
- `AI验收`: the Base table row, attachment, AI recognition / validation status,
  and feedback result are visible by default.
- `原因归因`: the analysis result, reason tags, owner, and chart are visible by
  default.
- `结果看板`: at least one metric, one chart, and one insight are visible by
  default.

Internal scroll is allowed for supplementary inspection, long image previews,
or secondary records. It must not be required to understand the main workflow
state.

## 5. Interaction And Motion

Design interaction only when it improves the live explanation.

Good interactions:

- Click `10:00预警` to send a new group message and highlight the related Base
  row.
- Click `上传照片` to move a store image from mobile / group chat into the
  inspection panel.
- Click `AI验收` to show pass / fail result, reason, and automatic write-back.
- Click `归因汇总` to transform voice / chat feedback into structured reason
  tags.
- Click `结果看板` to show chart and KPI changes.

Motion rules:

- Animate the business object, not an abstract decoration. For example, in a
  store-upload scenario, the transfer-success screenshot / receipt should appear,
  upload, be recognized, and become a structured record. A generic card moving
  without a recognizable business object is weaker and should be avoided.
- Use small CSS/JS state transitions for live demo clarity: message arrives,
  row highlight moves, upload card appears, AI check progresses, status changes,
  chart updates.
- Prefer a concrete sequence: source object appears -> system is processing ->
  recognized result / structured record appears -> next responsible action is
  visible.
- Keep motion short and reversible. It must never hide content permanently.
- Each motion should end in a stable, explainable state. The presenter should be
  able to pause and point at the result.
- Do not add decorative animation that does not explain the workflow.
- Do not add a full-process autoplay by default. Use autoplay only when the user
  explicitly asks for it. Prefer small per-step effects, such as message arrival,
  upload appearance, scan line, row highlight, or chart growth, so the presenter
  can control the story.

## 6. Prototype Emphasis

The prototype must have one visual emphasis at a time.

For each state, define:

- primary focus object
- main business question answered by this state
- key result / number / decision shown in this state

Promote only the result numbers that make the mechanism credible. Avoid a KPI
wall. When showing a result, place the number near the chart, table row, or
status that proves it.

## 7. Dashboard Feel

A result dashboard must not be only a list.

Minimum dashboard ingredients:

- 1-2 top metrics with clear deltas
- one comparison chart, trend chart, ranking, funnel, or distribution chart
- one highlighted insight / decision card
- a visible filter / period / scope cue when useful
- enough layout density to feel like an operating dashboard, not a table dump

Use charts or visual summaries for result proof. Tables are supporting detail,
not the whole dashboard unless the source case is explicitly table-centric.

## 8. QA Additions

Before handoff, verify:

- Before images, if used, are real evidence of the old pain.
- After visuals are reconstructed prototype surfaces unless direct proof
  screenshots are explicitly needed.
- Each step looks materially different.
- The prototype makes clear which Feishu / Lark tool is being used.
- `product_surface_map` exists and every step has a product surface, primary
  visual object, state change, and prohibited content.
- The embedded product UI follows the selected surface: IM looks like Feishu
  group chat, Base looks like multidimensional table, Dashboard looks like an
  operating dashboard.
- No step shows content that belongs to a later step, such as upload photos
  appearing in the first reminder state.
- Shared business objects are consistent across steps: group name, store ID,
  SKU, dataset, owner, date, and status.
- Title and logo are on one visual row; title, subtitle, metrics, body, and
  bottom safe area follow the required proportions.
- Page numbers are absent unless explicitly requested.
- Left and right body regions align at the top, and section labels / headings
  do not drift vertically.
- Region backgrounds do not overlap. No container should visually intrude into
  the title, metrics, or another body container.
- Scenario media makes the physical or frontline action understandable.
- At least one meaningful interaction changes state, not just text.
- Motion supports the speaking path and does not distract.
- Result dashboard includes real dashboard structure: metrics + chart + insight.
- The product demo window is large enough. If not, remove redundant header rows,
  duplicated sidebars, or explanatory copy before shrinking the product surface.
- Critical state content is visible by default. Internal scroll is only for
  supplementary inspection.
- The page does not contain meta copy such as `prototype说明`, `新版After`,
  `素材角色`, or design-process explanations.
