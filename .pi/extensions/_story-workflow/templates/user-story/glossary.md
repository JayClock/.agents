# 用户故事概念字典

> 维护角色、稳定目标、业务术语、关键规则和范围边界。由 `/fm-model` 从 FM YAML 源模型派生。
> 引用 FM entity 名称时使用 Markdown 链接，便于跳转到源 YAML：[`<EntityName>`](fm-model/entities/<EntityName>.yaml)。
> FM entity 名称应使用业务语义名，避免 `Contract`、`Context`、`Role`、`Request`、`Confirmation`、`Evidence` 等冗余类型后缀。

## 用户角色与目标
- <角色> / [`<BusinessRoleEntityName>`](fm-model/entities/<BusinessRoleEntityName>.yaml)：<稳定业务目标>

## 业务术语
| 概念 | FM 对应 | 定义 | 关键属性 / 状态 | 关系 / 边界 |
|---|---|---|---|---|
| <概念> | [`<EntityName>`](fm-model/entities/<EntityName>.yaml) / <Contract / Context / Thing / Evidence / Request / Confirmation / Role> | <一句话定义> | <属性或状态> | <相关概念、同义词、边界> |

## 业务规则
- <规则>：<跨故事复用的约束或判断条件；规则落点如 [`<EntityName>`](fm-model/entities/<EntityName>.yaml).`precondition` / `calculationRule` / `notes`>

## 范围边界
- <已纳入范围 / [`<BusinessBoundaryEntityName>`](fm-model/entities/<BusinessBoundaryEntityName>.yaml)>
- <不纳入范围 / 独立合同或独立上下文 / 已有独立故事>
