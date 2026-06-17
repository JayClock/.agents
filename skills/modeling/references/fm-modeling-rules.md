# 履约建模规则

当任务需要精确生成或校验 Fulfillment Modeling（FM，履约建模）时，使用以下规则。

## 核心视角

- 优先建模业务逻辑，而不是实现逻辑：关注业务如何证明权利、责任、支付、KPI 结果和异常处理。
- 履约建模的主线是：合同上下文 → 主要履约项 → 履约请求 / 履约确认 → 违约项 → 跨合同凭证引用 → 变化点 / 边界。
- 将履约视为异步过程：请求打开一个时间区间，确认关闭这个区间。在确认发生之前，业务状态是未知或待定的。
- 将异常视为新的履约义务，而不是静默的自动修正；除非合同规则明确规定不会产生进一步责任。

## 实体类别

- Evidence：RFP、Proposal、Contract、Fulfillment Request、Fulfillment Confirmation、Proof。
- Participant：Party、Thing。
- Role：Party Role、Domain Role、Third Party Role、Context Role、Evidence As Role。
- Context：有边界的业务上下文容器，例如支付、库存、开票、交付、订阅、服务或支持。

## 实体类型词典

使用本词典选择实体种类并避免语义漂移。将 Evidence 视为带时间的业务事实，Participant 视为静态占位，Role 视为责任或计算参与者，Context 视为有边界的业务容器。

### Evidence（凭证）

Evidence 实体表示在某个业务时间点实际发生的业务动作、承诺或结果制品。它们构成动态业务控制流：

- Contract：合约。表示当事双方形成正式合约关系，用于留存合约签订证据的业务凭证；在实际的法律追责中，三方合约被视作双方合约的组合。所以在建模时，需要根据当事双方的不同将三方合约建模成多个合约上下文。
- RFP：索取提案，表示初始客户意向、询价或需求请求。
- Proposal：提案，表示响应 RFP 的具体报价、方案或承诺。
- Fulfillment Request：履约请求，表示某一当事方发起履约过程，用于留存其履约发起证据的业务凭证。
- Fulfillment Confirmation：履约确认，表示某一当事方在履约过程中实施了某种履约确认，用于留存其履约中、确认证据的业务凭证。
- Proof：其它凭证，表示任何不属于前 5 中类型的，但为了追溯需要而必须留存证据的其它业务凭证，例如收入确认记录、电子发票或仓库收货文档。

#### 合约前上下文的常见场景

- **一次 RFP 对应一次 Proposal**：一次方案索取可能只会对应一次提案，并且业务上只需要对方案索取和提案的唯一凭证进行留存。
- **一次 RFP 存在多次 Proposal**：一次方案索取可能对应多次提案，并且业务上需要对多次提案的凭证进行留存和追溯。
- **没有 RFP**：可能会没有方案索取的过程，或业务上无需对方案索取的凭证进行留存和追溯。
- **没有 RFP 和 Proposal**：可能会没有方案索取和提案的过程，或业务上对方案索取和提案的凭证进行留存和追溯。
- **一个合约可能存在多种合约前的上下文**：合约的签订，可能会通过多种不同方式的合约的上下文所达成。

#### 合约上下文的常见场景

- **一个 Fulfillment Request 时段内有单次 Fulfillment Confirmation**：在履约过程中，一次履约申请可能只会对应一次履约确认，并且业务上只需要对某个唯一的履约确认凭证进行记录和追溯。
- **一个 Fulfillment Request 时段内有多次 Fulfillment Confirmation**：在履约过程中，一次履约过程也可能对应多次履约确认，并且业务上需要对这些履约确认凭证进行记录和追溯。
- **多个 Fulfillment Request 关联共同的 Fulfillment Confirmation**：不同的履约请求，也可能可以通过相同的履约确认来进行履约，在这种情况下用于履约确认的凭证在权责关系上是等价的。

> 在建模时，有履约请求（时段）就一定有一次或者多次履约确认（时刻）。在追溯时，如果履约请求（时段）缺少了模型上对应的履约确认（时刻）凭证，则可被认为是除了履约确认超时外的另一种违约形式

### Participant（参与者）

Participant 实体表示客观存在的物理实体或业务对象。在 FM 图中，它们是静态领域骨架占位，而不是展开的字段模型。当身份或对象重要时，通过角色或直接业务关联将它们连接到 Contract 或售前 Evidence。

- Party：履约过程中所涉及到的具体人员（或其在系统内的对应存在），对凭证所承载的权责直接负责（也可以理解为凭证需要谁签字或盖章）
- Thing：交易或履约动作围绕的具体对象，例如商品、付费内容或虚拟资产。用它回答合同出售或履约的是什么。

### Role（角色）

代表可被抽象表达的变化点，可以由具体事物或概念所扮演。角色的主要作用是通过抽象提供业务变化点，在实际过程中，需要结合对变化点的需要进行抽象，不必追求完全抽象。

- Party Role：从合约的视角来看，合约的当事双方实际上都是法人，而具体的当事人实际上是业务流程中代表法人进行履约活动。可以使用 Party Role 来抽象合约双方的法人概念。将当事人角色化后，具体的当事人就可以扮演法人角色，这样就为系统实现提供了基于角色的变化点。
- Domain Role：黑盒业务计算者、校验者或规则执行者，例如价格评估员或折扣审批人。用现实世界中的岗位或职位命名，而不是软件系统。
- Third Party Role：内部控制之外的外部机构，例如支付机构或税务发票平台。它只能连接到 Proof 或 Evidence As Role，绝不能直接进入核心内部履约流。
- Context Role：对于当前合约上下文相关联的其它合约上下文，**我们不关心其内部业务逻辑时，也可以使用角色化来代替**。
- Evidence As Role：以支付为例，有时候我们可以出现多种支付方式，而支付凭证往往是另一个合约上下文中的凭证。可以用**凭证角色化来表达另一个合约上下文中的凭证，对当前合约上下文中所依赖的凭证扮演关系**。由于时段类凭证不能代表业务上确定的结果，所以只有时刻类凭证能够称为凭证角色化的扮演者

### Context（上下文）

- 拥有角色扮演关系的角色元素提供了最为明显的上下文边界提示，按照被扮演的角色可以清晰的分离不同的上下文，而这些角色被分割开的两个上下文共用。
- 未标明扮演关系的参与元素、领域逻辑、第三方系统和其它合约上下文均处于独立的上下文中
- 参与元素、领域逻辑、第三方系统，通常是专门的领域问题，业务逻辑与领域逻辑的边界清晰分离

#### 常见的跨合约上下文关联方式

- **通过具体凭证直接关联**：在无需通过抽象提供变化点的情况下，可能与另一个合约上下文中的时刻类凭证进行跨上下文的直接关联。
- **通过凭证角色化扮演关系直接关联**：在通过抽象变化点的情况下，通过凭证角色化元素和时刻类的扮演关系进行跨上下文的直接关联。
- **通过参与元素间接关联**：两个合约上下文，可能通过某个共同使用的参与元素及所属的领域上下文产生间接关联

## FM 流程

1. 上下文与合同边界优先：先识别 Contract、相关 Contract Context 及关键 Party Role，再识别其他实体。将一个 Contract 视为一条主链；三方或多方合约在法律追责和权责建模上按当事双方关系拆成多个合约上下文。Participant Party 是可选的辅助信息，不是主要建模入口。
2. 售前证据按留痕需要建模：只有当需求中包含售前阶段且业务需要追溯时，才添加 RFP 或 Proposal。允许一次 RFP 对一次 Proposal、一次 RFP 对多次 Proposal、没有 RFP、没有 RFP 和 Proposal，以及一个合约存在多种合约前上下文。如果不存在需要留痕的售前阶段，则直接从 Contract 开始。
3. 证据优先发现：在每个 Contract 上下文内，先寻找主要资金流动证据，并用既有 Evidence 种类表达为 Fulfillment Request、Fulfillment Confirmation 或 Proof 等具体凭证，不要新增词典外的 Evidence 类型。创建最能锚定业务义务的证据，并在适用时列出关键属性，例如业务时间点、金额、币种、付款窗口、数量或退款金额。如果资金流动较弱或不存在，则从关键 KPI 或验收证据开始。
4. 属性来源追踪：对当前证据上的每个关键属性，都要追踪其来源，并保持来源路径清晰。来源只能来自用户输入、先前的证据实体或算法计算。如果金额、币种、数量、付款窗口、退款金额、KPI 或验收指标派生自先前的证据实体，则同时记录先前证据路径和用于派生它的计算规则。不要保留无法解释来源的属性。
5. 主履约事项：从锚定证据回溯到它所证明的权利与义务，然后发现用于确立、请求和确认这些义务的周边证据。将每一项具体责任建模为 Fulfillment Request 打开的履约时段，以及一次或多次 Fulfillment Confirmation 关闭或部分关闭该时段；当业务上确认凭证在权责关系上等价时，多个 Fulfillment Request 可以关联共同的 Fulfillment Confirmation。不要把 Request -> Confirmation 强制理解为一对一。
6. 异常与违约流程：对于退款、取消、服务暂停、冲正、赔偿以及类似的违约或异常流程，从相关的资金证据或 KPI/验收证据出发，重复相同的证据发现方法，然后将其建模为各自的 Fulfillment Request 时段与一次或多次 Fulfillment Confirmation 时刻。持续扩展违约处理，直到需求到达外部争议或诉讼边界。
7. 先证据流后角色：先完成相互连接的证据流，再围绕每个证据添加参与创建、请求、确认、计算或桥接该证据的角色，以细化模型。
8. 参与方角色建模：Participant Party 是全局的现实世界个人或组织身份；Party Role 表达该 Party 在特定上下文中的身份、责任、权限和参与方式。对于关键签约方、受益人、履约人或必须跨上下文追踪的身份，添加或复用 Participant Party。优先使用 Participant Party -> Party Role -> Contract 表达上下文责任；当只需要表达具体身份与 Contract 或售前 Evidence 的直接业务关联，且不需要角色变化点时，也可以直接关联 Participant Party，并记录原因。如果只绘制 Party Role，则记录或解释其底层物理身份对该模型切片不重要或未知。
9. 角色拆分：根据业务意图添加 Party Role、Evidence As Role、Third Party Role、Context Role 和 Domain Role。Domain Role 表示黑盒业务计算者、校验者或规则执行者，应询问“在软件出现之前，现实世界中是什么岗位在做这项工作”，并用岗位/职位语义命名。Third Party Role 表示内部控制之外的外部机构，例如支付机构或税务发票平台。Context Role 表示当前合约上下文相关联、但不关心其内部业务逻辑的其它合约上下文。
10. 参与规则：每个 RFP、Proposal、Fulfillment Request、Fulfillment Confirmation 和 Proof 都应有且只有一个责任参与方。优先用相邻 Party Role 表达该责任参与方；如果本模型切片选择直接连接 Participant Party，则不要再为同一凭证重复连接等价 Party Role。
11. Proof 与 Evidence As Role：
    - 当一个确认产生的业务文档或副产物保留在同一上下文内时，使用 Proof。
    - 当同一语义跨上下文起桥接作用时，使用 Evidence As Role。
    - 不要为同一业务语义同时保留这两种实体。
12. Evidence As Role 桥接规则：Evidence As Role 用于表达另一个合约上下文中的凭证在当前上下文中扮演依赖凭证角色。只有时刻类凭证能够作为 Evidence As Role 的扮演者，例如 Fulfillment Confirmation 或其它表示确定结果的 Proof；不要将时段类 Fulfillment Request 作为扮演者，也不要将 Evidence As Role 连接到 Contract、Proposal 或 RFP。
13. Third Party Role 与 Context Role：Third Party Role 只能连接到 Proof 或 Evidence As Role，不能直接进入核心内部履约流。Context Role 用于在不展开其它合约上下文内部逻辑时表达上下文级依赖；应连接到承载该依赖的具体时刻类凭证、Proof 或 Evidence As Role，而不是替代当前上下文内应建模的 Request/Confirmation。
14. 多合同处理：
    - 一个 Contract 等于一条主链。
    - 每个 Contract 上下文都独立遵循完整流程。
    - 每个 Context 都包含自己的链条，可从 RFP、Proposal 或 Contract 开始；没有额外业务文档或跨上下文桥接时，可以自然结束于 Fulfillment Confirmation，不必强制添加 Proof 或 Evidence As Role。
    - Participant Party 实体保留在 Context 外部。
    - 同一个现实世界参与方可以通过一个外部 Participant Party，在不同上下文中表现为不同的 Party Role；不要仅因为不同现实世界参与方参与同一合同，就把它们合并成一个 Party。
    - 不同合同上下文之间可以通过具体时刻类凭证直接关联、通过 Evidence As Role 扮演关系关联，或通过共同 Participant Party 及其领域上下文间接关联；是否抽象为 Evidence As Role 取决于是否需要表达变化点。
    - 不要将 Contract 直接连接到 Contract，也不要将 Contract 直接连接到另一个上下文的 Request/Confirmation。
15. 边界与流：在角色和参与方明确后，将 Party 和 Thing 放入适当的领域边界。关系应表达证据流、角色参与和上下文协作，同时将业务控制流与领域计算逻辑分离。

## 文件输出

对于新的/初始模型，将 YAML 文件直接写入磁盘。使用用户指定的目录；如果未指定，则在当前工作目录下使用 `fm-model/`。磁盘上的文件是事实来源。

推荐目录布局：

```text
fm-model/
  summary.yaml
  entities/
    SalesFulfillmentContext.yaml
    SellerFulfillmentRole.yaml
    SalesContract.yaml
    DeliveryRequest.yaml
    DeliveryConfirmation.yaml
  relationships/
    SalesContract_to_DeliveryRequest.yaml
    DeliveryRequest_to_DeliveryConfirmation.yaml
    SellerFulfillmentRole_to_DeliveryRequest.yaml
    SellerFulfillmentRole_to_DeliveryConfirmation.yaml
```

每个 YAML 文件只包含一个语义对象。使用基于业务 `name` 值的友好、稳定文件名。实体 `name` 是关系和上下文成员引用所使用的稳定引用键。

推荐 `summary.yaml`：

```yaml
type: summary
summary: 销售履约模型
```

推荐实体文件 `entities/SalesFulfillmentContext.yaml`：

```yaml
type: entity
category: Context
kind: Bounded Context
name: SalesFulfillmentContext
label: 销售履约上下文
```

推荐实体文件 `entities/SalesContract.yaml`：

```yaml
type: entity
category: Evidence
kind: Contract
name: SalesContract
label: 销售合同
context: SalesFulfillmentContext
attributes:
  - name: contractAmount
    label: 合同金额
    valueType: Money
    required: true
    meaning: 双方约定的履约金额
```

推荐关系文件 `relationships/SalesContract_to_DeliveryRequest.yaml`：

```yaml
type: relationship
source: SalesContract
target: DeliveryRequest
label: 合同触发交付申请
```

关系文件是一等图对象。除非明确要求，否则不要把关系嵌入实体文件；即使嵌入，也只能作为可选的非权威引用。

使用实体 `name` 作为稳定引用键。实体文件名应使用实体 `name`，例如 `SalesContract.yaml`；关系文件名应使用源实体名和目标实体名，例如 `SalesContract_to_DeliveryRequest.yaml`。如果文件名冲突，追加一个简短且有意义的限定词或数字后缀。文件名使用 ASCII 字母、数字、`_` 和 `-`。实体 `name` 值必须非空，并且在所有实体文件中唯一。关系文件名必须在所有关系文件中唯一。每个关系端点都必须按 `name` 引用一个已存在实体。

每个关系文件都是标量 1:1 关系：`source` 恰好是一个实体 `name`，`target` 恰好是一个实体 `name`。不要使用数组、逗号分隔名称、通配符或自定义端点载荷来表达一对多。当一个 Contract 有多个 Fulfillment Request 时，编写多个独立关系文件，它们复用该 Contract 作为 `source`，并分别指向一个 Fulfillment Request。

推荐实体字段：

- `type`：必须是 `entity`。
- `category`：`Evidence`、`Participant`、`Role` 或 `Context`。
- `kind`：具体 FM 种类，例如 `Bounded Context`、`Contract`、`Party Role`、`Fulfillment Request`、`Fulfillment Confirmation`、`Evidence As Role` 或 `Proof`。
- `name`：简洁的技术或英文标识符；在同一模型的实体中必须唯一。
- `label`：人类可读的业务标签。
- `context`：上下文内实体的父业务 Context 实体 `name`。Context 实体必须出现在其成员之前。Participant Party 实体不得有 `context`。
- `attributes`：可选数组，用于表示实体的内在业务属性。每个条目在已知时应包含 `name`、`label`、`valueType`、`required` 和 `meaning`。
  任何派生属性都应包含 `calculationRule`。这适用于业务时间、金额、数量、退款值、KPI 指标、验收指标、资格标志，以及其他从先前证据或算法计算派生出的值。当使用先前证据时，`calculationRule` 必须包含源证据属性路径，例如 `refundAmount = ColumnSubscriptionContract.columnPrice`。当值派生自同一证据上的属性时，可以使用本地属性名，例如 `expiredAt = startedAt + duration("PT30M")`。直接用户输入值可以省略 `calculationRule`。表达式风格见“属性计算规则”。
- `notes`：可选的简短说明。

推荐关系字段：

- `type`：必须是 `relationship`。
- `source`：恰好一个源实体 `name` 字符串。不要使用数组或组合名称。
- `target`：恰好一个目标实体 `name` 字符串。不要使用数组或组合名称。
- `label`：解释该关系的简短业务短语。
- `notes`：可选的简短说明。

不要在 FM YAML 文件中包含展示层字段。模型只应携带业务语义和图连通性。

## 属性计算规则

对派生属性使用可解析的表达式风格规则。将这些字段视为解析器实现的小型 DSL 契约，而不是自由文本。

- `calculationRule` 必须且只能是一个赋值表达式，形式为 `<targetAttribute> = <expression>`。
- `calculationRule` 左侧必须是当前属性的 `name`。不要给另一个属性、多个属性、实体路径或嵌套字段赋值。
- `precondition` 必须且只能是一个布尔表达式。它不得包含赋值运算符。
- 只使用 ASCII 标识符：`[A-Za-z_][A-Za-z0-9_]*`。实体 `name` 值优先使用 PascalCase，属性 `name` 值优先使用 camelCase。
- 使用显式 `EntityName.attributeName` 路径引用先前证据属性，例如 `PaymentConfirmation.paidAmount` 或 `ShipmentConfirmation.confirmedAt`。
- 仅对同一证据上的属性使用本地 `attributeName` 引用，例如 `expiredAt = startedAt + duration("PT30M")`。
- 不要在表达式中使用标签、空格、中文标点、自然语言短语或显示名称。
- 支持的字面量包括数字、双引号字符串、布尔值 `true` / `false` 和 `null`。不要使用单引号字符串。
- 支持的算术运算符包括 `+`、`-`、`*`、`/` 和 `%`。
- 支持的比较运算符包括 `==`、`!=`、`<`、`<=`、`>` 和 `>=`。
- 支持的布尔运算符包括 `&&`、`||` 和一元 `!`。
- 可以使用括号分组；当优先级可能不清晰时，应使用括号。
- 支持的函数调用仅限于 `isNull(value)`、`notNull(value)`、`if(condition, whenTrue, whenFalse)`、`duration(iso8601Duration)`、`min(a, b)`、`max(a, b)`、`round(value, digits)`、`floor(value)`、`ceil(value)` 和 `abs(value)`。
- 使用显式空值检查，例如 `isNull(ShipmentConfirmation.confirmedAt)` 和 `notNull(PaymentConfirmation.confirmedAt)`。除非简单数据比较确实需要直接空值相等检查，否则不要写 `x == null`。
- 当一个值必须回退到另一个值时，使用条件表达式：`cancelledQuantity = if(OrderCancellationRequest.cancelable == true, OrderSalesContract.quantity, 0)`。
- 当某个属性只在某个业务条件下存在或只在该条件下有效时，优先使用单独的 `precondition` 字段。在这种情况下，让 `calculationRule` 聚焦于值计算。
- 时间偏移必须通过 `duration(...)` 使用显式 ISO 8601 时长表示法，例如 `expiredAt = startedAt + duration("PT30M")`、`expiredAt = startedAt + duration("PT48H")` 或 `expiredAt = startedAt + duration("P7D")`。
- 避免混合说明与计算。将业务说明放入 `meaning` 或 `notes`，而在 `calculationRule` 和 `precondition` 中只放可执行或可机器检查的规则。
- 不要在 `calculationRule` 或 `precondition` 中使用自然语言片段，例如 `is absent`、`when ...`、`before shipment`、`after payment`、`within 7 days` 或 `if paid then ...`。

推荐解析器优先级，从高到低：

1. 函数调用和括号表达式。
2. 一元 `!` 和一元 `-`。
3. `*`、`/`、`%`。
4. `+`、`-`。
5. `<`、`<=`、`>`、`>=`。
6. `==`、`!=`。
7. `&&`。
8. `||`。

最小语法形态：

```text
calculationRule := identifier "=" expression
precondition    := booleanExpression
path            := identifier | identifier "." identifier
functionCall    := identifier "(" arguments? ")"
arguments       := expression ("," expression)*
```

类型规则：

- `precondition` 必须求值为 `Boolean`。
- `calculationRule` 右侧必须与当前属性的 `valueType` 兼容。
- 比较操作数应具有兼容类型；字符串、数字、布尔、日期时间和货币值不应跨不兼容领域进行比较。
- `duration(...)` 只能加到 DateTime 类值上或从 DateTime 类值中减去。
- `if(condition, whenTrue, whenFalse)` 要求 `condition` 为 Boolean；`whenTrue` 和 `whenFalse` 应解析为兼容的结果类型。

以下派生属性场景优先使用可机器检查表达式：

- 业务窗口和截止时间：`expiredAt = startedAt + duration("PT30M")`。
- 金额传递：`payableAmount = OrderSalesContract.orderAmount`。
- 金额计算，包括退款、赔偿、违约金、费用、税费、折扣、佣金和结算值：`refundAmount = PaymentConfirmation.paidAmount - CouponConfirmation.discountAmount`。
- 数量传递和计算，包括下单、预留、发运、验收、取消、退货和可用数量：`availableQuantity = InventoryConfirmation.totalQuantity - InventoryConfirmation.reservedQuantity`。
- 资格、权限或能力标志：`cancelable = notNull(PaymentConfirmation.confirmedAt) && isNull(ShipmentConfirmation.confirmedAt)`。
- 验收或质量指标：`accepted = QualityInspectionConfirmation.defectRate <= QualityContract.maxDefectRate`。
- SLA 和违约检测：`slaBreached = DeliveryConfirmation.confirmedAt > ShipmentFulfillmentRequest.expiredAt`。
- 条件赔偿或回退值：`compensationAmount = if(slaBreached == true, PaymentConfirmation.paidAmount * 0.1, 0)`。
- 从证据完成情况派生的状态分类：`fulfillmentStatus = if(notNull(DeliveryAcceptanceConfirmation.confirmedAt), "COMPLETED", "IN_PROGRESS")`。
- 风险、复核或升级决策：`manualReviewRequired = OrderSalesContract.orderAmount >= 5000 || BuyerRiskConfirmation.riskLevel == "HIGH"`。
- 跨证据一致性检查：`amountMatched = PaymentConfirmation.paidAmount == OrderSalesContract.orderAmount`。

## 文件更新

对于现有模型的更新，直接更新 YAML 文件：

- 在 `entities/` 下为每个新实体创建一个新的实体 YAML 文件。
- 在 `relationships/` 下为每个新关系创建一个新的关系 YAML 文件。
- 当现有实体或关系的业务语义发生变化时，覆盖对应 YAML 文件。
- 当语义被移除时，删除过时的实体或关系 YAML 文件。
- 删除实体时，必须在同一次更新中删除每个相关关系文件。

文件更新规则：

- 除非业务概念本身被重命名，否则当标签、属性、上下文成员关系或备注发生变化时，现有实体保持其 `name` 不变。
- 新实体使用当前模型目录中不存在的 `name` 值。
- 关系 `source` 和 `target` 可以引用现有实体名，也可以引用同一次建模任务中新建的实体名。
- 绝不要保留其 `source` 或 `target` 实体文件已不存在的关系文件。
- 当前文件内容代表当前模型状态。

每次文件更新后，针对模型目录运行 YAML 自检，并在回复前修复报告的问题。如果需要假设或人工复核提醒，请将其纳入适当的实体/关系 `notes` 字段，或在模型文件外说明。

## 建模反模式

- 不要将 API、服务、消息队列、任务、数据库、表、页面、SDK、引擎或技术组件建模为 FM 实体，除非用户明确要求 FM 之外的实现设计。
- Domain Logic 和 Third Party 角色必须使用人的岗位/职位名称，而不是规则引擎、SDK、队列、风控服务或支付网关等技术组件名称。
- 不要将同一业务语义同时建模为 Proof 和 Evidence As Role。
- 不要将 Contract 直接连接到 Contract，也不要直接连接到另一个上下文的 Request/Confirmation。
- 不要使用数组、逗号分隔名称、通配符或自定义端点载荷作为关系端点。
- 不要在单个关系上放置 `1:n` 等聚合基数。用多个 1:1 关系表示一对多。

## 自检清单

写入 YAML 文件并运行自检后，手动验证：

- 每个重要业务对象都在 Contract、Thing、Evidence 或属性中有归属。
- 每个有意义的业务责任都有 Fulfillment Request 时段以及一次或多次 Fulfillment Confirmation 时刻；若多个 Request 共用一个 Confirmation，应有明确业务依据。
- 每个 Request 都有清晰的 Contract 来源，并至少有一个直接或可追溯的 Confirmation 后继；缺少确认凭证时应作为违约或未解决项说明。
- 每个需要参与的 Evidence 都恰好有一个责任参与方，优先为相邻 Party Role；若直接连接 Participant Party，应说明未使用 Party Role 的原因。
- 每个非平凡规则都可追溯到 `precondition`、`calculationRule`、Domain Role 或备注。
- 每个下游信号都表示为证据流或 Evidence As Role 桥接。
- 跨上下文关系符合词典约束：可通过具体时刻类凭证直接关联、通过 Evidence As Role 扮演关系关联，或通过共同 Participant Party 间接关联；不得用 Contract 直接连接另一个 Contract。
- Third Party Role 只连接到 Proof 或 Evidence As Role；Context Role 只表达未展开的外部上下文依赖，不替代当前上下文内应建模的 Request/Confirmation。
- 实体名和关系文件名唯一。
- 关系 `source` 和 `target` 各自只引用一个已存在实体 `name`。
- FM 图中不出现展示层字段。
- YAML 文件有效，每个文件只包含一个对象，并且每个对象使用 `type: summary`、`type: entity` 或 `type: relationship`。
- 无法修复的无效关系或不确定实体应从图载荷中移除，或在图外标记为未解决。
