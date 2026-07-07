# Product Surface Patterns

Read this reference when a skill-two case prototype needs an embedded Feishu /
Lark product surface on the right side of the Deck page.

This file complements `lark-design-prototype`: that skill provides Feishu /
Lark visual language and component discipline; this file maps customer-case
workflow steps to the right product surface and story state.

## 1. Surface Selection Rule

Before design, write a `product_surface_map`:

| Step | Business Action | Product Surface | Source Evidence | Primary Visual Object | State Change | Prohibited Content |
| --- | --- | --- | --- | --- | --- | --- |

Rules:

- Use the product surface implied by the business action, not the prettiest
  screenshot.
- Source screenshots for After are usually references for reconstructing the
  surface; do not paste them as the main After visual unless they are direct
  result proof.
- Before screenshots can be used directly when they prove the old pain.
- Keep the same group name, store ID, SKU, dataset, owner, date, and status
  across steps unless the source changes them.
- Do not put internal design notes or source-role explanations on the case page.

## 2. IM / Group Chat Pattern

Use for:

- bot reminders
- store feedback
- photo upload
- voice reply
- AI cards posted to a group
- human follow-up in a shared work group

Required anatomy:

- top chat header with group name, member count / status, and light toolbar
- tabs or shortcuts only when useful: Message, Pin, Docs, Images / Videos
- message area with time separator, avatars, sender names, bot badges, and
  message cards
- realistic message bubbles, image thumbnails, voice chip, transcript, and
  lightweight action buttons
- input bar at bottom when the state is about communication

Step rules:

- `10:00预警`: show one bot notification card and the target store / SKU. Do not
  show the later upload photo in this state.
- `门店上传`: show photo upload first, then voice message / transcript if the
  story uses reason collection, then a recorded / write-back confirmation.
- `原因反馈`: if it is still a store reply, it can live in the same chat. If the
  story has moved to analysis, use an analysis panel, not another plain chat.

Avoid:

- duplicate sidebars that list the same steps as the Deck flow controls
- generic chat bubbles without Feishu-like header, avatars, cards, and input
- oversized internal title rows that repeat the Deck heading
- hiding the primary photo / voice / confirmation below scroll

## 3. Base / Multidimensional Table Pattern

Use for:

- record collection
- structured write-back
- AI validation / inspection status
- owner tracking
- issue workflow state
- attachment and field-based review

Required anatomy:

- workspace title or table name, but keep it compact inside Deck
- view list or view tabs when they help comprehension
- top toolbar with filter / sort / group / search / action affordances
- field columns, records, selected row, status tags, owner, dates, and
  attachment thumbnails
- optional right detail drawer only when it clarifies the selected row

AI validation variant:

- show fields such as attachment, image translation / recognition, AI validation
  status, feedback result, voice reason, owner, and automatic action
- highlight one row as the current story object
- show status changing from pending to passed / failed / follow-up
- if there is a right detail drawer, it supports the selected row; it is not the
  main visual subject

Avoid:

- using a generic card list when the story is about record and status flow
- duplicating the left-side field list and right-side detail list with the same
  labels
- making the table too small to read while leaving large empty space elsewhere
- replacing a Base workflow with a static screenshot if a reconstructed table
  would explain the mechanism better

## 4. Dashboard / Result Board Pattern

Use for:

- result verification
- performance comparison
- issue trend / distribution
- operation cockpit
- management follow-up

Required anatomy:

- title / scope / period or filter
- 1-2 top metrics with deltas
- at least one chart: bar, line, ranking, funnel, distribution, or comparison
- one insight / decision card that states what action follows
- optional table only as supporting detail

Avoid:

- list-only result pages
- KPI walls with no chart or decision
- charts that are too decorative to prove the case
- repeating every source number instead of the 1-2 numbers that serve the story

## 5. Step Mapping Examples

For retail store execution / inspection cases:

- `10:00预警`: Feishu IM group, bot notification card, target store / SKU.
- `门店上传`: Feishu IM group, store photo + voice + transcript + recorded card.
- `AI验收`: Base table, selected record with attachment, AI recognition,
  validation status, feedback result, and automatic write-back.
- `原因归因`: analysis surface, reason tags, owner, chart, and follow-up action.
- `结果看板`: dashboard, AB comparison or trend, metrics, chart, insight.

For price / procurement cases:

- `异常发现`: dashboard or Base exception list.
- `责任确认`: IM / task / approval surface, owner and follow-up.
- `谈价建议`: AI assistant / Docx / Base detail panel with recommendation.
- `闭环追踪`: Base table or dashboard status flow.

For knowledge / SOP cases:

- `标准沉淀`: Wiki / Docx / Base rule library.
- `执行采集`: IM / audio / form / Base record.
- `AI对照`: Base or dashboard showing SOP match / gap.
- `整改闭环`: task / IM reminder / dashboard progress.

## 6. Product Surface QA

Before handoff, check:

- Can a viewer identify the intended Feishu product surface within three
  seconds?
- Does each step show a distinct state, not only a different tab label?
- Is the primary visual object visible without internal scroll?
- Are source screenshots used according to role: Before evidence, After
  reference, or result proof?
- Does the UI avoid generic SaaS panels when IM / Base / Dashboard is implied?
- Are duplicated titles, redundant sidebars, and explanation rows removed when
  they waste prototype space?
- Does zoom enlarge the full product window or important object, then return to
  the Deck quickly without changing state?
