# 客户案例布局配方

## 操作卡

- 输入：已确认 `story-contract.json`、素材实际比例与优先级。
- 产出：`DESIGN-PLAN.md` 的方向选择；`layout-plan.json` 的 recipe、语法、流程位置和理由。
- 命令：`python3 scripts/validate_layout_plan.py --plan <layout-plan> --run-dir <RUN_DIR>`。
- 红线：recipe 必须注册于 `assets/contracts/layout-recipes.json`。
- 红线：经典语法保留问题、机制、结果三项业务任务；流程留在机制区。
- 红线：`process-first-v1` 必须有经故事确认的非空例外理由。
- 红线：页数只由 `source-and-story.md` 决定。

本文件是经典案例语法与自适应方向的唯一 Markdown 权威。

## 1. 默认案例语法

当故事包含过去问题、改变后的运行机制和可验证结果时，选择 `classic-case-card-v1`：

```text
标题/副标题 -> 已批准时的结果带 -> 问题 | 当前机制 | 结果验证 -> 底部安全区
```

三个业务任务必须都存在，但列宽按主导证据和真实比例自适应。流程是机制区内部组件，不是第四个顶层区域。机制是叙事重心时，机制列必须最宽。结果带语义决定见 `source-and-story.md` §2，视觉实现见 `visual-contract.md` §5。

只有以下条件全部满足才可使用 `process-first-v1`：故事明确将端到端流程本身视为主要证据；经典三幕会歪曲故事；原因已写入并确认；问题与结果仍可理解。不得仅因横向流程好排版而使用。

## 2. 注册 recipe

- `classic-case-card-v1`：问题 / 机制 / 结果三幕式，内部几何自适应。
- `evidence-first-v1`：单一证据明显强于其他素材时，以大证据为锚点。
- `paired-comparison-v1`：两张真正可比较的 Before/After 证据。
- `foundation-parallel-v1`：同一基础能力支撑多条并行业务线。
- `process-first-v1`：通过例外测试的流程主导案例。
- `custom-v1`：现有 recipe 不适用；必须记录为何无法使用其他配方。

机器注册表是 `assets/contracts/layout-recipes.json`。新增 recipe 时先改注册表、模板和契约测试，再更新本节。

## 3. 自适应原则

列宽、证据框数量和图片比例可调整，但必须满足 Token、容器归属、防重叠和主导证据可读性。常见方向：

- 单一证据主导：一张大证据，辅助证据只证明不同主张。
- 成对比较：两侧证据同权、标题与说明对齐。
- 经典三幕：机制列通常最大，两侧保持最低可读宽度。
- 基础 + 并行：基础能力只出现一次，业务线不得伪装成连续步骤。

具体数值只读 `assets/tokens/case-tokens.json`，不得在本文件复制阈值。

## 4. 两页与记录

两页只在用户明确要求或证据/并行故事满足 `source-and-story.md` 的条件并重新确认后使用。通常第 1 页讲问题与机制，第 2 页讲结果与边界；两页保持同一视觉契约。

布局计划记录：`page_count_reason`、`layout_mode`、`case_grammar`、`layout_recipe`、选择理由、流程位置、主导叙事元素、主导证据、指标处理、列角色权重、`evidence_composition: {"ref":"asset-plan"}`、容器几何、标题对齐与总结位置。
