# Changelog

## v2.0.0 - 2026-07-20

- 新增 `case-tokens.json` 与 `layout-recipes.json` 两个机器真源；校验器缺配置即阻断，不再使用内置默认值。
- 布局 warning 改为记录但不阻断；证据不可读与几何失败升级为明确 error。视觉 override 必须绑定当前已确认故事。
- collector 只采原始 CSS、natural image 和几何值；Python 统一解析颜色、透明度、表面、source ratio、coverage 与阅读顺序。
- 新增稳定 `deck_id`、阶段依赖 hash、rewind、`case_pipeline.py status/next/requalify` 及标准浏览器 QA 采集。
- 证据构图只在 asset plan 定义；layout plan 使用 `{"ref":"asset-plan"}`，消除逐字段复制。
- 证明基础 Deck 的 raw `slide.data.html` 会原样透传 `data-case-*`，并增加渲染字节确定性回归。
- 机器 QA 从 Markdown 正则迁移到 `qa-notes.json`；`QA-NOTES.md` 仅保留人工观察。
- 回归 fixture 强制位于 skill 与 RUN_DIR 之外；评测无人值守增加 prompt/env、`evaluation-mode.json` 和规范路径三重校验。
- Reference 正文从 1608 行降到 650 行（约 60%），每阶段增加操作卡并删除跨文件重复规则。

### Breaking migration

- `story-contract.json`: version 1 -> 2；新增 `token_profile`、`approved_overrides`。
- `layout-plan.json`: version 7 -> 8；删除内嵌 `tokens`，证据构图改为 asset-plan 引用。
- `rendered-layout.json`: schema 1 -> 2；保存原始 CSS/图片几何，不再保存 collector 判定布尔值。
- `case-state.json`: schema 1 -> 2；新增稳定 `deck_id` 和依赖 hash。旧 run 应新建状态或按新合同重新资格化。
- `QA-NOTES.md` 机器字段停止支持；改用 `qa-notes.json`。

## v1.0.0 - 2026-07-10

- 将技能重构为单一稳定版本，删除 1.1 并停止维护并行规则分支。
- 增加 `case-state.json` 状态机：当次故事未经明确确认时，设计与渲染命令直接阻断；来源或故事变化后自动作废旧确认。
- 将规则按来源与故事、图片证据、场景、版式、验证交付和维护评测拆分为阶段化参考文件，减少一次性上下文负担。
- 增加图片证据计划校验：每张选用图片必须说明证明结论、页面优先级、完整展示/滑动/裁剪策略和说明文字模式。
- 固化标题、版面比例、容器所有权、图片圆角、图片说明、滑动与完整图放大等案例页面规则。
- 增加最终交付验证：检查确切 HTML、关联资源、文件大小、截图像素和交付清单，阻止空页面、错路径和缺失资源进入交付。
- 增加状态门禁、证据计划和交付验证的自动化回归测试。

## v0.1.0 - 2026-07-04

- 发布 Feishu Deck-Customer Case 初始正式版。
- 支持先梳理可汇报故事，再生成客户案例卡片。
- 增加图片证据展示、滑动查看、点击放大、完整图展示规则。
- 增加案例制作的人工作业边界：AI 可以提炼和排版，但案例重点、关键素材与对客讲法需要人工确认。
