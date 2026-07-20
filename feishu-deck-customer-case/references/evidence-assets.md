# 证据素材契约

## 操作卡

- 产出：完整候选清单 `asset-plan.json` 与 `asset-validation.json`。
- 命令：`python3 scripts/validate_asset_plan.py --plan <asset-plan> --run-dir <RUN_DIR>`。
- 红线：每个候选素材均须 selected/rejected；拒绝必须有业务理由。
- 红线：每张入选图须声明主张、优先级、展示模式、说明模式和稳定本地路径。
- 红线：机制证据构图与节点映射只在本文件 §2 和 asset plan 定义。
- 红线：截图默认完整 `contain`；裁剪必须有业务原因。
- 红线：关键证据不可读时返回素材/故事阶段，不得靠缩小或 `cover` 解决。

## 1. 候选清单与选择

素材计划是完整候选清单。每项记录稳定 ID、来源、可用性与选择决定；入选项还须记录页面、证明角色（before/after/value/weak）、具体 claim、优先级（dominant/supporting/optional）、展示模式（contain/crop/scroll）、布局语境、说明模式、说明文案、用户是否指定及裁剪原因。

选择顺序：用户指定证据 -> 真实截图/聊天/表格/报告/现场照片 -> 同时展示业务对象与环境的图片 -> 演示尺寸下仍可理解的素材。不得因等宽或整洁而拒绝关键证据；弱、重复、不可读或不能证明主张的素材应拒绝。

每页必须且只能有一张主导视觉证据。主导叙事元素可以是证据、流程或指标，但只有故事明确批准时流程/指标才可取代证据成为页面焦点。

## 2. 机制证据构图

机制故事在 `mechanism_evidence.evidence_composition` 中定义唯一构图真源；`layout-plan.json` 只写 `{"ref":"asset-plan"}`。

- `single-dominant`：一张主证据说明关键转折，其余节点用流程文字。
- `paired-comparison`：两张同权、可直接比较的证据。
- `process-sequence`：两至四张证据按因果/时间顺序排列。
- `dominant-plus-supporting`：一张主图，辅助图只补充不同转折。
- `parallel-matrix`：两张以上真正同级、需要横向比较的证据。

`asset_ids_in_visual_order` 只列解释机制的关键图片；`node_mapping` 将每张图映射到一个或多个真实转折并说明理由。`turn_coverage` 为每个关键转折记录 evidence 或 text；存在可读且直接的候选证据时，`visual-if-available` 不得无理由降为文字。总图数通常一至四张，不要求逐节点配图。

不得因剩余空间打乱因果顺序或把不同方向截图塞进无关小格。先确定证明链，再按真实比例分配空间。

## 3. 主导证据与标注

辅助证据只有证明不同主张时才保留，通常一至三张。标签必须命名具体证明任务，例如“AI 自动检核”“异常提醒”“责任人触达”，不得覆盖关键 UI，也不得用箭头补救不可读截图。

## 4. 完整图片与裁剪

截图、聊天、表格、仪表盘、报告、图示和手机页面默认 `object-fit: contain`。只有现场照片、装饰媒体或已说明的局部放大可用 `cover`。

裁剪仅在关键 UI、标题、发言人、图表/表格上下文仍完整可理解，且删除内容只是留白或重复细节时允许；必须记录 `crop_reason`。不得拉伸图片。页数不足时返回故事阶段重新确认。

## 5. 滚动视口

缩小会破坏可读性时：长聊天、手机页、报告与长表格用纵向滚动；宽仪表盘、表格与图示用横向滚动。初始视图仍须表达主张，滚动不能补救错误选材或过小容器。

## 6. 点击放大

有意义的证据图片须支持灯箱，并暴露 `data-case-lightbox-trigger` 与 `data-case-lightbox`。放大图使用 `contain`，位于深色半透明画布遮罩中，清晰且无需额外滚动；点击图片或遮罩即可关闭，关闭后布局与滚动状态不变。关闭态使用 `visibility:hidden` 与 `pointer-events:none`，建议支持 Esc。

## 7. 说明模式

每张重要证据图只有一种说明模式：

- `in-image`：主导图、Before/After 或非均匀构图。白色半透明说明条附着在图片底部，颜色、alpha、字号与 padding 只读 Token；只保留底部圆角，不覆盖关键证据。
- `above-image`：仅用于真正同级的 `parallel-matrix`，或底部说明会覆盖关键证据时；同级标签须同一水平行。

每条说明直接写“该图证明什么”，通常一行、最多两行。不得同时使用两种模式，不得变成第二个模块标题。语义与模式由本节决定，数值实现只见 `assets/tokens/case-tokens.json`。
