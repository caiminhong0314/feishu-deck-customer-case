# 来源与故事契约

## 操作卡

- 产出：`SOURCE-NOTES.md`、完整 `STORY-REVIEW.md`、`story-contract.json`。
- 命令：`validate_story_contract.py` -> `case_state.py story-draft` -> 用户确认后 `story-approve`。
- 红线：只读取用户准确指定的来源；partial/blocked 不得继续。
- 红线：先完成来源与场景校准，再起草故事；发送完整审核稿后必须停止。
- 红线：指标分级、单位语义与结果带语义决定只在本文件 §2 定义。
- 红线：来源或故事哈希变化后必须重新确认。
- 红线：默认一页；两页必须满足 §7 并取得确认。

## 1. 准确来源

必须读取用户明确提供的文档、URL、附件或 token。相关材料、搜索结果、同客户其他文档、缓存摘要和预览不能替代准确来源。记录：来源 URL/token、本地文件、修订/哈希、获取时间、权限状态与缺失部分。

来源状态只有 `fetched`、`partial`、`blocked`。通常仅 `fetched` 可继续；无法读取时说明阻断点并停止，不得以推断补齐。

## 2. 主张、指标与结果带语义

每个对客主张必须标记：来源位置、事实/推断/估算、确定性、必要限定语。不得把试点写成全面上线、把计划写成已实现、把估算写成实测、把内部目标写成客户结果。

指标分级是本节唯一权威：

- L1：最强业务结果，可放标题、副标题或结果带。
- L2：辅助规模/过程结果，放行内或局部详情。
- L3：计算细节，放工作笔记或省略。

每个指标记录稳定 ID、原始值、展示文本、业务角色、单位语义、证据状态、来源和展示要求。`percentage` 与 `percentage-point` 必须区分；估算值展示“预计”或“测算”；baseline 不得冒充顶部结果。

`metric_band.decision` 的语义规则：当 `before-mechanism-result` 故事有 2-4 个来源支持、承担不同证明任务的 L1 指标，且这些结果应在进入证据前形成结论入口时设为 `required`；否则为 `optional` 或 `not-used`，并写明理由与指标 ID。视觉实现只见 `visual-contract.md` §5。

## 3. 可讲性检查

进入故事前确认材料至少支持：明确客户/业务场景、真实问题、变化后的机制、可验证结果或边界、至少一项可用证据。缺少机制、结果或证据时，应返回用户补充，而不是包装成完整案例。

记录需要客户确认的问题：范围、时间、口径、是否实测、匿名要求、对外可披露性、素材是否必须展示。

## 4. 初步场景

从来源记录可能的主场景/次场景，但不得在本阶段强行分类。随后按 `scenario-rules.md` 完成校准，并把采用规则、选择理由、匹配程度及 fallback 状态写回 `SOURCE-NOTES.md`。

## 5. 故事形态

故事审核稿必须回答：客户是谁、过去为何困难、什么机制改变了运行方式、结果如何被证明、边界是什么、哪些证据支撑关键转折。

来源同时包含过去问题、改变后的运行机制和可验证结果时，故事形态使用 `before-mechanism-result`。机制主导故事记录 2-5 个 `mechanism_turns`，每个标记 `visual-if-available` 或 `text-allowed`。故事形态是语义决定，不是 CSS。

## 6. 故事审核稿与结构化合同

`STORY-REVIEW.md` 至少包括：

1. 一句话结论与目标听众
2. 客户背景和范围
3. 过去问题
4. 当前机制及关键转折
5. 结果与指标台账
6. 证据计划方向
7. 页数、case grammar、recipe 建议
8. 结果带决定与主导业务任务
9. 不确定项、边界及待确认问题
10. 视觉 override（如有）及用户确认原文

`story-contract.json` 使用版本 2，并与审核稿 SHA256 绑定；记录 `token_profile`、`approved_overrides`、页数、grammar、recipe、主导任务、结果带、指标和机制转折。override 必须包含 `token`、`value`、`reason`、`user_confirmation`、`confirmed_in_story:true`，且 token 位于可覆盖白名单。

运行：

```bash
python3 <skill>/scripts/validate_story_contract.py --contract <RUN_DIR>/output/story-contract.json --story <RUN_DIR>/output/STORY-REVIEW.md
python3 <skill>/scripts/case_state.py story-draft --run-dir <RUN_DIR> --story-file <RUN_DIR>/output/STORY-REVIEW.md
```

将完整审核稿发送给用户后停止。只有用户明确确认当前稿件，才运行 `story-approve`。泛化的“开始做”、沉默、旧任务确认或 Agent 自述均无效。

## 7. 页数决策

默认一页。仅在用户明确要求两页，或一页无法同时保持关键证据可读且存在可分离的证据/并行故事时建议两页；必须把两页结构写入审核稿并重新确认。布局阶段不得自行增页。

## 8. 变更与恢复

来源修订、故事文本、页数、recipe、L1 指标、结果带、机制转折或 override 变化，均使确认及下游产物失效。先运行 `case_pipeline.py status`，从第一断点恢复；不得手工改写哈希。
