---
name: modeling
description: 履约建模（Fulfillment Modeling，FM / 8X Flow / BOD 面向业务设计）指导，用于将业务、合同、服务协议、业务流程或软件需求转化为以合同履约和业务凭证为中心、与表现层无关的 YAML 图模型。当用户要求创建、更新、审查或校验涉及业务建模、业务/领域分离、合约分析、权责履约、渠道/合约前上下文、合同上下文、履约上下文、事件流、收入流、成本结构、业务脊梁、Party Role、Participant Party、RFP/Proposal 售前凭证、Fulfillment Request、Fulfillment Confirmation、Other Evidence（其它凭证）、Evidence As Role、Domain/Third Party/Context Role、多合同边界、业务规则、KPI、下游信号、业务宏流程、核心业务模式或场景路径的 FM 模型时使用本 skill。本 skill 会写入模型文件并运行内置自检；如果用户要求从 FM 图生成数据库表、SQL、存储或物理 schema 设计，请改用 fm-database-design。
---

# 履约建模（Fulfillment Modeling）

## 事实来源

`references/fm-modeling-rules.md` 是 FM 的权威规则手册。请将本 `SKILL.md` 仅作为简短操作指南；不要在这里复制完整实体词典、命名规则、文件布局、关系约束或自检清单。如果本文件、脚本提示或既有习惯与 reference 冲突，请遵循 reference，并修正产生冲突的内容。

在创建、更新或审查完整 FM 模型之前，先读取 `references/fm-modeling-rules.md`。当任务涉及实体类型选择、多合同边界、Evidence As Role、Other Evidence、角色参与、文件命名、业务规则放置或输出布局时尤其如此。

## 建模节奏

把 FM 建模按“三段式”推进，避免一开始就陷入 YAML 细节：

1. **简化建模图**：先只识别 Evidence、Participant、Role 和上下文边界，用于快速对齐业务事实、权责和沟通流。
2. **标准建模图**：再补充 Evidence 子类型、时段/时刻、1:1 关系、关键属性、角色扮演和跨上下文桥接，用于发现变化点和验证业务脊梁。
3. **YAML 图模型**：最后把标准建模图落盘为一文件一实体/关系的 YAML，并以自检脚本作为最低质量门槛。

回复用户时不必画图，但在生成 YAML 前要完成这三步的思考。若用户要求工作坊、演示或快速草图，可先输出简化图或标准图说明，再落 YAML。

## 默认工作流

1. 明确模型范围和输出目录。用户指定目录时使用用户目录；否则在当前工作目录下使用 `fm-model/`。
2. 为当前任务加载 `references/fm-modeling-rules.md` 中的权威规则，并将其作为最终依据。
3. 先做输入分拣：合同条款、流程步骤、服务蓝图或事件风暴材料只是线索；只把说明权责、履约、金额、时间、KPI、异常和追责的内容转成 FM。领域算法、目录、计算能力、外部系统和纯法务/展示/技术事项只在确实影响业务变化点时用 Thing、Domain Role、Third Party Role 或 Context Role 表达。若判断为纯领域系统或工具集成，不要强行生成 Contract / Request / Confirmation；应说明为什么不适合 FM，并请求更多业务权责材料。
4. 先形成简化建模图：列出候选 Evidence、Participant、Role、Contract 上下文、合约前/渠道上下文和事件流锚点。将一个 Contract 视为一条主要履约链；同时优先围绕现金收入、现金支出、目标-实际/KPI 三类稳定业务线索寻找事件流入口。若输入缺少合约或权责说明，先向用户索要或明确假设，再从业务凭证逆推合约。
5. 将简化图细化为标准建模图：从事件流锚点向前后追溯 Evidence 流，根据关键数据项追溯售前凭证、Contract、Fulfillment Request、Fulfillment Confirmation、Other Evidence、异常/反向凭证，以及必要的跨上下文桥接凭证。业务上的更正、取消、冲正、退款或补偿应表现为新的凭证，而不是修改旧凭证。
6. 用“纸质单据演练”校准 Evidence：如果一个候选对象无法被想象成需要留存、签字、盖章、审计或追责的单据/记录，通常不要建成 Evidence。
7. 只有当 Participant、Party Role、Domain Role、Third Party Role、Context Role 和 Evidence As Role 在权威规则下代表真实业务参与、领域能力、第三方依赖或变化点时，才添加它们。角色抽象的目的不是补齐图形，而是提供业务变化点。
8. 捕获关键业务属性、属性来源凭证，并在值为派生值时使用可机器检查的 `calculationRule` / `precondition` 表达式。
9. 直接写入或更新 YAML 图模型文件。磁盘上的文件是事实来源；根据当前模型创建、覆盖、重命名或删除实体/关系文件。关系可用 `relationshipKind` 标记 `association`、`rolePlaying` 或 `crossContextAssociation`。
10. 当用户需要业务扩展、复用分析、平台化/中台设计或长期维护时，补充业务宏流程与核心业务模式说明，比较相似合同/业务线的稳定履约链路与变化点，但不要为了表达模式新增 FM 实体类型。
11. 运行内置 YAML 自检，并在回复前修复所有报告的问题。
12. 脚本通过后，手动复核 reference 中的语义清单；简要说明仍未解决的假设或问题。

## 输出契约

- 默认将适合 FM 的图模型持久化为 YAML 文件。若输入被判断为纯领域系统、工具集成或缺少业务权责/凭证依据，不要强行生成 FM YAML；先输出不适用说明和需要补充的业务材料。文件布局、文件名约定、允许的类别/类型以及更新规则均以 `references/fm-modeling-rules.md` 为准。
- 保持 FM 与表现层无关：除非用户明确要求单独的实现设计产物，否则不要将 API、服务、页面、数据库表、队列、引擎、SDK 或部署关注点建模为 FM 实体。
- 按 reference 中的定义，使用 `Other Evidence`（文件后缀 `evidence`）表示其它可追溯凭证；不要新增遗留或临时凭证类型。
- 回复时给出简洁摘要，包括变更的文件路径和自检状态。

## 可执行自检

按本 skill 目录解析内置脚本路径。写入或更新模型后，运行：

```bash
python3 <skill-dir>/scripts/self_check_fm_yaml.py <model-dir>
```

请使用实际模型目录替换 `<model-dir>`。在最终回复前修复所有失败项。如果脚本与 `references/fm-modeling-rules.md` 不一致，请将其视为 skill 缺陷，并让脚本或说明与 reference 对齐。

## 相关 skill

当用户要求将 FM 图转成数据库表、物理 schema、SQL DDL、不可变凭证持久化或存储设计时，请改用 `$fm-database-design`。
