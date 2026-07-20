# 客户案例视觉契约

## 操作卡

- 产出：`DESIGN-PLAN.md` 的视觉契约段、`layout-plan.json.token_profile` 与确认过的 overrides。
- 命令：布局阶段运行 `validate_layout_plan.py`；渲染后运行 `validate_rendered_layout.py`。
- 红线：Token 只读 `assets/tokens/case-tokens.json`，缺失即阻断，不得内置回退值。
- 红线：用户覆盖必须写入已确认 `story-contract.json.approved_overrides`，布局计划只能原样引用。
- 红线：结果带只实现故事合同的语义决定，不得在视觉阶段重判。
- 红线：主导证据不可读、区域重叠、标题错位或大面积死区均阻断。

本文件是视觉实现的 Markdown 权威；所有数值以 `assets/tokens/case-tokens.json` 为准。

## 1. 稳定基线

默认 profile 为 `case-standard-v2`。使用基础 Deck 的内容背景、框架和字标；第一个可见文字是中文结论标题，紧邻一个副标题。默认不增加英文眉题、来源页脚、客户 Logo 或重复飞书 Logo。用户提供明确参考时可覆盖，但必须通过已确认故事合同中的 `approved_overrides` 表达。

页面必须先表达业务观点，再用证据证明。删除只能依赖演讲者解释的细节。

## 2. Token 引用

权威值见 `assets/tokens/case-tokens.json`。当前 profile 包括 `1920x1080` 画布、标题/副标题/正文层级、间距、圆角、纵横向预算、证据覆盖率、颜色、透明度及校验容差。文档与 JSON 不一致时以 JSON 为准。

不得使用 transform 模拟字号，不得使用负字距。不得创建独立注释轨道；必须展示的限制说明放入 Token 定义的底部安全区。

## 3. 卡片阅读顺序

模块顺序固定为：分区标题 -> 一条核心总结或机制流程 -> 证据图组。核心总结与流程必须位于图片上方；同级业务卡片标题须位于同一水平行。

说明模式与实现只见 `evidence-assets.md` §7。过去现状的 `stacked-cards` 必须有低权重但可见的表面与边界，并保持纵向业务顺序。

## 4. 自适应布局

根据已确认故事、主导叙事元素、证据优先级、真实宽高比和可读尺寸选择注册 recipe。注册表见 `assets/contracts/layout-recipes.json`；recipe 内部几何可按 `layout-archetypes.md` 自适应。无适用 recipe 时使用 `custom-v1` 并记录理由。

经典语法与流程优先例外只见 `layout-archetypes.md`。不得机械套用等宽列或因素材比例抹去已确认业务任务。

## 5. 结果带视觉实现

结果带是否出现、包含哪些 L1 指标，由 `source-and-story.md` §2 的故事合同决定。本节只定义 `required` 时的实现：

- 使用 `blue-result-cards-v1`，每个指标是一张独立等权卡，卡间距取 Token。
- 渐变、描边、禁用颜色、字体及容差全部读取 Token；不得出现紫色、多色或彩虹分卡。
- 外层保持透明且无第二层大边框；数值在左，标签紧随，实测/预计标记保持轻量。
- DOM 容器使用 `data-case-metric-band="blue-result-cards-v1"`。

结果带只承载不同证明任务的 L1 指标；baseline 数据留在局部详情。没有故事批准不得临时创建结果带。

## 6. 证据视觉

证据选择、构图配方、说明、滚动、裁剪与灯箱行为只见 `evidence-assets.md`。布局必须匹配真实方向，截图默认 `contain`，不得用 `cover` 或裁掉关键 UI 伪造填充感。

渲染后覆盖率、真实 source ratio 与可读宽度均由 collector 原始测量值和 Token 计算；不得采信 DOM 自报的“可读”布尔值。

## 7. 视觉阻断项

以下任一情况阻断：标题或同级卡片基线错位；总结位于证据下方；证据低于可读阈值；指标争夺主焦点；区域/背景框重叠；内容紧贴或溢出；语义阅读顺序反转；主导元素不占主导；出现超出 Token 的顶部/底部死区；说明覆盖关键 UI；用户 override 未绑定当前故事。

结构校验通过只是必要条件，人工截图检查仍须确认短尾换行、视觉密度和证据可读性。
