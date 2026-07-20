---
name: feishu-deck-customer-case
description: |
  根据 CSM 文档、客户成功材料、截图和飞书/Lark 文档生成或编辑飞书/Lark 风格
  客户案例卡片。适用于客户案例、案例卡片、一页纸案例、两页案例、CSM 文档转案例、
  Before/After 案例、客户成功案例、行业案例、场景案例复盘和证据型 HTML 案例页面。
  工作流必须读取准确来源，向用户提交可汇报故事并获得本次运行确认，规划证据素材，
  通过已安装的 Feishu Deck 技能渲染，并在交付前验证准确的最终产物。
---

# Feishu Deck-Customer Case

通过带门禁、以证据为核心的工作流构建面向客户的案例卡片。本技能是基础 Feishu Deck
引擎之上的案例设计配置，不是替代渲染器。

## 强制依赖与职责边界

开始任何工作前，定位并阅读已安装的飞书/Lark HTML Deck 技能。规范上游项目为
`https://github.com/FuQiang/feishu-deck-h5`；本地名称可能是 `Feishu Deck 0613`、
`feishu-deck-h5` 或其他等价名称。如果没有安装等价技能，停止并请用户安装。

- 基础 Deck 负责 DeckJSON、画布、母版背景、飞书框架、渲染器、框架资源、基础校验器
  和打包。
- 本技能负责来源完整性、业务故事、本次运行确认、一页适配、证据选择、案例构图、图片
  行为和对客表述边界。
- 真实证据需要证据型原始页面时，本技能可以覆盖通用故事案例模板，但仍使用基础引擎和
  渲染器。
- `deck.json` 是唯一事实来源。不得把手工修改的最终 HTML 当作权威版本。
- `story-contract.json`、`asset-plan.json` 和 `layout-plan.json` 是从已确认故事到最终 DOM 的
  结构化决策链。渲染器不得以手工 CSS 或临时脚本改变其中的页面语法、指标、证据顺序或布局配方。

## 不可协商的原则

- 读取用户准确提供的来源。相关材料不得替代被阻断或只读取部分的来源。
- 发送完整的当前故事审核稿，然后在设计或 HTML 生成前停止。
- 只有用户已经看到并明确确认当前故事，且来源版本和故事文件哈希未变化时，确认才有效。
- “开始生成”“直接做”“重新做”、沉默、历史聊天确认或其他运行的确认都不能绕过故事门禁。
- 默认一页。两页方案必须遵守 `source-and-story.md` 的页数决策并取得用户确认。
- 通过 DeckJSON 和基础 Deck 管线完成渲染与修复。
- 验证用户最终打开路径上的准确产物。任何失败门禁都会阻断交付。
- 只有 `scripts/validate_case_run.py` 针对准确运行目录通过后，才能宣称案例完成或交付 HTML。
  自定义截图、Playwright 或临时 QA 脚本只能补充标准 QA，不得取代它。
- 除非用户另行明确要求，不得发布、上传、发送消息或把案例导入外部系统。
- 将 Reference 信息架构视为技能维护契约。每次新增、删除或迁移规则，都必须保持渐进式
  阶段顺序、单一权威文件边界和每份 Reference 内部既定的优先级顺序；必须遵循
  `maintenance-evaluation.md`，不得为了方便随意追加规则或在多个文件中重复定义。

唯一的无人值守例外是 `references/run-state-and-artifacts.md` 定义的准确测评条件，
不得自行推断。

## 渐进式生成工作流

按照以下顺序加载 reference，不得在开始时一次性加载全部文件。

### 阶段 0：初始化运行

完整阅读 `references/run-state-and-artifacts.md`。仅在尚未存在运行目录时创建基础 Deck
运行目录，初始化状态，并持久化规范的 `RUN_DIR` 及其唯一的 `OUTPUT_DIR`。

退出条件：状态为 `NEW`，规范路径和稳定 `deck_id` 已记录。

### 阶段 1：理解来源

执行 `references/source-and-story.md` 第 1-5 节：获取准确来源、应用主张边界、检查业务
可讲性、识别不确定信息和客户追问，并记录初步场景分类。

退出条件：`input/SOURCE-NOTES.md` 已记录准确来源状态和初步场景。通常只有 `fetched`
状态能够继续。此阶段不得创建 `STORY-REVIEW.md`。

### 阶段 2：校准场景

阅读 `references/scenario-rules.md` 的路由契约，然后执行匹配的主场景章节、一个必要的
次场景章节或“自定义/未覆盖”兜底。不得把未覆盖案例强制归入已有分类。

退出条件：`input/SOURCE-NOTES.md` 已记录已校准的主场景/次场景、采用规则清单、选择理由、
匹配程度和兜底状态。

### 阶段 3：起草并确认故事

返回 `references/source-and-story.md` 第 6-8 节。通过模板创建完整 `STORY-REVIEW.md` 和与其哈希绑定的
`story-contract.json`，其中包括已经确认的业务故事形态、页面配方决策、指标台账和机制关键转折。故事形态是语义决策，不是 CSS 布局：
当来源明确包含过去问题、改变后的运行机制和可验证结果时，使用
`before-mechanism-result`。发送给用户后停止。

审核稿还必须明确页面叙事重心、机制关键转折、哪些转折需要真实图片，以及每个数字的业务角色、单位
语义、证据状态和展示层级。结构化契约中的 L1 指标、顶部结果带决定和关键转折在用户确认后不得由
素材选择、布局或 CSS 阶段自行降级、删除或改写。

有效的本次运行确认前，不得创建设计计划、大纲、DeckJSON、页面片段或 HTML。来源或
故事发生变化后，原确认失效。

退出条件：状态为 `STORY_APPROVED`，设计门禁通过。

### 阶段 4：规划证据

完整阅读 `references/evidence-assets.md`。建立完整候选素材清单：每一张可用素材均须标记为入选或拒绝，
拒绝必须有业务原因。把候选素材分类为 Before、After、Value 或 Weak/Decorative，为每项入选素材指定
主张和展示行为。对线性机制，先记录完整关键转折，再只为帮助理解闭环的关键图片分配顺序和证明任务；
不得将每个节点都强制配图。创建并校验 `asset-plan.json`。

退出条件：状态为 `ASSET_PLANNED`，每张入选图片都有明确的证据任务。

### 阶段 5：建立视觉契约

完整阅读 `references/visual-contract.md`。它是固定视觉数字、空间范围、卡片阅读顺序和
视觉阻断项的唯一 Markdown 权威来源。

把 `assets/templates/DESIGN-PLAN.template.md` 复制到 `output/DESIGN-PLAN.md`，完成其中
已确认故事和视觉契约部分。

退出条件：设计计划记录了当前视觉契约和所有经过明确确认的例外。

### 阶段 6：选择布局方向

完整阅读 `references/layout-archetypes.md`。先解析必需的默认案例语法和具体 `layout_recipe`，再考虑自适应选项。
已确认的 `before-mechanism-result` 故事从“结果带 + 三幕式构图”开始；流程优先页必须满足
该 Reference 定义的例外并记录理由。随后基于已确认故事、证据优先级和来源素材的实际宽高比，
选择已注册的 `layout_recipe`。注册表见 `assets/contracts/layout-recipes.json`；recipe 内部的列宽、证据框数量和图片比例可按已确认故事自适应。不适用现有 recipe 时使用 `custom-v1`，并在故事合同与布局计划中记录理由。

把选择/调整后的布局方向和选择理由补充到同一份 `output/DESIGN-PLAN.md`。

退出条件：设计计划骨架已记录布局方向和选择原因。

### 阶段 7：构建具体布局

完整阅读 `references/layout-and-copy.md`。完成阶段性创建的 `DESIGN-PLAN.md`，而不是重新
创建它；再创建 `layout-plan.json` 并运行 `scripts/validate_layout_plan.py`。布局计划必须记录
案例语法、布局配方、流程位置、叙事重心、指标的证明角色/单位语义/展示位置、几何、背景归属、证据优先级、
机制证据阅读顺序、对素材计划中证据构图的引用、说明模式、过去现状呈现方式、标题行对齐和“核心总结位于证据上方”的顺序。

退出条件：布局校验通过且不存在 error。warning 保留在报告中但不阻断；证据不可读直接归类为 error。

### 阶段 8：通过基础 Deck 渲染

编写 DeckJSON 前，重新阅读 `visual-contract.md` 和所选布局选项，再重新阅读已确认故事、
素材计划、设计计划、布局计划和大纲。通过基础 Deck 的设计优先、DeckJSON 优先管线
进行渲染。原始页面通过 DeckJSON `slide.data.html` 暴露 `qa-and-delivery.md` 所需的语义测量钩子：一个顶层案例网格、命名区域、
同级标题、证据图、指标、文案层级和可测量内容块。机制链中的每张证据图还必须暴露序号和证明任务，
供渲染后校验其实际阅读顺序、构图和过去现状小卡片。任何校验失败都必须在上游结构化计划或 DeckJSON 中修复并重新渲染；
不得仅修改最终 HTML 或用临时 CSS 覆盖。

退出条件：状态为 `RENDERED`；浏览器确认页面非空白的责任属于阶段 9，再进行校验和交付。

### 阶段 9：校验与交付

完整阅读 `references/qa-and-delivery.md`，并重新阅读作为视觉权威的 `visual-contract.md`。优先运行
`scripts/case_pipeline.py requalify` 执行基础校验、浏览器采集、截图、交互和渲染后布局校验；它在人工视觉判断处必须停止。

把人工观察写入 `QA-NOTES.md`，逐项完成 `qa-notes.json` 后推进到 `VALIDATED`；再创建交付清单并运行 `validate_case_run.py`。
自定义检查不能替代该最终运行校验。

退出条件：只有准确的交付清单和 `run-validation.json` 均通过后，状态才能进入 `DELIVERED`。

### 仅用于维护

只有进行技能测评、回归或发布时才读取 `references/maintenance-evaluation.md`。它不属于
普通案例生成上下文。

## Reference 职责

- `run-state-and-artifacts.md`：运行目录、产物、状态命令、门禁、测评例外。
- `source-and-story.md`：来源完整性、可讲性、故事、主张、指标台账、布局配方决策和页数。
- `scenario-rules.md`：条件场景校准和“自定义/未覆盖”兜底。
- `evidence-assets.md`：证据选择、完整图片、滚动、放大和说明模式。
- `visual-contract.md`：固定视觉数字和跨案例视觉原则的唯一 Markdown 权威来源。
- `layout-archetypes.md`：默认案例语法、自适应故事/证据布局方向，以及流程优先例外。
- `layout-and-copy.md`：具体构图、文案、几何和防重叠方法。
- `qa-and-delivery.md`：准确产物的浏览器、截图、交互和交付验证。
- `maintenance-evaluation.md`：仅用于回归和发布治理。

## 人工判断边界

AI 可以组织故事、推荐证据并生成页面。案例负责人仍须对业务主张、证据优先级、指标
确定性和对客重点负责。用户对图片选择或重点的修正应被视为故事信号修正，而不只是视觉反馈。
