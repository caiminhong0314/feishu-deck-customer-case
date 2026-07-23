---
name: feishu-deck-customer-case
metadata:
  version: "v0.1.0"
description: |
  Feishu Deck-Customer Case: generate and edit Feishu/Lark-style customer case
  cards from CSM/customer-success documents, customer stories, case materials,
  screenshots, and Lark/Feishu docs. Use for 客户案例, 案例卡片, 一页纸案例,
  one-pager case, 行业案例, 客户成功案例, 场景案例复盘, CSM 文档转案例卡片,
  and case pages that should be produced with a Feishu/Lark deck-generation
  skill such as Feishu Deck 0613. Formerly triggered as feishu-case.
---

# Feishu Deck-Customer Case

This skill is a case-card design profile on top of **feishu-deck-h5**
(`https://github.com/FuQiang/feishu-deck-h5`). It does not replace the base deck
skill. It defines how to understand, structure, and visually present customer
cases while reusing the base deck skill for production, rendering, validation,
and delivery.

## Mandatory Base Deck Skill

Before generation, editing, rendering, validation, or handoff, locate and read
the available base Feishu / Lark deck-generation skill.

The canonical upstream dependency is `feishu-deck-h5`:

`https://github.com/FuQiang/feishu-deck-h5`

Do not depend on a single local display name. In different environments the base
skill may appear as `feishu-deck-h5`, `Feishu Deck 0613`, `feishu-deck`, or
another equivalent local name. Use the available skill list and descriptions to
find the skill that owns Feishu / Lark HTML deck generation, DeckJSON rendering,
raw-page production, visual validation, and delivery.

In this maintainer's local environment, the known path is:

`/Users/bytedance/.codex/skills/Feishu Deck 0613/SKILL.md`

Use that path only when it exists. If it does not exist, search the available
skills / skill roots for `feishu-deck-h5` or an equivalent Feishu / Lark deck
skill.

If no equivalent base deck skill is installed, do not continue into HTML case
generation. Explain that the current environment lacks the required base deck
capability: this customer-case skill depends on `feishu-deck-h5` for DeckJSON
rendering, raw-page production, visual validation, and delivery. Tell the user
to install `feishu-deck-h5` first, and provide the link:

`https://github.com/FuQiang/feishu-deck-h5`

Inherit the base deck skill requirements, including:

- DeckJSON-first workflow.
- Design-first workflow.
- Raw-first policy where appropriate.
- Feishu visual system, type scale, colors, safe zones, and page chrome.
- `render-deck.py` rendering.
- Validator and screenshot / visual QA requirements.
- `deck.json` as the source of truth for edits.

Do not hand-write final HTML as the source of truth. For edits to existing
decks, update the DeckJSON slide/page and render from it.

## Scope

Default scope is one 16:9 case card unless the user explicitly asks for a
multi-page case deck.

If the case content is rich, has many key images, or contains multiple proof
scenes, the user can explicitly ask to make it a two-page case card instead of
forcing everything into one crowded page.

A case card is a presentation artifact, not a full document summary. It should
help a reader understand the case in 5-10 seconds and support a speaker who can
explain details verbally.

## Human Story-Judgment Boundary

This skill accelerates customer-case card creation, but it does not replace the
case owner's judgment.

The agent may draft the story, recommend page structure, and choose candidate
evidence assets. The user / case maker still needs a clear understanding of:

- what the case is truly trying to prove
- which customer scene matters most
- which evidence images are necessary for the customer-facing story
- which claims should be emphasized, softened, or left to speaker explanation

Do not present the first generated page as final if the story logic, proof
images, or customer-facing emphasis have not been reviewed.

When the document is rich but the key story is not obvious, explicitly remind
the user that AI can organize and visualize the material, but the final priority
selection still depends on human understanding of the case and sales context.

If the user says an image choice or page emphasis is wrong, treat that as a
story-signal correction, not merely a layout revision. Update the proof asset
selection and narrative emphasis before adjusting typography or spacing.

## Source Integrity Gate

If the user provides a specific source page, URL, wiki, doc, PDF, or file, that
source is authoritative. Do not silently replace it with adjacent materials,
same-customer archives, or similar screenshots.

Before designing:

1. Read the exact source content first.
2. Distinguish these states clearly:
   - `source fetched`: exact content successfully read.
   - `source blocked`: exact content exists but could not be read due to auth,
     permissions, or environment.
   - `source partial`: only part of the exact content was read.
3. Generate normally only from `source fetched`.

If the source is `source blocked` or `source partial`:

- Do not generate a normal case card as if the source had been read.
- Do not fill gaps with inference from same-customer old decks, local folders,
  or nearby project materials unless the user explicitly agrees to that fallback.
- State the real blocker precisely, for example:
  - CLI installed but keychain unavailable in sandbox.
  - Auth available but media token download denied.
  - Exact doc body unreadable, only related assets found locally.

### Lark / Feishu Source Rule

If the source is a Lark / Feishu wiki or doc:

- Try the exact doc first with the available Lark CLI / doc tools.
- If sandboxed access fails because keychain or login state is unavailable,
  retry with the approved out-of-sandbox path when the environment allows it.
- Only after the exact document body is fetched may related local materials be
  used as supporting evidence assets.

Related local materials may support layout and proof, but they are never a
substitute for the missing source story.

## Business Narratability Gate

Before design or layout, run a simple "业务可讲性检查".

The case is not ready for visual design unless the agent can explain it aloud in
plain business language in 3-5 sentences, without hiding behind layout terms or
tool names.

The agent should be able to answer these four questions clearly:

1. What customer/business scenario is this actually about?
2. What was broken or expensive before the change?
3. What mechanism changed the work, not just what product was used?
4. What business result proves the change mattered?

If, after reading the source, the agent still cannot explain the case clearly,
do **not** continue into design just because assets or numbers are available.

Instead, pause and get clarification first:

- Prefer asking an industry-aware stakeholder, the original author, or the user.
- Ask no more than **3 focused questions**.
- Use the questions to remove business ambiguity, not to collect decorative copy.

Recommended question types:

- `场景确认`: 这个案例里真正要解决的业务问题是什么？它对客户为什么重要？
- `机制确认`: 真正起作用的机制是什么？哪些动作是 AI / 自动化替代的，哪些仍然靠人？
- `价值确认`: 最终应该讲的价值到底是效率、质量、风险控制，还是收入增长？核心数字对应哪个价值？

If no knowledgeable person is reachable in the current environment:

- state that the case is `story unclear`
- list the missing business assumptions explicitly
- ask the user for clarification before generating a polished case page

Do not let the skill produce a visually strong but narratively empty page.

## Challenge And Unconfirmed-Details Gate

After the case passes the narratability gate, run a second check:
`反问这个案例，找出没有确认的细节，以及最容易被同类客户追问的点。`

Goal:

- identify what is still ambiguous
- identify where a prospect or peer customer would challenge the case
- prevent the page from sounding complete when key business details are still fuzzy

Before design, the agent should explicitly list two buckets:

1. `未确认细节`
2. `容易被追问/挑战的问题`

These are not the same:

- `未确认细节` = facts the source does not fully specify
- `容易被追问/挑战的问题` = facts that may be partially known, but will still
  be tested by an industry-aware audience

Typical challenge dimensions:

- business object definition
- data source and data quality
- metric口径 and attribution
- responsibility split between AI and humans
- boundary / exceptions / non-covered cases
- scalability and reuse conditions

Recommended prompt to self-check the case:

- 这个案例里，哪些关键名词其实还没定义清楚？
- 这个结果数字，口径到底是什么？谁会追问它怎么算出来的？
- 这个机制里，哪些步骤是系统自动完成的，哪些仍然靠人？
- 如果是同类客户，他们最可能问“你这个到底比对了什么、数据从哪里来、为什么能信”？

For retail / pricing / operations cases, always probe questions like:

- 比对的具体是什么价格？采购价、批发价、零售价、竞品价分别如何定义？
- 这些价格信息分别来自哪里？系统、人工市调、供应商、门店，还是外部渠道？
- 异常判断规则是什么？阈值、区间、频次是谁定的？
- AI 在这个案例里到底做了识别、分析、建议中的哪几步？
- 收益提升和效率提升分别对应哪个动作链条？

Output rule before design:

- If these challenge points can be answered from source, summarize the answers.
- If they cannot be answered, keep them as an explicit `风险/待确认` list in the
  working notes.
- Do not silently smooth them over with polished wording.

Presentation rule:

- The final case page does not need to display every open question.
- But the agent must know them before designing, so the page does not overclaim
  certainty.
- If a detail is likely to be challenged in live selling, prefer designing the
  page so the claim stays at the right level of certainty.

## Story Review Before Generation

After finishing:

- business narratability check
- challenge / unconfirmed-details check
- presales scene framing

do **not** jump straight into slide generation.

Default workflow for case-card creation:

1. read exact source
2. produce the `可汇报故事方案`
3. send the story to the user first
4. discuss and revise until the story is approved
5. only then ask explicitly whether to generate the case card
6. generate design / layout / HTML only after user confirmation

This rule is especially important for case work, because a page can look polished
while the story is still weak, vague, or strategically wrong.

Minimum story-review output before generation:

- `一句话总述`
- `售前讲法顺序`
- `可以明确讲的点`
- `不要讲满的点`
- if useful, `建议页面主叙事`

Do not treat silence as approval.
Do not infer “go ahead and generate” merely because the user asked for a case
earlier in the thread.
Once the story proposal is sent, wait for the user's approval or revisions
before entering design/render execution.

## Universal Case Card Requirements

Every case card should make these five elements visible:

- Background / pain points.
- Solution.
- Before / after change.
- Quantified value.
- Key evidence assets.

If the source lacks numbers, screenshots, diagrams, or other evidence, state the
gap. Do not invent facts, metrics, customer names, quotes, or source claims.

## One-Page Fit Gate

Do not assume every customer story fits a one-page case card.

A one-page case card works best when the source has:

- one dominant problem frame
- one dominant solution frame
- one dominant value frame
- one dominant evidence visual

If the source is actually one of these, pause and reframe before rendering:

- a strategic umbrella story with several parallel subcases
- a platform story with multiple application lines of similar importance
- a long program update with no single proof-heavy visual anchor
- a document whose real value is comparison across several scenes

In those cases, choose one of these paths explicitly:

- narrow to one subcase
- reframe as `foundation + application lines`
- recommend a multi-page case deck instead

Do not force a weak one-pager just because the user said "案例".

## Story First

Before designing, identify the real story structure. Do not mechanically turn
source sections into Step 1 / Step 2 / Step 3.

Classify the case into one or more story archetypes:

- Single-point efficiency: one workflow or role became faster or easier.
- Process automation: a manual chain became automated or trackable.
- Knowledge / standardization: scattered standards or knowledge became reusable.
- Data insight: hidden information became structured insight.
- Business growth: insight drove sales, conversion, retention, or revenue action.
- Multi-application loop: one foundation supports multiple downstream use cases.
- Platform foundation: a shared system, data layer, knowledge base, or workflow
  platform enables many teams or scenarios.

Use a linear step flow only when the source story is genuinely linear. If the
case is "one foundation + multiple applications", show the foundation and the
application lines clearly.

### Strategic Transformation / Umbrella Case

If the case starts from a chairman / CEO / BU strategic ask and then branches
into several initiatives, do not flatten those initiatives into fake sequential
steps.

Instead separate:

- strategic ask
- shared operating foundation
- key application lines
- measurable operating value

For these cases, a good one-pager usually reads as:

- why the organization had to change
- what common system or mechanism was built
- which 2-4 application lines prove it worked
- what scale or value numbers validate the change

If the template cannot express that clearly, switch away from a default
step-flow or generic story-case shape.

## Presales Scene Framing

When the case will be used in presales, do not jump straight into abstract
pain points or platform capability labels.

Start from a concrete business scene that a customer can picture:

- who discovered the problem
- where they discovered it
- what they needed to do next
- why that manual action stopped working at scale

Good presales case storytelling usually follows this order:

1. `一个具体场景`
2. `这个动作在小规模下怎么做`
3. `规模一上来为什么失效`
4. `系统机制如何接管`
5. `结果为什么成立`

This helps the story feel operational and believable, instead of reading like a
polished summary detached from real work.

Recommended pattern:

- `原来，当……的时候，需要……`
- `但当规模变成……时，完全靠人去……已经不现实`
- `于是问题开始表现为……`
- `新的机制不是替代业务，而是把……这条动作链接住`

For retail / pricing / store / field-operation cases, prefer scene-led openings
such as:

- 市调人员在线下/线上发现竞品价格异常，需要回头找采购确认
- 区域运营发现门店执行偏差，需要追总部标准和门店现场情况
- 门店/客服一线收到大量反馈，但总部无法快速提炼出共性问题

Avoid opening the story with:

- “客户使用了飞书多维表格 / AI / 机器人……”
- “该案例实现了数字化、智能化、自动化……”

Those are solution labels, not scenes. A presales listener first needs to feel
the work, then understand the mechanism.

## Narrative Rules

Summarize pain points as short display phrases, preferably parallel in structure.
Examples:

- Standard scattered / execution opaque / insights buried.
- Manual review / long cycle / high cost.
- Data fragmented / decisions delayed / actions hard to track.

Use the user's domain language when it is clearer than generic wording. Avoid
copying long source paragraphs directly onto the slide.

Describe the solution as actions and mechanisms, not just product names. Prefer:

- "AI identifies document issues and standardizes content"
- "Recordings are transcribed and compared against standards"
- "Customer feedback is clustered into weekly review actions"

Over:

- "Use Feishu AI"
- "Use Wiki"
- "Use forms"

For before / after comparisons, use concise paired language:

- Past: manual sampling + experience judgment.
- Now: item-level comparison + data tracking.

## Conditional Scenario Rules

Apply these only when the source case matches the scenario. Do not force them
onto unrelated cases.

### Knowledge / SOP / Standardization

If the case is about SOP, standards, knowledge management, policies, manuals, or
documentation, highlight how AI or workflow turns raw material into usable
standards:

- Issue detection.
- Deduplication.
- Missing content detection.
- Conflict detection.
- Ambiguous wording detection.
- Standardization.
- Knowledge-base structuring.
- Maintenance and version control.

### Process Automation

If the case is about approval, audit, fulfillment, operations, finance, HR, or
other process automation, emphasize:

- Original manual nodes.
- Automated or AI-assisted nodes.
- Handoff reduction.
- Cycle-time reduction.
- Error / rework reduction.
- Traceability and responsibility.

### Data Insight / Voice of Customer

If the case is about extracting information from recordings, chats, tickets,
documents, comments, or surveys, emphasize:

- Source signal capture.
- Structuring / classification.
- Insight extraction.
- Clustering.
- Routing into reports, reviews, or actions.
- Closed-loop follow-up.

### Business Growth

If the case is about sales, conversion, retention, renewals, store growth, or
marketing, emphasize:

- Where growth signals were hidden.
- How they were extracted or prioritized.
- How they entered sales / store / marketing actions.
- What measurable business value changed.

### Collaboration / R&D / Project Management

If the case is about project work, product/R&D, cross-team collaboration, or
delivery management, emphasize:

- Cross-team alignment.
- Knowledge reuse.
- Decision traceability.
- Progress visibility.
- Risk discovery.
- Delivery efficiency.

### Customer Service / Frontline Operations

If the case involves customer service, retail, stores, field teams, call centers,
or frontline operations, emphasize:

- Frontline signal capture.
- Standard execution.
- Service quality.
- Customer issues.
- Feedback to managers or headquarters.
- Actionable review loops.

## Layout Strategy

Default recommended layout:

- Top: lightweight summary strip.
- Bottom: key evidence assets as the main visual.
- Overall: light conclusion, heavy evidence, stable numbers, clear story.

Top summary can include:

- Pain point phrases.
- Solution axis.
- Core value metrics.

Bottom visual can include:

- Flow diagram for "how it works".
- Business story image for "why it matters".
- Result screenshot for "what was produced".
- Before / after visual for "what changed".

Do not make all modules equally heavy. Choose one dominant visual anchor.

## Case Poster Rules

Customer case cards should read more like a presentation poster than a
documentation page.

The page must make a strong business point first, then prove it with evidence.
Do not turn the case into a balanced inventory of pain / solution / metrics /
screenshots where every module has similar visual weight.

Before layout, define:

- `page role`: what this page is mainly doing, such as pain framing, mechanism
  proof, before / after comparison, result proof, or evidence showcase
- `one-line conclusion`: the business claim the audience should remember
- `dominant proof`: the strongest screenshot, process diagram, before / after
  visual, or metric that proves the claim
- `supporting details`: secondary numbers, captions, or screenshots that can be
  visually demoted

If this decision is unclear, do not continue into visual production. A case page
without a dominant claim will usually become a crowded module board.

## Title-As-Conclusion Rule

Prefer titles that carry the case conclusion, not neutral topic labels.

A strong case title usually contains:

- customer / scenario
- AI or workflow action
- measurable business result when source-backed

Prefer:

- `AI助力门店反馈洞察，反馈收集提升50%`
- `AI辅助终端巡检，覆盖率提升74%，检查效率提升300%`
- `AI助力差评申诉，成功率提升4倍`

Over:

- `门店反馈管理案例`
- `终端巡检解决方案`
- `差评申诉流程`

If a metric is the strongest proof on the page, consider putting it in the title
or subtitle instead of burying every number in equal KPI cards.

## Title And Source Display Rules

Default case-card chrome should match the clean case-poster pattern:

- The first visible text in the title band should be the Chinese conclusion title.
- Do not place English eyebrow, category, or customer metadata above the title,
  such as `J&T EXPRESS · CASE` or `BUSINESS VALUE · FIELD CASES`.
- If customer / industry / stage metadata is needed, move it to file metadata,
  speaker notes, or a small in-body label that directly helps the proof.
- Do not display `来源`, `数据口径`, calculation notes, or internal document links
  as a bottom footer by default. Keep source and caveat details in working notes,
  speaker notes, `DESIGN-PLAN.md`, or the final response.
- Do not add a customer logo by default. Add customer / partner logos only when
  the user explicitly requests them, the source page requires them for the case
  format, or the reference layout strongly depends on a logo lockup. Do not infer
  that a customer logo is needed just because a logo asset exists.
- On dark case pages, do not add a white badge / white container behind logos by
  default. Use the transparent / white Feishu logo directly. If a customer logo
  is explicitly required, first look for a transparent, white, or dark-background
  compatible logo treatment; use a white logo backing only when the user asks for
  that branded lockup or when the reference design clearly requires it.
- In Feishu Deck raw pages, do not manually add a second Feishu / Lark logo when
  the base framework already injects a `.wordmark` / brand mark. Duplicate Feishu
  logos are a page-chrome defect.
- Show a visible source / data note only when the user explicitly asks for it,
  compliance requires it, or the page claim would be misleading without it.
- If a visible source note is required, keep it compact and ensure it does not
  create a bottom dead zone or compete with the dominant proof visual.


## Evidence-Led Layout Rule

When credible screenshots, real scene photos, tables, chats, dashboards, or
process images exist, the default layout should be evidence-led.

Recommended pattern:

- one dominant proof visual
- one to two local zooms, labels, or secondary proof snippets
- a small number of result metrics
- short labels explaining what each visual proves

Do not default to equal-width screenshot grids. Equal grids work only when every
image is readable at presentation distance and each image proves a different
point.

If multiple screenshots are available:

- promote the clearest and most important one as the main proof
- use smaller overlays / callouts for supporting screenshots
- remove or move weak screenshots instead of shrinking all images equally
- prefer visual labels on top of images over long explanatory paragraphs below
  them

Evidence visuals must answer "what does this prove?" quickly. If a screenshot is
present but unreadable, it is not strong evidence; enlarge it, crop deliberately,
zoom into the relevant area, or demote it.

## Visual Annotation Rules

Use short labels, callouts, arrows, highlights, or zoom cards to explain
evidence visuals directly.

Good labels name the business capability demonstrated by the screenshot:

- `AI自动总结`
- `异常自动提醒`
- `风险评级`
- `申诉话术生成`
- `看板追踪`
- `责任人触达`

Avoid asking the audience to infer the story by reading small screenshot text.
When the source image is dense, annotate the capability being proven and keep
the label close to the evidence.

Use overlays sparingly:

- overlays should clarify the proof, not decorate the page
- labels should not cover the critical part of the image
- arrows and highlights should point to a specific evidence area
- never use annotations to compensate for an otherwise unreadable image

## Container And Region Rules

Design the page as a region system before placing modules.

Typical case regions:

- `Header`: title and one-line conclusion
- `Context / Metrics`: pain phrases, scale, or result numbers
- `Main`: dominant proof visual or mechanism visual
- `Support`: secondary evidence, local zooms, or supporting notes
- `Footer` (optional): only required notes or page chrome; omit source and
  data notes by default unless explicitly required

Every visible module must clearly belong to one region. A module should not sit
across two region boundaries.

Hard rules:

- do not let one region's background frame extend behind another region
- do not let a card from a lower region visually intrude into the upper region
- do not place explanatory text on the boundary between two framed regions
- do not rely on transparent background overlap to imply separation
- if two adjacent regions both have visible borders or tinted backgrounds, either
  leave a clear gutter between them or visually demote one region

For dense case pages, prefer sibling regions over nested heavy containers.

## Background Ownership Rules

Each visual region must choose one container strategy:

- region frame: one large background frame, with lightweight internal elements
- card group: no large parent frame, with cards carrying the visual structure
- open band: no heavy frame, using spacing, labels, lines, or arrows

Do not combine all three at the same weight.

Avoid:

- a large tinted parent frame containing several equally heavy cards
- two adjacent large dark frames touching or nearly touching
- a process frame and evidence cards competing for the same vertical boundary
- repeated thick borders that make the page feel like stacked containers rather
  than one clear story

If the proof image is the dominant visual, demote surrounding process and metric
containers into lightweight strips, tags, or open bands.

If the process diagram is the dominant visual, demote screenshots into an
evidence strip or small proof snippets.

Container design should support hierarchy. It should never become the hierarchy.

## Spatial Budget Rules

Case pages must be designed against the **full usable slide area**, not against a
smaller floating inner artboard.

Do not solve layout by placing content inside an arbitrarily smaller fixed canvas
and leaving large unused space above or below it.

Default vertical budget for a case page:

- title / subtitle band: about `16% - 20%`
- core metrics / conclusion band: about `8% - 12%`; default placement is
  between the title band and the main content band
- main narrative and evidence band: about `60% - 70%`
- optional note band: `0% - 4%`; if no visible note is required, give this
  space back to the main content
- bottom safe area: about `4% - 6%`
- slack space: minimal and intentional

Interpretation:

- The main content should visually dominate the page.
- Core metric cards should support the story transition from title to evidence;
  do not default them to the bottom unless the layout needs a bottom conclusion
  strip.
- Large dead zones between title and body, or between body and footer, are a
  layout failure, not elegant whitespace.
- If a page still has visible empty bands after the core modules are placed,
  expand the dominant visual or resize the content grid before adding more text.

When using raw layout:

- Budget from the full page safe area first, then place modules.
- Do not create a smaller fixed inner canvas unless the content is intentionally
  meant to float and the user explicitly wants that effect.
- If absolute positioning is used, anchor blocks to the page-level content band,
  not to a conservative sub-canvas.
- For dense stacked modules, prefer CSS grid / flex row tracks over multiple
  independently absolutely-positioned blocks.

## Overlap Prevention Rules

Case pages must treat overlap as a layout design failure, not as a polish issue
found late in QA.

Default prevention rule:

- if a page contains 3 or more stacked content zones, build them with explicit
  row tracks or measured vertical bands first
- do not stack several cards by hand with absolute `top` values unless the page
  is very sparse and the content heights are extremely stable

Required discipline for subtitle-bearing pages:

- first reclaim unnecessary title-to-subtitle and subtitle-to-body gap
- only after that shrink or rebalance body modules
- do not leave unused space under the subtitle while lower modules collide
- For case pages with a subtitle, set the subtitle at `30px` and the visible
  title-to-subtitle spacing at `10px` by default.
- In Feishu Deck raw pages, the effective spacing is usually controlled by
  `.header .page-sub { margin-top: ... }`, not by title `margin-bottom`. Verify
  the effective selector before assuming a spacing change worked.
- If using `30px` exceeds the base Deck type ladder, explicitly mark the
  subtitle with `data-allow-typescale` rather than silently shrinking it to a
  weaker size.
- Subtitle copy must be line-break safe at the final rendered width. Do not allow
  the second line to contain only one or two Chinese characters or punctuation.
  If this happens, first shorten redundant copy, remove repeated labels, or
  rewrite the subtitle; do not solve it by silently shrinking the subtitle below
  the case default.

Required discipline for dense raw pages:

- one module's internal copy must fit within that module's own measured height
- leave a deliberate vertical buffer between adjacent zones
- never rely on hidden overflow or hoped-for text wrapping to avoid collision

If using absolute positioning anyway, the agent must explicitly budget:

- zone top
- zone height
- expected internal content height
- gap to the next zone

and verify that the sum is coherent before rendering.

Strong recommendation:

- use a top-level grid such as `metrics / mechanism / proof / footer`
- then size cards within each zone

This is more robust than freehand `top` offsets and should be the default for
image-heavy case pages.

## Dominant Visual Rules

Every case page should have one clear visual anchor that takes the largest share
of attention and area.

Good anchors:

- a before / after evidence zone
- a mechanism / process diagram
- a key system screenshot
- a business story image with direct explanatory value

Avoid pages where several medium-weight modules sit in the middle of the slide
with similar size and large unused margins around them.

For image-rich multi-page cases:

- page 1 usually lets the before / after evidence zone occupy most of the main
  content band
- page 2 usually lets the mechanism diagram or strongest proof visual occupy
  most of the main content band

The anchor should expand first. Secondary chips, labels, and helper text should
shrink or move before the anchor gives up space.

## Image Rules

Case cards should use meaningful visual assets when available. Images are not
decoration; they must help tell the story.

Prefer:

- Flow diagrams to explain mechanisms.
- Product screenshots to prove output.
- Business story diagrams to explain insight.
- Real scene photos to prove operating context.
- Before / after visuals to explain change.

### Evidence Asset Selection

Before layout, classify every available image by its proof job. Do not choose
images because they look cleaner or fit the grid more easily.

Required selection pass:

1. `Before evidence`: images that prove the old workflow, pain, manual effort,
   scattered data, or customer quote.
2. `After evidence`: images that prove the new mechanism, system output,
   dashboard, automation, report, or operating loop.
3. `Value evidence`: images that prove measurable result, exception handling,
   tracking, decision support, or business action.
4. `Decorative / weak`: images that are pretty, generic, duplicated, unreadable,
   or not directly connected to the story.

Selection rules:

- promote images that show the business object and operating context, even if
  they are visually less polished
- prefer real screenshots / chats / tables / reports over generic UI fragments
  when the goal is to prove a case
- choose the screenshot that best supports the story claim, not the screenshot
  that is easiest to crop
- if the user provides or marks specific images as Before / After / key proof,
  treat those as first-choice assets unless they are technically unusable
- do not replace user-provided proof images with adjacent same-customer material
  unless the user explicitly agrees
- omit weak images instead of shrinking or cropping strong images to make room

If the selected image set does not clearly prove the story, pause and state the
asset gap rather than building a polished but weak case card.

Evidence images are proof, not decoration:

- default to full-image readability first
- prefer `contain` behavior for screenshots, chat records, tables, and process
  diagrams
- use `cover` only when the image is decorative, or when a crop is intentional
  and still preserves the key evidence area
- if an image must be cropped to show a key detail, that crop should be an
  explicit decision, not a default background behavior

Respect the source asset's aspect ratio and orientation:

- vertical screenshots should usually get narrow-tall containers
- wide dashboards and flow diagrams should usually get wide containers
- do not force several very different assets into identical containers if that
  makes them unreadable

If a screenshot becomes too small to read at presentation size:

- enlarge it
- or remove a weaker neighboring module
- or move it to another page

Do not keep a tiny proof image just because it exists.

### Image Display And Cropping Policy

Default behavior for proof images is **show the whole image**.

Cropping is allowed only when all of these are true:

- the crop preserves the user's ability to understand what the image is
- the crop keeps the business object, key UI area, or proof text visible
- the cropped-away area is genuinely irrelevant whitespace or repeated detail
- a caption or nearby label still explains what the image proves

Do not use aggressive cropping as a layout shortcut.

Avoid:

- cropping dashboards so column / chart context disappears
- cropping tables so headers or row labels disappear
- cropping chat screenshots so the speaker / quoted pain point is unclear
- cropping mobile screenshots so the screen type or primary action disappears
- using `object-fit: cover` on dense proof screenshots just to fill a card

Preferred implementation:

- use `object-fit: contain` for dense screenshots, tables, chats, reports,
  diagrams, and dashboards
- use `object-fit: cover` only for real scene photos, decorative textures, or a
  deliberately labeled local zoom
- use restrained image corner radii. For proof screenshots, dashboards, tables,
  chats, and system UI images, prefer about `10px` radius. Keep image corners
  in the `8px - 12px` range unless the source UI itself strongly calls for
  another value.
- Do not give inner proof images the same large corner radius as the outer
  content card; large image rounding makes real screenshots feel decorative and
  can weaken evidence credibility.
- if full-image `contain` creates letterboxing, resize the container to match
  the image aspect ratio before switching to crop
- never stretch evidence images by forcing incompatible width and height values;
  preserve the source aspect ratio even inside scrollable viewports
- if a detail needs emphasis, keep the full image visible and add a zoom inset
  or highlight rather than replacing the full image with an unexplained crop
- if there is not enough space to show key images clearly, reduce text, remove
  weaker images, or split into another page

If a provided image already explains a section, reduce adjacent explanatory
text. Delete weak proof images, duplicated images, and decorative images that
compete with the main story.

When no strong asset exists, reconstruct a simple diagram from the source story
using Feishu-style components, but do not fabricate source facts.

### Interactive Evidence Image Policy

When producing HTML case cards with dense proof images, support two levels of
image viewing:

1. `In-card scroll viewport`:
   - Use a scrollable image viewport when a proof image is larger than its card,
     when the image is tall, or when shrinking it would make the proof unreadable.
   - Support vertical scrolling for tall screenshots, chat records, mobile
     screens, long tables, and reports.
   - Support horizontal scrolling for wide dashboards, tables, diagrams, and
     screenshots when the card cannot show the full width clearly.
   - Keep the image understandable in its card. Do not use scrolling to hide a
     bad asset choice or an overly small evidence area.

2. `Click-to-enlarge lightbox`:
   - Make meaningful proof images clickable when the output format supports
     interaction.
   - The enlarged view should show the complete image with `object-fit: contain`;
     it should not require additional vertical or horizontal scrolling.
   - Remove white container or background treatment in the enlarged view unless
     the source image itself has a white background. Use a dark translucent
     overlay and let the image occupy as much of the viewport as possible.
   - The enlarged image should be centered and should normally use about
     `80% - 90%` of the visible page area when the source aspect ratio allows it.
     Do not leave it as a small preview in the middle of a large overlay.
   - A blurred or dimmed page background is acceptable, but the blur must apply
     only behind the image. The enlarged foreground image itself must stay sharp
     and visually on top of the overlay.
   - In Feishu Deck raw pages, do not rely only on `opacity` or `display` to keep
     the lightbox closed; framework entrance styles may override them. Use a
     robust closed state such as `visibility: hidden` + `pointer-events: none`
     and verify the page is not blurred before any image is clicked.
   - Because Feishu Deck scales the 1920×1080 slide canvas, a lightbox placed
     inside a slide may be scaled down if it uses only `vw` / `vh`. Prefer a
     large canvas-sized viewport, for example about `1800×950` to `1840×1000`
     canvas px, so the displayed image still fills the intended page area.
   - Do not add extra instructional copy, extra controls, or decorative chrome.
     A minimal close control is acceptable, but closing must also work by
     clicking the enlarged image itself and by clicking the surrounding overlay.
     `Esc` close is recommended.
   - Use `zoom-in` and `zoom-out` cursor affordance when practical.
   - Closing the lightbox should return immediately to the original case page
     without changing the page layout or scroll state.

### Evidence Caption Policy

Every important evidence image should include a short interpretation caption.
The caption explains what the image proves, not where the image came from.

Choose the caption placement based on image role and available space:

1. `In-image caption`:
   - Preferred for one or two dominant proof images.
   - Place the caption inside the image area, usually as a bottom overlay, when
     it can bind the interpretation directly to the screenshot without covering
     key evidence.
   - If the image is small, crowded, information-dense, or the overlay would
     block the business object / key UI / proof text, move the caption above the
     image instead.

2. `Above-image caption strip`:
   - Preferred for dense multi-image evidence matrices, such as 2×2 proof grids.
   - Also use it when an in-image caption would make a small screenshot feel
     cramped.
   - Style it as a light-blue translucent strip with bold white centered text.
     Use the Feishu Deck type ladder, usually `24px` or `28px` (`28px` when the
     strip is the local proof title). Keep the caption short.

Caption rules:

- Keep it short enough to read in presentation mode; avoid full-sentence source
  notes or calculation notes under images.
- Prefer business capability language, such as `一店一群自动预警`,
  `异常原因自动汇总`, `AI 判断陈列与商品照片是否合规`, or `看板追踪执行结果`.
- Use captions to replace redundant paragraph explanation when the image already
  carries the proof.

Default compact below-image caption style for 16:9 raw case cards:

- about `16px` font size, `500` weight, `1.12` line-height
- compact padding around `10px 14px 12px`
- dark text such as `#18284f` on a light neutral background such as
  `rgba(248, 251, 255, 0.96)`
- keep the caption visually subordinate to the image and card title


## Metrics Rules

Use only source-backed metrics. Keep the final page to the most proof-heavy
3-6 numbers unless the user explicitly asks for more.

Promotion rule:

- only the most important `2-3` result metrics on a page should become strong
  stat cards
- background scale metrics should usually stay as inline tags, labels, or a
  short sentence
- do not cardize every number just because the source contains it

Every promoted metric should clearly serve one of these jobs:

- explain why the old way failed at scale
- prove the new mechanism changed the work
- prove the business value mattered

If a metric does not sharpen the story, demote it.

Prefer metrics that prove:

- Scale / coverage.
- Time saved.
- Cost saved.
- Cycle reduction.
- Automation rate.
- Accuracy / pass rate / execution rate.
- Volume processed.
- Revenue / conversion / retention / growth.
- Issue count / insight count / action count.

Numbers should serve the story. Do not include metrics just because they exist.

Metric hierarchy:

- `L1`: main result number; can appear in title, subtitle, or strong KPI card
- `L2`: supporting number; use as tag, side note, or compact inline metric
- `L3`: background or calculation detail; move to speaker notes or omit
  from the main page. Use a visible footer only when explicitly required

Each page should usually have no more than `2-3` L1 metrics. If metric cards
compete with the dominant proof visual, demote the weaker metrics before
shrinking the evidence.

For multi-page case decks, do not repeat the same metric band on every page.
Put the core result metrics on the page where they set up the story, then let
later mechanism / proof pages use that space for evidence unless a new metric
directly proves that page's distinct claim.

Metric card visual treatment:

- Core metrics / conclusion cards may use a stronger blue gradient background to
  distinguish result proof from ordinary content cards.
- The stronger metric background should highlight the value claim, not turn every
  module into a high-emphasis card.
- When the metric band sits between title and body, keep clear vertical gutters
  above and below it so it reads as a transition band, not as a frame overlapping
  either the title or evidence region.
- If the metric band competes with the dominant proof visual, reduce the number
  of promoted metrics or soften the less important cards before shrinking the
  evidence.

## Copy Rules

- Write for presentation, not full reading.
- Keep explanation text short.
- Let the speaker carry secondary details.
- Avoid long paragraphs.
- Use display phrases and compact labels.
- Avoid vague labels such as "solution" when a more specific action is known.
- Use customer/domain language when it improves clarity.
- Keep Chinese copy concise and natural.
- Avoid orphan / short-tail wrapping in display copy. This applies especially to
  page titles, subtitles, module titles, and key conclusion sentences. If the
  next line contains only one or two Chinese characters or punctuation, treat it
  as a copy/layout issue, not a harmless browser wrap.
- Fix short-tail wrapping by shortening redundant words, removing repeated
  labels already shown nearby, or tightening the phrase. Do not first solve it by
  shrinking only that line's font size.
- For subtitles, prefer reducing the sentence to the core mechanism and outcome.
  If a header already names the customer or page role, do not repeat those words
  in the subtitle.
- Example: if a card already has a `结果验证` tag, remove repeated title text
  such as `测试验证：` before considering font changes.

## Visual Density Rules

Avoid information explosion:

- Reduce text before shrinking fonts.
- Prefer fewer, stronger modules.
- Prefer images and diagrams over redundant explanation.
- Avoid nested cards unless they represent repeated items or framed tools.
- Avoid multiple equally strong focal points.
- Keep key numbers readable and separated.
- Do not trade crowding for dead space; both are layout failures.
- If the page feels empty in large bands, enlarge the anchor visual or rebalance
  the module grid before adding more modules.

If the page feels busy, remove content rather than adding more styling.

Do not copy the flaws of legacy sales-case posters:

- do not keep microtext that cannot be read in presentation mode
- do not add every available screenshot just because it exists
- do not let arrows, badges, and labels cover the actual evidence
- do not make a page depend entirely on speaker narration when the slide itself
  cannot show the claim and proof

What should be learned from good legacy case posters is:

- strong conclusion in the title
- visible business result
- real proof materials as the visual center
- clear left-to-right or top-to-bottom speaking path
- labels directly attached to the proof they explain

## Dead-Zone Audit

Before handoff, explicitly inspect for unused bands of space.

Check three things:

1. title-to-body gap
2. body-to-footer gap
3. whether the main narrative and evidence band visually occupies about
   `60% - 70%` of the usable page height, with the core metrics / conclusion
   band occupying about `8% - 12%`

If a top or bottom dead zone feels larger than about `6% - 8%` of the page
height, treat it as a layout issue that needs fixing.

Preferred fix order:

1. expand the dominant visual
2. rebalance the grid / card heights
3. compress title / subtitle area
4. reduce redundant helper copy
5. switch the page from absolute stacking to explicit row-grid layout if
   collisions persist

Do not justify large empty areas as "breathing room" unless that whitespace is a
deliberate part of the narrative emphasis and the user agrees with it.

## QA Checklist

Before handoff, verify:

- The page has background/pain, solution, before/after change, metrics, and
  evidence assets.
- The page has a clear `page role`, `one-line conclusion`, and `dominant proof`.
- The title or subtitle communicates the business conclusion when the source
  supports it.
- If a subtitle is present, it uses the case subtitle default (`30px`, `10px`
  visible title-to-subtitle spacing) unless there is a specific design reason to
  override it.
- The real story structure is represented correctly.
- The page can be understood in 5-10 seconds.
- There are no display-copy orphan lines where a second line contains only one
  or two Chinese characters.
- The title/subtitle area has been visually checked after render; subtitles do
  not end with a one-character or two-character tail line.
- Key images are clear enough to read at presentation size.
- Proof image corner radii are restrained, usually around `10px`, and do not
  make screenshots look like decorative cards.
- Evidence images are shown with the right display mode and are not accidentally
  cropped.
- Dense or oversized proof images use scrollable in-card viewports when needed.
- Click-to-enlarge proof images show the complete image on a dark overlay, do
  not add a white container background, do not require scrolling in the enlarged
  view, and close by clicking the image or overlay.
- Important evidence images have concise interpretation captions below them,
  using the default compact caption style unless the page design requires a
  clear exception.
- Every evidence visual has a clear proof job; decorative or unreadable images
  were removed, zoomed, or demoted.
- Numbers are not crowded.
- Only the most important metrics were promoted as stat cards.
- If the core metric band uses a strong blue gradient, it still remains
  subordinate to the main evidence visual and has clear gutters from neighboring
  regions.
- There is no canvas overflow.
- There is no module overlap.
- There is no background-frame overlap, ambiguous shared frame, or visually
  touching heavy containers.
- Every framed module clearly belongs to one region.
- There is no hidden overlap caused by subtitle/body spacing being left unused
  while lower zones collide.
- There is no obvious top or bottom dead zone caused by under-filled layout.
- The main content visually occupies most of the page, rather than floating in a
  smaller inner canvas.
- Text does not collide with controls, footnotes, or neighboring modules.
- The final HTML was rendered from `deck.json`.

If the normal Feishu Deck visual gate cannot run due to environment limitations,
use the allowed fallback visual QA path from the Feishu Deck skill and state the
limitation clearly.
