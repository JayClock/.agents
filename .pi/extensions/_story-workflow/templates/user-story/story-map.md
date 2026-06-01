# 用户故事地图

> 维护用户旅程、故事拆分、故事边界和依赖。由 `/fm-model` 从 FM YAML 源模型派生。

## 范围 / 业务目标
- <本次故事地图覆盖的业务目标、Contract 或 Context>

## 用户旅程
### <角色 / Party Role>
1. <阶段一：对应 Evidence 链或业务责任>
2. <阶段二：对应 Request -> Confirmation>
3. <阶段三：对应下游 Evidence 或终态>

## 故事拆分
### <旅程阶段 / 履约责任链>
- [Epic] 作为 <角色>，我希望 <能力>，从而 <价值>（边界：<Contract / Context>）
- [Journey step] 作为 <角色>，我希望 <能力>，从而 <价值>（来源：<Evidence 链>）
- [Thin slice] 作为 <角色>，我希望 <能力>，从而 <价值>（来源：<Fulfillment Request -> Fulfillment Confirmation>）

## 异常流故事
- [Thin slice] 作为 <角色>，我希望 <取消 / 退款 / 暂停 / 反转 / 补偿能力>，从而 <异常处理价值>

## 故事边界与依赖
- <故事 A>：<边界 / 依赖 / 是否可独立验收 / 是否跨 Context Evidence As Role>

## 推荐下一张 TQA 故事
- 作为 <角色>，我希望 <能力>，从而 <价值>
