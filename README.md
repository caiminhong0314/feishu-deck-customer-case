# Feishu Deck-Customer Case

**Feishu Deck-Customer Case｜10分钟制作客户案例一页纸**

基于 CSM 文档、客户成功材料和案例素材，先梳理可汇报故事，再生成飞书风格客户案例卡片。

## 适用场景

售前 / CSM / 销售团队，将客户最佳实践转成一页纸案例。

## 核心能力

- 先梳理"可汇报故事"，提炼背景痛点、解决方案、前后对比、量化价值和关键证据；当次故事未经用户明确确认时，技能不会进入设计和 HTML 生成。
- 案例卡片参照 Before & After 逻辑，清晰呈现对比及方案价值。
- 对每张候选图片声明“证明什么、是否选用、如何展示”，优先完整图，支持滑动查看、点击放大和完整图展示。
- 对最终交付的确切 HTML、关联资源和截图执行验证，避免交付空文件、错路径或资源缺失页面。
- 视觉 Token、布局 recipe、状态依赖和 QA 结果均为机器可校验契约，降低规则漂移和重跑成本。
- `case_pipeline.py` 可定位第一断点、输出下一条完整命令并自动重跑客观校验；人工视觉判断仍保留硬停点。

## 安装

该技能基于 feishu-deck-h5 衍生，需先安装并配合基础 Deck 技能使用。

基础技能仓库：

[https://github.com/FuQiang/feishu-deck-h5](https://github.com/FuQiang/feishu-deck-h5)

安装本技能：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/caiminhong0314/feishu-deck-customer-case/tree/main/feishu-deck-customer-case
```

安装后重启 Codex 以加载技能。

## 版本策略

只维护 `feishu-deck-customer-case` 一个稳定版本。规则按来源与故事、证据素材、版式、验证和维护阶段拆分加载，不再维护 1.1 或其他并行规则分支。历史版本通过 Git tag 和 Changelog 追溯，不在本地复制多份技能目录。

`v2.0.0` 升级了 story/layout/rendered/state/QA 合同，不兼容旧 run。旧案例如需继续编辑，应在新运行目录重新初始化并复用来源素材，不要手改旧产物哈希或 schema 版本。

## 如何使用

1. 提供最佳实践文档。
2. 先确认 AI 生成的故事方向，再生成 HTML 案例卡片。
3. 如图片选择不准，直接指定必须展示的图片重新调整。
4. 如果案例内容较多、图片素材较多，或需要讲清多个业务场景，可以直接告诉 AI 做成两页案例卡片。

![使用示例](assets/usage-prompt-example.png)

## 注意事项

- 需先安装 feishu-deck-h5 技能。
- 案例制作仍需要制作人对业务场景、故事主线和证明重点有清晰判断，不能完全依赖 AI 做重点选择和内容展示。
- 需要具备文档阅读权限和图片下载权限。
- AI 第一版图片选择不一定完全准确，需结合对客讲解逻辑确认关键素材。
- “开始生成”“直接做”只表示发起任务，不能替代当次故事确认；技能会先发出完整故事方案并等待明确确认。

## 维护与验证

修改技能后运行：

```bash
python3 feishu-deck-customer-case/scripts/run_contract_tests.py
python3 feishu-deck-customer-case/scripts/run_browser_contract_tests.py
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  feishu-deck-customer-case
```

案例运行遇到阻断或重渲染后：

```bash
python3 feishu-deck-customer-case/scripts/case_pipeline.py status --run-dir <RUN_DIR>
python3 feishu-deck-customer-case/scripts/case_pipeline.py next --run-dir <RUN_DIR>
python3 feishu-deck-customer-case/scripts/case_pipeline.py requalify --run-dir <RUN_DIR>
```

发布稳定版本时再提交 Git，并使用语义化版本 tag；不要在技能目录内保留 `.bak` 或复制版。
