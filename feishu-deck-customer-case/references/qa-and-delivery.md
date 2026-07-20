# QA 与准确交付

## 操作卡

- 产出：`rendered-layout.json`、其 validation、截图、`interaction-check.json`、`QA-NOTES.md`、`qa-notes.json`、manifest、run validation。
- 命令：优先 `case_pipeline.py requalify --run-dir <RUN_DIR>`；人工停点按提示完成。
- 红线：机器采集不能替代人工视觉结论；pipeline 不得自动把 pending 改为 pass。
- 红线：collector 只采原始 CSS/几何，阈值由 Python + Token 判断。
- 红线：只验证最终准确 HTML；复制/内联后必须重新采集。
- 红线：任何 error、缺图、空白页、交互失败或哈希错配均阻断。

## 1. 校验顺序

1. 基础 Deck JSON/HTML 校验。
2. 浏览器加载、截图、控制台与图片加载检查。
3. 采集真实 DOM，运行 rendered layout 校验。
4. 实际执行滚动和灯箱交互。
5. 人工检查截图并完成 QA 叙述与 JSON。
6. `verify_delivery.py` 生成 manifest。
7. `validate_case_run.py` 验证全链。

任何产物重建或 BLOCKED 后，先运行 `case_pipeline.py status`；不得手工改哈希。

## 2. 基础 Deck 门禁

`deck.json` 是唯一渲染来源，`deck.deck_id` 必须等于 `case-state.json.deck_id`。运行基础 Deck 的 strict validator 和最终渲染；失败必须回写 DeckJSON/结构化计划后重跑，不得补丁式修改最终 HTML。

原始页面通过 `slide.layout="raw"` 的 `slide.data.html` 声明 `data-case-*`；基础 renderer 原样透传。示例：

```json
{"key":"case-1","layout":"raw","data":{"html":"<section data-case-page=\"page-1\" data-case-top-grid=\"true\">...</section>"}}
```

渲染前运行 `validate_deck_hooks.py`；回归由 `test_raw_hook_passthrough.py` 证明 deck.json -> index.html 钩子不丢失。

## 3. 浏览器与交互

`collect_case_qa.py` 使用本地 HTTP 和 Chromium 打开准确 HTML，等待字体/图片，采集 console error、截图、滚动与标准灯箱交互。最终页面必须使用：

- 证据触发器：`data-case-lightbox-trigger`
- 灯箱遮罩：`data-case-lightbox`
- 滚动证据：`data-case-display-mode="scroll"`

`interaction-check.json.target_html_sha256` 必须匹配最终 HTML。灯箱须打开完整图、点击图片或遮罩关闭，关闭后布局稳定；每个滚动视口记录真实方向与操作结果。

## 4. DOM 钩子

每个案例页必须暴露：

- `data-case-page`；唯一 `data-case-top-grid="true"`
- `data-case-region` + `data-case-role`
- `data-case-title`、`data-case-subtitle`、`data-case-peer-title`、`data-case-column-row`
- `data-case-block`
- `data-case-copy-role`：仅 module-title/summary/body/flow-node/metric-value/metric-label/caption
- `data-case-metric-id`、`data-case-metric-placement`、`data-case-metric-status`
- 批准时的 `data-case-metric-band="blue-result-cards-v1"`
- `data-case-evidence`、display mode、source ratio、caption mode
- 机制证据的 sequence、proof task；图组使用 `data-case-evidence-composition` 与 `data-case-evidence-composition-assets`
- `data-case-pain-treatment` 与 stacked 时的 `data-case-pain-point`
- `data-case-flow`、flow placement、flow container

## 5. 原始采集与判定

`collect_rendered_layout.js` 只返回计算后的原始字符串和几何：字号、矩形、CSS background/border/outline/shadow、natural/image-box 尺寸、overflow、DOM 位置和 data 声明。它不得判定“可见”“可读”或颜色是否合法。

运行：

```bash
python3 <skill>/scripts/validate_rendered_layout.py \
  --layout-plan <RUN_DIR>/output/layout-plan.json \
  --html <RUN_DIR>/output/index.html \
  --report <RUN_DIR>/output/rendered-layout.json \
  --output <RUN_DIR>/output/rendered-layout-validation.json
```

Python 从 Token 读取阈值，解析 CSS 颜色的逗号与空格/斜杠语法，使用 natural ratio 复算 coverage，核对 source ratio 声明，判定表面/边界、阅读顺序和可读宽度。模糊阅读顺序只产生 warning；不可读证据与几何错误产生 error。warning 本身不阻断。

## 6. 人工视觉检查

截图必须来自最终复制/内联之后。人工确认：页数与键；故事/证据一致；标题及卡片基线；无重叠、紧贴、溢出或死区；关键证据可读且未裁关键 UI；说明模式正确；无短尾换行；指标与主焦点关系正确。

Pipeline 完成客观采集后会创建 pending 的 `qa-notes.json` 并停止。制作人把观察写入 `QA-NOTES.md`，将六项 `checks` 逐项改为 `pass`，最后才设置顶层 `pass:true`。不得只改顶层 pass。

## 7. QA JSON

机器字段只存在 `qa-notes.json`：schema、pass、准确 HTML path/hash、base validator、空 limitations、截图路径、interaction/report 路径和六项 checks。`QA-NOTES.md` 只保留人读叙述并引用 JSON；旧的 `pass: true` Markdown 字段不再被接受。

推进：

```bash
python3 <skill>/scripts/case_state.py advance --run-dir <RUN_DIR> --to VALIDATED --artifact <RUN_DIR>/output/qa-notes.json
```

## 8. 准确交付

运行 `verify_delivery.py` 时明确 linked/single 与 viewer，验证 HTML 非空、资源完整、截图像素、交互报告及准确 hash。随后运行 `validate_case_run.py`；只有其 `pass:true` 且状态推进到 DELIVERED，才能宣称完成。
