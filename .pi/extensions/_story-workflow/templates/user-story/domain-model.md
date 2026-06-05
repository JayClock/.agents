# 用户故事领域模型

> 维护 FM 派生的领域对象、关系、生命周期和业务不变量。由 `/fm-model` 从 FM YAML 源模型派生。
> 引用 FM entity 名称时使用 Markdown 链接，便于跳转到源 YAML：[`<EntityName>`](fm-model/entities/<EntityName>.yaml)。
> FM entity 名称应使用业务语义名，避免 `Contract`、`Context`、`Role`、`Request`、`Confirmation`、`Evidence` 等冗余类型后缀。

## 模型说明
- <领域模型覆盖的业务范围、合同上下文和关键假设>

## FM 派生结构
### Contract / Context
- [`<BusinessBoundaryEntityName>`](fm-model/entities/<BusinessBoundaryEntityName>.yaml)：<边界与责任>

### Roles
- [`<BusinessRoleEntityName>`](fm-model/entities/<BusinessRoleEntityName>.yaml) / <Party Role / Domain Role / Third Party Role>：<责任或参与方式>

### Evidence 链与履约责任
- [`<BusinessBoundaryOrEvidenceEntityName>`](fm-model/entities/<BusinessBoundaryOrEvidenceEntityName>.yaml) → [`<BusinessRequestEntityName>`](fm-model/entities/<BusinessRequestEntityName>.yaml) → [`<BusinessResultEntityName>`](fm-model/entities/<BusinessResultEntityName>.yaml)：<业务责任说明>

### Thing / 关键业务对象
- [`<ThingName>`](fm-model/entities/<ThingName>.yaml)：<关键属性 / 状态>

## 关键关系
- [`<ConceptAEntityName>`](fm-model/entities/<ConceptAEntityName>.yaml) 与 [`<ConceptBEntityName>`](fm-model/entities/<ConceptBEntityName>.yaml)：<关系说明>

## 生命周期
- <状态或阶段>：由 [`<BusinessRequestEntityName>`](fm-model/entities/<BusinessRequestEntityName>.yaml) -> [`<BusinessResultEntityName>`](fm-model/entities/<BusinessResultEntityName>.yaml) / [`<BusinessEvidenceEntityName>`](fm-model/entities/<BusinessEvidenceEntityName>.yaml).`<attribute>` 证明，不建独立状态实体。

## 业务规则与不变量
- <不变量 / 约束>：<规则落点，如 precondition / calculationRule / Domain Role / notes>

## 待验证点
- <需要通过验收场景或 `/model-check` 验证的概念、关系或规则>
