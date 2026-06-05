# 用户故事地图

> 维护用户旅程、故事拆分、故事边界和依赖。由 `/fm-model` 从 FM YAML 源模型派生。
> 主体内容面向业务读者，用自然语言描述“发生了什么、谁提出、谁确认、结果是什么”；FM entity 链接放在 `FM 来源` 折叠区中，便于跳转到源 YAML。
> FM entity 名称应使用业务语义名，避免 `Contract`、`Context`、`Role`、`Request`、`Confirmation`、`Evidence` 等冗余类型后缀。

## 范围 / 业务目标
- 业务目标：<用一句自然语言说明本次故事地图要达成的目标>
- 主要受益者：<真正受益角色>
- 成功结果：<业务上如何判断目标被满足>

<details>
<summary>FM 来源</summary>

- Contract：[`<BusinessContractEntityName>`](fm-model/entities/<BusinessContractEntityName>.yaml)
- Context：[`<BusinessContextEntityName>`](fm-model/entities/<BusinessContextEntityName>.yaml)

</details>

## 用户旅程

### 1. <自然语言阶段名>
<用一两句话描述这个阶段发生了什么，以及为什么重要。>

- 主要受益者：<角色>
- 谁提出：<发起方；来自 Request 相邻 Party Role>
- 谁确认：<确认方；来自 Confirmation 相邻 Party Role>
- 业务结果：<这个阶段完成后业务上成立的事实>

<details>
<summary>FM 来源</summary>

- 来源：[`<BusinessEvidenceOrRequestEntityName>`](fm-model/entities/<BusinessEvidenceOrRequestEntityName>.yaml) -> [`<BusinessEvidenceOrResultEntityName>`](fm-model/entities/<BusinessEvidenceOrResultEntityName>.yaml)
- 发起方：[`<InitiatorPartyRoleEntityName>`](fm-model/entities/<InitiatorPartyRoleEntityName>.yaml)
- 确认方：[`<ConfirmerPartyRoleEntityName>`](fm-model/entities/<ConfirmerPartyRoleEntityName>.yaml)

</details>

## 故事拆分

### <自然语言阶段名>
- [Epic] 作为 <角色>，我希望 <能力>，从而 <价值>
  - 主要受益者：<角色>
  - 业务结果：<Epic 达成后的业务结果>
  <details>
  <summary>FM 来源</summary>

  - 边界：[`<BusinessContractEntityName>`](fm-model/entities/<BusinessContractEntityName>.yaml) / [`<BusinessContextEntityName>`](fm-model/entities/<BusinessContextEntityName>.yaml)

  </details>

- [Journey step] 作为 <角色>，我希望 <能力>，从而 <价值>
  - 谁提出：<发起方>
  - 谁确认：<确认方>
  - 业务结果：<这个旅程阶段完成后的业务结果>
  <details>
  <summary>FM 来源</summary>

  - 来源：[`<BusinessEvidenceEntityName>`](fm-model/entities/<BusinessEvidenceEntityName>.yaml) 链
  - 发起方：[`<InitiatorPartyRoleEntityName>`](fm-model/entities/<InitiatorPartyRoleEntityName>.yaml)
  - 确认方：[`<ConfirmerPartyRoleEntityName>`](fm-model/entities/<ConfirmerPartyRoleEntityName>.yaml)

  </details>

- [Thin slice] 作为 <角色>，我希望 <能力>，从而 <价值>
  - 谁提出：<发起方>
  - 谁确认：<确认方>
  - 业务结果：<可独立验收的最小业务结果>
  <details>
  <summary>FM 来源</summary>

  - 来源：[`<BusinessRequestEntityName>`](fm-model/entities/<BusinessRequestEntityName>.yaml) -> [`<BusinessResultEntityName>`](fm-model/entities/<BusinessResultEntityName>.yaml)
  - 发起方：[`<InitiatorPartyRoleEntityName>`](fm-model/entities/<InitiatorPartyRoleEntityName>.yaml)
  - 确认方：[`<ConfirmerPartyRoleEntityName>`](fm-model/entities/<ConfirmerPartyRoleEntityName>.yaml)

  </details>

## 异常流故事
- [Thin slice] 作为 <角色>，我希望 <异常处理能力>，从而 <异常处理价值>
  - 谁提出：<发起方>
  - 谁确认：<确认方>
  - 业务结果：<异常被处理后的业务结果>

## 故事边界与依赖
- <故事 A>：<自然语言说明边界、依赖、是否可独立验收>

<details>
<summary>FM 追踪说明</summary>

- 跨 Context 桥接：[`<EvidenceAsRoleEntityName>`](fm-model/entities/<EvidenceAsRoleEntityName>.yaml) 或“无”。
- 待验证点：<若发起方或确认方无法唯一判断，在这里说明，不要猜测。>

</details>

## 推荐下一张 TQA 故事
- 作为 <角色>，我希望 <能力>，从而 <价值>
