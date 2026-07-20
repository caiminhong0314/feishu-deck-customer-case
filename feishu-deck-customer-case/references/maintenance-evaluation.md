# 维护、评测与发布

## 操作卡

- 产出：影响扫描、契约测试、前向/对抗样例、回归分类、发布说明。
- 命令：`run_contract_tests.py`、`quick_validate.py`、外部 fixture 回归、Git diff/status。
- 红线：独立分支；不覆盖用户未提交改动；不维护并行活动版本。
- 红线：规则单一权威，其余位置只留指针。
- 红线：回归 fixture 必须物理位于 skill 与 RUN_DIR 之外。
- 红线：发布前必须获得用户明确授权；失败版本不得安装或打 tag。

本文件只在技能维护、评测和发布时读取。

## 1. 修改前影响扫描

先用 `rg` 搜索规则、字段、数值、模板和脚本引用，列出影响面。每条规则只保留一个 Markdown 权威与一个机器真源；数值统一进入 `assets/tokens/case-tokens.json`，recipe 统一进入 `assets/contracts/layout-recipes.json`。

涉及 schema 时同步更新：模板、所有读取脚本、状态机、最终链校验、契约测试、迁移说明和版本号。不得以兼容默认值掩盖缺字段。

## 2. 测试层级

每次修改至少运行：

```bash
python3 scripts/run_contract_tests.py
python3 scripts/run_browser_contract_tests.py
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

校验器行为变化还须增加合法变体与非法对抗用例。浏览器/渲染变化须验证：非空截图、DOM 钩子、真实几何、交互、同一 deck 两次渲染的 index.html 字节一致性。

前向样例至少一个清晰来源案例和一个高风险案例；高风险覆盖长标题、竖长/横宽证据、估算指标、弱证据或多图因果顺序中的至少两项。

## 3. 回归夹具物理隔离

隐藏 fixture 目录必须位于技能目录与任何案例 `RUN_DIR` 之外，建议 `<skill-parent>/case-fixtures/`。不得复制到 skill、运行目录、prompt、SOURCE-NOTES、故事合同、布局计划或 Agent 可读上下文。

验证命令必须提供 run dir：

```bash
python3 scripts/validate_regression_contract.py \
  --fixture <external-case-fixtures>/<case>.json \
  --layout-plan <RUN_DIR>/output/layout-plan.json \
  --run-dir <RUN_DIR>
```

脚本发现 fixture 位于 skill 或 RUN_DIR 内会直接阻断。隐藏字段只能由回归 runner 在生成完成后读取。

## 4. 回归判定

检查页数、grammar、recipe、主导任务、指标处理、关键证据顺序、story roles、容器几何与最终截图。差异分类：

- `intended`：本次规则修复直接导致且满足验收。
- `content-driven`：来源/证据真实差异导致的允许自适应。
- `regression`：故事、证据、可读性、几何或交付门禁退化。

regression 必须修复；不得通过改 fixture 接受失败。视觉变化记录 before/after hash 与分类理由。

## 5. 规则维护

Reference 顶部操作卡不超过 15 行，只写产物、命令和硬红线。正文保留 rationale，不复制其他文件的规则。新增规则时先确定权威归属，再把其他位置改成一行指针。

执行顺序保持：状态 -> 来源 -> 场景 -> 故事确认 -> 素材 -> 视觉 -> recipe -> 具体布局 -> 渲染 -> QA/交付。不得为了方便把后期规则移到早期并增加上下文负担。

## 6. 发布

1. 在独立 `codex/` 分支完成修改。
2. 契约测试、quick validate、前向/对抗样例与回归全部通过。
3. 检查工作树，仅暂存本次文件。
4. 更新 README、CHANGELOG 和语义化版本说明。
5. 安装为唯一活动技能并复跑校验；不得留下并行版本。
6. 获得用户明确授权后提交、tag、push。

发布说明列出 breaking schema、迁移步骤、intended/content-driven 差异、基础 Deck 钩子透传与确定性结论、残余风险。
