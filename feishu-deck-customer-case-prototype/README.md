# Feishu Deck-Customer Case Prototype

**技能二：客户案例机制原型演示**

基于 CSM / 客户成功案例文档，提炼最核心的业务机制，并生成飞书 Deck 风格的可交互 HTML 原型页。

当前版本：`v0.2.6`

## 与技能一的区别

- 技能一 `feishu-deck-customer-case`：证据型案例卡片，重点是真实素材、Before & After、量化价值。
- 技能二 `feishu-deck-customer-case-prototype`：原型型案例演示，重点是把核心业务机制做成可点击、可演示的 HTML 原型。

两个技能独立维护、独立安装、独立运行。

## 默认页面结构

- 上方：主标题、副标题、核心指标
- 左侧：过去痛点和真实证据
- 右侧：可交互原型
- 底部：安全区或必要说明

## 核心工作流

- 先读取完整来源，再输出“可汇报故事 + 原型适配判断 + 原型设计方案 + 交互/动画方案 + 素材方案”。
- 方案经确认后再生成 HTML；除非明确要求跳过确认，否则不能直接生成。
- 飞书 / Lark 产品界面必须使用飞书产品风格，不做泛化 SaaS UI。
- 真实素材优先；缺少转账截图、门店照片、货架图等关键业务素材时，先询问是否可以提供，无法提供时才生成写实示意素材。
- 动画和交互必须围绕真实业务对象变化，例如“凭证出现 -> 上传 -> 识别 -> 生成记录 -> 状态流转”。

## 适合场景

- 门店反馈 -> AI 总结 -> 问题归类 -> 责任人跟进
- 价格异常 -> AI 识别 -> 采购确认 -> 看板闭环
- 资质材料 -> AI 初审 -> 供应商反馈 -> 审批流转
- 巡检照片 -> AI 判定 -> 异常提醒 -> 整改追踪

## 安装

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/caiminhong0314/feishu-deck-customer-case/tree/main/feishu-deck-customer-case-prototype
```

安装后重启 Codex。

## 注意事项

- 仍需先安装基础 Deck 技能 `feishu-deck-h5` 或等价飞书 Deck 生成技能。
- 原型可以使用模拟数据，但不能编造客户没有做过的业务机制。
- 必须区分“机制演示原型”和“客户真实系统”。
- 第一版重点是讲清一个核心流程，不追求完整 SaaS 产品。
