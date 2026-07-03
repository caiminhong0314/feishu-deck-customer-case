# Feishu Deck-Customer Case

**Feishu Deck-Customer Case｜10分钟制作飞书案例一页纸**

基于 CSM 文档、客户成功材料和案例素材，先梳理可汇报故事，再生成飞书风格客户案例卡片。

## 适用场景

售前 / CSM / 销售团队，将客户文档、Wiki、复盘材料、截图素材转成一页纸案例。

## 核心能力

1. 先梳理“可汇报故事”，提炼背景痛点、解决方案、前后对比、量化价值和关键证据。
2. 自动判断图片证据展示方式，支持图片滑动查看、点击放大、完整图展示。
3. 保留图片下方简短解读，帮助讲清每张图证明什么。

## 安装

该技能基于 `Feishu Deck 0613` 衍生，需先安装并配合该技能使用。

安装本技能：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/caiminhong0314/feishu-deck-customer-case/tree/main/feishu-deck-customer-case
```

安装后重启 Codex 以加载技能。

## 如何使用

1. 提供 CSM 文档 / 飞书文档链接 / Wiki 链接 / 图片素材。
2. 先确认 AI 生成的故事方向，再生成 HTML 案例卡片。
3. 如图片选择不准，直接指定必须展示的图片重新调整。
4. 如果案例内容较多、图片素材较多，或需要讲清多个业务场景，可以直接告诉 AI 做成两页案例卡片。

## 注意事项

1. 需要具备文档阅读权限和图片下载权限。
2. AI 第一版图片选择不一定完全准确，需结合对客讲解逻辑确认关键素材。
3. 案例制作仍需要制作人对业务场景、故事主线和证明重点有清晰判断，不能完全依赖 AI 做重点选择和内容展示。

