---
name: modeling
description: 履约建模（Fulfillment Modeling，FM）指导，用于将业务或软件需求转化为以合同为中心、与表现层无关的 YAML 图模型。当用户要求创建、更新、审查或校验涉及合同、上下文、Party Role、Participant Party、RFP/Proposal 售前凭证、Fulfillment Request、Fulfillment Confirmation、Proof 凭证、Evidence As Role、Domain/Third Party/Context Role、多合同边界、业务规则、下游信号或场景路径的 FM 模型时使用本 skill。本 skill 会写入模型文件并运行内置自检；如果用户要求从 FM 图生成数据库表、SQL、存储或物理 schema 设计，请改用 fm-database-design。
---

# 履约建模（Fulfillment Modeling）

## 事实来源

`references/fm-modeling-rules.md` 是 FM 的权威规则手册。请将本 `SKILL.md` 仅作为简短操作指南；不要在这里复制完整实体词典、命名规则、文件布局、关系约束或自检清单。如果本文件、脚本提示或既有习惯与 reference 冲突，请遵循 reference，并修正产生冲突的内容。

在创建、更新或审查完整 FM 模型之前，先读取 `references/fm-modeling-rules.md`。当任务涉及实体类型选择、多合同边界、Evidence As Role、Proof、角色参与、文件命名、业务规则放置或输出布局时尤其如此。

## 默认工作流

1. 明确模型范围和输出目录。用户指定目录时使用用户目录；否则在当前工作目录下使用 `fm-model/`。
2. 为当前任务加载 `references/fm-modeling-rules.md` 中的权威规则，并将其作为最终依据。
3. 先识别 Contract 上下文。将一个 Contract 视为一条主要履约链；当规则要求时，将多方合同中的法律权责拆分为多个合同上下文。
4. 先发现 Evidence 流，再考虑实现细节：根据可追溯需要建模售前凭证，然后建模 Contract、Fulfillment Request、Fulfillment Confirmation、Proof、异常/反向凭证，以及必要的跨上下文桥接凭证。
5. 只有当 Participant、Party Role、Domain Role、Third Party Role、Context Role 和 Evidence As Role 在权威规则下代表真实业务参与或变化点时，才添加它们。
6. 捕获关键业务属性、属性来源凭证，并在值为派生值时使用可机器检查的 `calculationRule` / `precondition` 表达式。
7. 直接写入或更新 YAML 图模型文件。磁盘上的文件是事实来源；根据当前模型创建、覆盖、重命名或删除实体/关系文件。
8. 运行内置 YAML 自检，并在回复前修复所有报告的问题。
9. 脚本通过后，手动复核 reference 中的语义清单；简要说明仍未解决的假设或问题。

## 输出契约

- 默认将图模型持久化为 YAML 文件。文件布局、文件名约定、允许的类别/类型以及更新规则均以 `references/fm-modeling-rules.md` 为准。
- 保持 FM 与表现层无关：除非用户明确要求单独的实现设计产物，否则不要将 API、服务、页面、数据库表、队列、引擎、SDK 或部署关注点建模为 FM 实体。
- 按 reference 中的定义，使用 `Proof` 表示其它可追溯凭证；不要引入遗留或临时的凭证类型。
- 回复时给出简洁摘要，包括变更的文件路径和自检状态。

## 可执行自检

按本 skill 目录解析内置脚本路径。写入或更新模型后，运行：

```bash
python3 scripts/self_check_fm_yaml.py <model-dir>
```

请使用实际模型目录替换 `<model-dir>`。在最终回复前修复所有失败项。如果脚本与 `references/fm-modeling-rules.md` 不一致，请将其视为 skill 缺陷，并让脚本或说明与 reference 对齐。

## 相关 skill

当用户要求将 FM 图转成数据库表、物理 schema、SQL DDL、不可变凭证持久化或存储设计时，请改用 `$fm-database-design`。
