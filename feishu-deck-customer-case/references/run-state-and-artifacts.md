# 运行状态与产物

## 操作卡

- 产出：唯一 `RUN_DIR`、`OUTPUT_DIR`、版本 2 `case-state.json` 与稳定 `deck_id`。
- 首命令：`case_state.py init`；恢复命令：`case_pipeline.py status` / `next` / `requalify`。
- 红线：`OUTPUT_DIR` 必须严格为 `<RUN_DIR>/output`，不得创建第二运行目录。
- 红线：状态只能按顺序推进；产物或依赖 hash 变化必须 rewind/requalify。
- 红线：任何 BLOCKED 后先跑 status，禁止手工改哈希。
- 红线：无人值守须同时满足标记、harness 文件和路径三重条件。

## 1. 目录

提示词给出 `/output` 绝对路径时，其父目录为 `RUN_DIR`；给出运行目录时，输出固定为其 `output/`；否则使用基础 Deck `new-run` 返回路径。所有输入、状态和工作产物只在该目录内完成。

复制、发布、上传、发消息或 GitHub 操作不属于本地收尾，必须有用户明确授权。

## 2. 状态机

```text
NEW -> SOURCE_FETCHED -> STORY_DRAFTED -> STORY_APPROVED
    -> ASSET_PLANNED -> RENDERED -> VALIDATED -> DELIVERED
```

`case-state.json` 记录 run/output、稳定 `deck_id`、故事 hash、阶段产物 hash 及依赖 hash。`deck.json.deck.deck_id` 必须在渲染前通过 `case_pipeline.py stamp-deck` 写入；不得复制其他 deck ID。

## 3. 必需产物

```text
case-state.json
input/SOURCE-NOTES.md
output/STORY-REVIEW.md
output/story-contract.json
output/asset-plan.json
output/asset-validation.json
output/DESIGN-PLAN.md
output/layout-plan.json
output/layout-validation.json
output/outline.json
output/deck.json
output/index.html
output/rendered-layout.json
output/rendered-layout-validation.json
output/interaction-check.json
output/QA-NOTES.md
output/qa-notes.json
output/delivery-manifest.json
output/run-validation.json
```

截图路径记录在 QA JSON 和 manifest；多页可使用多张截图。

## 4. 初始化与推进

```bash
python3 <skill>/scripts/case_state.py init --run-dir <RUN_DIR> --output-dir <RUN_DIR>/output --source-url <url>
python3 <skill>/scripts/case_state.py source --run-dir <RUN_DIR> --status fetched --revision <revision>
python3 <skill>/scripts/validate_story_contract.py --contract <RUN_DIR>/output/story-contract.json --story <RUN_DIR>/output/STORY-REVIEW.md
python3 <skill>/scripts/case_state.py story-draft --run-dir <RUN_DIR> --story-file <RUN_DIR>/output/STORY-REVIEW.md
python3 <skill>/scripts/case_state.py story-approve --run-dir <RUN_DIR> --story-file <RUN_DIR>/output/STORY-REVIEW.md --confirmed-by user --confirmation-text "<confirmation>"
```

设计/渲染/交付前使用 `case_state.py gate`。阶段产物通过后使用 `advance`；VALIDATED 的 artifact 是 `qa-notes.json`，不是 Markdown。

任何阶段被 BLOCKED 或产物重建后：

```bash
python3 <skill>/scripts/case_pipeline.py status --run-dir <RUN_DIR>
python3 <skill>/scripts/case_pipeline.py next --run-dir <RUN_DIR>
```

status 输出第一断点和带真实路径的修复命令。`requalify` 自动执行可重复校验与浏览器采集；遇到人工视觉判断会生成 pending JSON 并停止。人工完成后再次 requalify 才继续 manifest 与 run validation。

最终链仍由 `scripts/validate_case_run.py --run-dir <RUN_DIR> --output <RUN_DIR>/output/run-validation.json` 判定，任何自定义检查都不能替代。

## 5. 失效规则

来源变化清空故事确认及全部下游；故事变化回到 STORY_DRAFTED；asset/layout/deck/html/QA/manifest 或任一记录依赖 hash 变化，从最早受影响阶段 rewind。不得以重写 report/hash 绕过。`case_pipeline.py requalify` 负责按依赖顺序恢复。

## 6. 评测实验室例外

无人值守只绕过人工故事暂停，且必须同时满足：

1. 调用参数或环境为 `EVALUATION_MODE=unattended`；
2. `RUN_DIR/evaluation-mode.json` 由 harness 原子写入，包含 schema 1、`created_by: feishu-case-evaluation-workbench`、mode、run id、created_at 与准确 output_dir；
3. 路径严格为 `*/技能实验室/data/runs/run-<id>/output`。

确认命令使用 `--confirmed-by evaluation-harness --confirmation-text "unattended evaluation run" --evaluation-mode unattended`。普通“测试”字样、聊天历史、缺 marker 或其他路径均不得接受。

评测模式不改变页数、视觉、来源、证据或交付门禁，也不得读取 `expected_*` 隐藏字段。
