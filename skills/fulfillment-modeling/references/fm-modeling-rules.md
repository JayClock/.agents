# Fulfillment Modeling Rules

Use these rules when a task needs precise Fulfillment Modeling generation or validation.

## FM Process

1. Contract context first: identify Contract and its key Party Roles before other entities. Treat one Contract as one primary chain and identify the contracting sides first. Participant Party is optional supporting information, not the main modeling entry.
2. Presales evidence: add RFP and Proposal only when the requirement contains a presales stage. If no presales stage exists, start directly from Contract.
3. Evidence-first discovery: within each Contract context, first look for the main cash movement evidence. Create the money-related evidence that best anchors the business obligation and list key attributes such as business time point, amount, currency, payment window, quantity, or refund amount when applicable. If cash movement is weak or absent, start from the key KPI or acceptance evidence instead.
4. Attribute source tracing: for every key attribute on the current evidence, trace its source and keep the source path clear. A source may only come from user input, a prior evidence node, or algorithmic calculation. Do not keep attributes whose source cannot be explained.
5. Main fulfillment items: return from the anchor evidence to the rights and obligations it proves, then discover the surrounding evidence needed to establish, request, and confirm those obligations. Model each concrete responsibility as Fulfillment Request -> Fulfillment Confirmation pairs, and ensure every evidence node carries the key attributes needed for business traceability.
6. Exceptions and breach flows: for refund, cancellation, service suspension, reversal, compensation, and similar breach or exception flows, repeat the same evidence discovery method from the related money evidence or KPI/acceptance evidence, then model them as their own Request -> Confirmation pairs. Continue expanding breach handling until the requirement reaches an external dispute or litigation boundary.
7. Evidence flow before roles: first complete the mutually connected evidence flow, then refine the model around each evidence by adding the roles involved in creating, requesting, confirming, calculating, or bridging it.
8. Party role modeling: extract Party Roles for each business subject and connect them to Contract or to the evidence they participate in. A Party Role expresses identity-in-context, responsibility, and participation; it does not replace concrete business actions. Add Participant Party only when explicit party identity matters; connect Participant Party -> Party Role -> Contract.
9. Role splitting: add Party Role, Evidence As Role, Third Party Role, Context Role, and Domain Role according to business intent. For Domain Logic and Third Party roles, first ask what real-world job did this work before software existed, then name the role with job/position semantics.
10. Participation rule: every RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence must have exactly one participating Party Role.
11. Other Evidence vs Evidence As Role:
   - Use Other Evidence when a confirmation produces a business document or byproduct that stays inside the same context.
   - Use Evidence As Role when that same semantic bridges contexts.
   - Do not keep both nodes for the same business semantic.
12. Evidence As Role bridge rule: only use Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation. Do not connect Evidence As Role to Contract, Fulfillment Request, Proposal, or RFP. Evidence As Role belongs to the Context of the source confirmation that produced it.
13. Third Party Role and Context Role may only participate in Other Evidence or Evidence As Role. They must not directly participate in RFP, Proposal, Contract, Fulfillment Request, or Fulfillment Confirmation.
14. Multi-contract handling:
   - One Contract equals one primary chain.
   - Each Contract context independently follows the full process.
   - Each Context contains its own chain from RFP or Contract through terminal Other Evidence or Evidence As Role.
   - Context does not contain Participant Party nodes.
   - The same real-world party may appear as different Party Roles in different contexts through one external Participant Party.
   - Different contract contexts may only bridge through Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.
   - Do not connect Contract directly to Contract or to another context's Request/Confirmation.
15. Boundary and flow: after roles and participants are clear, place Party and Thing into the appropriate domain boundaries. Edges should express evidence flow, role participation, and context collaboration while keeping business control flow separate from domain calculation logic.

## Entity Categories

- Evidence: RFP, Proposal, Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence.
- Participant: Party, Thing.
- Role: Party Role, Domain Role, Third Party Role, Context Role, Evidence As Role.
- Context: bounded business context containers such as payment, inventory, invoice, delivery, subscription, service, or support.

## Graph Output

For a new model, return the complete model as React Flow-shaped nodes plus edges:

```json
{
  "summary": "短摘要",
  "nodes": [
    {
      "id": "node-1",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "data": {
        "label": "销售合同",
        "name": "SalesContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "合同签署完成的业务时间"
          },
          {
            "name": "contractAmount",
            "label": "合同金额",
            "valueType": "Money",
            "required": true,
            "meaning": "双方约定的履约金额"
          }
        ],
        "notes": "可选说明"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "type": "smoothstep",
      "label": "合同触发履约申请"
    }
  ],
  "_meta": {
    "validationNotes": []
  }
}
```

Use stable AI-generated ids with explicit prefixes: node ids must start with `node-`, such as `node-1`, and edge ids must start with `edge-`, such as `edge-1`. These prefixes distinguish newly generated model elements from persisted production records. Node ids must be unique across `nodes`; node `data.name` values must be non-empty and unique across `nodes`; edge ids must be unique across `edges`. Every edge endpoint must reference a node id in the same model unless the caller provided an existing model with those ids.

Recommended node fields:

- `id`: stable identifier. For newly generated nodes, always use a `node-` prefix.
- `type`: must equal `data.category`, one of `Evidence`, `Participant`, `Role`, or `Context`. The self-check script enforces this so rendering type stays aligned with FM semantics.
- `position`: always return `{ "x": 0, "y": 0 }` for generated nodes. Do not compute layout positions; the frontend owns all layout calculation.
- `parentId`: parent Context node id for child nodes inside a context. Context nodes must appear before their children.
- `extent`: use `"parent"` when child movement should stay inside the context container.
- `data.label`: human-readable business label.
- `data.name`: concise technical or English identifier; must be unique across nodes in the same model.
- `data.category`: `Evidence`, `Participant`, `Role`, or `Context`.
- `data.kind`: concrete FM kind such as `Bounded Context`, `Contract`, `Party Role`, `Fulfillment Request`, `Fulfillment Confirmation`, `Evidence As Role`, or `Other Evidence`.
- `data.attributes`: optional array for intrinsic business attributes of the node, including lifecycle time semantics when relevant. Each item should include `name`, `label`, `valueType`, `required`, and `meaning` when known.
  Evidence lifecycle attributes are mandatory for these kinds: RFP/Proposal/Fulfillment Request include `startedAt` and `expiredAt`; Contract includes `signedAt`; Fulfillment Confirmation includes `confirmedAt`; Other Evidence includes `createdAt`. Each mandatory lifecycle item must use `valueType: "DateTime"` and `required: true`.
- `data.notes`: optional short explanation.

Recommended edge fields:

- `id`: stable identifier. For newly generated edges, always use an `edge-` prefix.
- `source`: source node id.
- `target`: target node id.
- `type`: React Flow edge type such as `smoothstep`, `step`, `straight`, or `default`.
- `label`: short business phrase explaining the relationship.
- `sourceHandle` / `targetHandle`: optional handle ids when a custom node exposes multiple ports.

For an update to a large existing model, return only changes when full output would be wasteful:

```json
{
  "summary": "短摘要",
  "changes": {
    "addNodes": [],
    "updateNodes": [],
    "deleteNodes": [],
    "addEdges": [],
    "updateEdges": [],
    "deleteEdges": []
  },
  "_meta": {
    "validationNotes": []
  }
}
```

Complete example for a medium-sized model:

```json
{
  "summary": "用户购买付费专栏，完成支付后平台开通阅读权限；若专栏长期断更，用户可申请全额退款。",
  "nodes": [
    {
      "id": "node-context-1",
      "type": "Context",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "专栏订阅上下文",
        "name": "ColumnSubscriptionContext",
        "category": "Context",
        "kind": "Bounded Context"
      }
    },
    {
      "id": "node-context-2",
      "type": "Context",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "支付上下文",
        "name": "PaymentContext",
        "category": "Context",
        "kind": "Bounded Context"
      }
    },
    {
      "id": "node-1",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "平台用户",
        "name": "PlatformUser",
        "category": "Participant",
        "kind": "Party"
      }
    },
    {
      "id": "node-2",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "专栏平台",
        "name": "ColumnPlatform",
        "category": "Participant",
        "kind": "Party"
      }
    },
    {
      "id": "node-3",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "付费专栏",
        "name": "PaidColumn",
        "category": "Participant",
        "kind": "Thing"
      }
    },
    {
      "id": "node-4",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "订阅用户",
        "name": "SubscriberRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-5",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "专栏服务提供方",
        "name": "ColumnProviderRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-6",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "专栏订阅订单",
        "name": "ColumnSubscriptionContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户提交订阅订单并形成订阅合同的业务时间"
          },
          {
            "name": "orderedAt",
            "label": "下单时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户提交专栏订阅订单的业务时间"
          },
          {
            "name": "columnPrice",
            "label": "专栏价格",
            "valueType": "Money",
            "required": true,
            "meaning": "专栏订阅应付金额"
          },
          {
            "name": "paymentDeadlineAt",
            "label": "支付截止时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "下单后15分钟内完成支付的截止时间"
          }
        ]
      }
    },
    {
      "id": "node-7",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "阅读权限开通申请",
        "name": "AccessProvisionRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台收到支付成功后发起权限开通的时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "阅读权限开通申请的业务失效时间"
          },
          {
            "name": "subscriptionOrderId",
            "label": "订阅订单号",
            "valueType": "String",
            "required": true,
            "meaning": "对应的专栏订阅订单标识"
          }
        ]
      }
    },
    {
      "id": "node-8",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "阅读权限开通确认",
        "name": "AccessProvisionConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台完成专栏阅读权限开通的业务时间"
          },
          {
            "name": "accessExpiresAt",
            "label": "权限到期时间",
            "valueType": "DateTime",
            "required": false,
            "meaning": "如有限期则记录阅读权限到期时间"
          }
        ]
      }
    },
    {
      "id": "node-9",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "全额退款申请",
        "name": "FullRefundRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户因专栏长期断更发起退款申请的时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "退款申请的业务失效时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "申请退回的全额金额"
          },
          {
            "name": "breachReason",
            "label": "退款原因",
            "valueType": "String",
            "required": true,
            "meaning": "触发退款的长期断更原因说明"
          }
        ]
      }
    },
    {
      "id": "node-10",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "全额退款确认",
        "name": "FullRefundConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台确认执行全额退款的业务时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际确认退回的金额"
          }
        ]
      }
    },
    {
      "id": "node-11",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "付款方",
        "name": "PayerRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-12",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "收款方",
        "name": "PayeeRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-13",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付订单",
        "name": "PaymentContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付订单建立并形成支付合同的业务时间"
          },
          {
            "name": "createdAt",
            "label": "创建时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付订单建立的业务时间"
          },
          {
            "name": "payableAmount",
            "label": "应付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "本次支付订单需要支付的金额"
          },
          {
            "name": "paymentMethod",
            "label": "支付方式",
            "valueType": "String",
            "required": true,
            "meaning": "移动支付方式标识"
          }
        ]
      }
    },
    {
      "id": "node-14",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付申请",
        "name": "PaymentRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户发起移动支付的业务时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付申请的业务失效时间"
          },
          {
            "name": "amount",
            "label": "支付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "本次支付申请金额"
          }
        ]
      }
    },
    {
      "id": "node-15",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付成功确认",
        "name": "PaymentSuccessConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "移动支付成功的业务时间"
          },
          {
            "name": "paidAmount",
            "label": "实付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际支付成功的金额"
          },
          {
            "name": "paymentChannelTxnId",
            "label": "渠道流水号",
            "valueType": "String",
            "required": true,
            "meaning": "第三方支付渠道返回的交易流水号"
          }
        ]
      }
    },
    {
      "id": "node-16",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付成功凭证",
        "name": "PaymentSuccessEvidenceRole",
        "category": "Role",
        "kind": "Evidence As Role"
      }
    },
    {
      "id": "node-17",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "退款确认凭证",
        "name": "RefundConfirmationEvidenceRole",
        "category": "Role",
        "kind": "Evidence As Role"
      }
    },
    {
      "id": "node-18",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "退款出款确认",
        "name": "RefundPayoutConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "退款资金退回完成的业务时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际退回用户的金额"
          }
        ]
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-4",
      "type": "smoothstep",
      "label": "用户扮演订阅用户"
    },
    {
      "id": "edge-2",
      "source": "node-2",
      "target": "node-5",
      "type": "smoothstep",
      "label": "平台扮演服务提供方"
    },
    {
      "id": "edge-3",
      "source": "node-1",
      "target": "node-11",
      "type": "smoothstep",
      "label": "用户扮演付款方"
    },
    {
      "id": "edge-4",
      "source": "node-2",
      "target": "node-12",
      "type": "smoothstep",
      "label": "平台扮演收款方"
    },
    {
      "id": "edge-5",
      "source": "node-3",
      "target": "node-6",
      "type": "smoothstep",
      "label": "专栏是订阅标的"
    },
    {
      "id": "edge-6",
      "source": "node-4",
      "target": "node-6",
      "type": "smoothstep",
      "label": "订阅用户参与订单"
    },
    {
      "id": "edge-7",
      "source": "node-5",
      "target": "node-6",
      "type": "smoothstep",
      "label": "服务提供方参与订单"
    },
    {
      "id": "edge-8",
      "source": "node-6",
      "target": "node-7",
      "type": "smoothstep",
      "label": "订单触发权限开通申请"
    },
    {
      "id": "edge-9",
      "source": "node-5",
      "target": "node-7",
      "type": "smoothstep",
      "label": "服务提供方发起开通申请"
    },
    {
      "id": "edge-10",
      "source": "node-7",
      "target": "node-8",
      "type": "smoothstep",
      "label": "申请得到开通确认"
    },
    {
      "id": "edge-11",
      "source": "node-5",
      "target": "node-8",
      "type": "smoothstep",
      "label": "服务提供方确认开通"
    },
    {
      "id": "edge-12",
      "source": "node-6",
      "target": "node-9",
      "type": "smoothstep",
      "label": "订单可触发退款申请"
    },
    {
      "id": "edge-13",
      "source": "node-4",
      "target": "node-9",
      "type": "smoothstep",
      "label": "订阅用户发起退款申请"
    },
    {
      "id": "edge-14",
      "source": "node-9",
      "target": "node-10",
      "type": "smoothstep",
      "label": "申请得到退款确认"
    },
    {
      "id": "edge-15",
      "source": "node-5",
      "target": "node-10",
      "type": "smoothstep",
      "label": "服务提供方确认退款"
    },
    {
      "id": "edge-16",
      "source": "node-11",
      "target": "node-13",
      "type": "smoothstep",
      "label": "付款方参与支付订单"
    },
    {
      "id": "edge-17",
      "source": "node-12",
      "target": "node-13",
      "type": "smoothstep",
      "label": "收款方参与支付订单"
    },
    {
      "id": "edge-18",
      "source": "node-13",
      "target": "node-14",
      "type": "smoothstep",
      "label": "支付订单触发支付申请"
    },
    {
      "id": "edge-19",
      "source": "node-11",
      "target": "node-14",
      "type": "smoothstep",
      "label": "付款方发起支付申请"
    },
    {
      "id": "edge-20",
      "source": "node-14",
      "target": "node-15",
      "type": "smoothstep",
      "label": "申请得到支付成功确认"
    },
    {
      "id": "edge-21",
      "source": "node-12",
      "target": "node-15",
      "type": "smoothstep",
      "label": "收款方确认收款成功"
    },
    {
      "id": "edge-22",
      "source": "node-15",
      "target": "node-16",
      "type": "smoothstep",
      "label": "支付成功产生跨上下文凭证"
    },
    {
      "id": "edge-23",
      "source": "node-16",
      "target": "node-8",
      "type": "smoothstep",
      "label": "支付成功支撑权限开通确认"
    },
    {
      "id": "edge-24",
      "source": "node-10",
      "target": "node-17",
      "type": "smoothstep",
      "label": "退款确认产生跨上下文凭证"
    },
    {
      "id": "edge-25",
      "source": "node-17",
      "target": "node-18",
      "type": "smoothstep",
      "label": "退款确认支撑退款出款确认"
    },
    {
      "id": "edge-26",
      "source": "node-12",
      "target": "node-18",
      "type": "smoothstep",
      "label": "收款方确认退款出款"
    }
  ],
  "_meta": {
    "validationNotes": [
      "示例同时展示了主合同上下文、支付上下文、退款异常流，以及通过 Evidence As Role 进行的跨上下文确认桥接。",
      "建模时仍应根据具体需求补充属性来源说明，例如 columnPrice 来自 Proposal 或商品定价规则，paymentDeadlineAt 来自下单时间加15分钟算法计算。"
    ]
  }
}
```

Use `changes` as an editing or transport optimization only. It must still preserve the conceptual model as nodes and edges. Within `changes`, do not repeat the same node id across `addNodes`, `updateNodes`, or `deleteNodes`, and do not repeat the same edge id across `addEdges`, `updateEdges`, or `deleteEdges`. Prefer full `nodes` and `edges` for new models, small models, or when the caller has not provided existing ids.

Use `_meta` for non-rendered diagnostics. Put validation notes, assumptions, and manual review reminders in `_meta.validationNotes`. Do not put `validationNotes` at the top level.

## Naming

- Keep `data.label` as a human-readable business label. Do not append lifecycle timestamp suffixes such as `started_at`, `expired_at`, `confirmed_at`, `signed_at`, or `created_at` to node labels.
- Return key time semantics as items in `data.attributes` when helpful.
- Return entity attributes in `data.attributes`; do not encode them in `data.label`.
- Keep `data.attributes` for state or facts owned by that node.
- Required lifecycle attributes must be present in `data.attributes` with `valueType: "DateTime"` and `required: true`:
  - RFP, Proposal, and Fulfillment Request must include `startedAt` and `expiredAt`.
  - Contract must include `signedAt`.
  - Fulfillment Confirmation must include `confirmedAt`.
  - Other Evidence must include `createdAt`.
- Model concrete business actions, decisions, calculations, and lifecycle transitions with Fulfillment Request/Fulfillment Confirmation nodes and flow edges.
- Evidence As Role should usually include a `createdAt` DateTime item in `data.attributes`.
- Domain Logic and Third Party roles must use human job/position names, not technical component names such as rule engine, SDK, queue, risk service, or payment gateway.

## Edge Rules

Main chain:

- RFP -> Proposal -> Contract -> Fulfillment Request -> Fulfillment Confirmation.
- If no presales stage exists, start from Contract.
- Proposal -> Contract is required when Proposal exists.
- Contract -> Fulfillment Request is required; do not create standalone Fulfillment Request.
- Proposal must not connect directly to Fulfillment Request.
- Contract -> Fulfillment Request is usually one-to-many.
- Fulfillment Request -> Fulfillment Confirmation is one-to-one.
- External second responses may cascade as Fulfillment Confirmation -> Fulfillment Confirmation.

Participants:

- Thing usually connects to Contract and may connect to RFP, Proposal, or Fulfillment Request.
- Prefer Party Role participation. Add Participant Party only as identity support.
- In multi-contract models, one Participant Party may connect to multiple Party Roles when they represent the same real-world subject.

Roles:

- RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence each connect to exactly one Party Role.
- Party Role names should describe the business capacity or responsibility, such as Customer, Supplier, Payer, or Service Provider. Model concrete actions, decisions, calculations, and lifecycle transitions with Fulfillment Request/Fulfillment Confirmation nodes and flow edges, not on the Party Role itself.
- Domain Logic Role connects to RFP, Proposal, or Request as a business calculator.
- Third Party Role and Context Role only connect to Other Evidence or Evidence As Role.
- Evidence As Role is only for cross-context bridges and only in the chain Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.

Direction:

- Use cause -> result or initiator -> action.
- Avoid meaningless cycles.
- Ensure the main flow can be read left-to-right.

## Executable Self-Check

Before returning machine-readable graph JSON, run:

```bash
python3 .agents/skills/fulfillment-modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

The script checks:

- Node ids, node `data.name` values, and edge ids are not duplicated.
- Every node `type` equals its `data.category`.
- Evidence lifecycle attributes are present with `valueType: "DateTime"` and `required: true`: RFP/Proposal/Fulfillment Request require `startedAt` and `expiredAt`; Contract requires `signedAt`; Fulfillment Confirmation requires `confirmedAt`; Other Evidence requires `createdAt`.
- Every mandatory edge has known endpoints.
- Every RFP/Proposal/Request/Confirmation/Other Evidence has exactly one Party Role neighbor.
- Every Fulfillment Request has one direct Contract predecessor and one Fulfillment Confirmation successor.
- Cross-context edges are limited to Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation.
- Evidence As Role does not point to Fulfillment Request.
- Unfixable invalid edges or uncertain nodes are removed or marked unresolved.

After the script passes, manually review semantic duplication:

- Other Evidence and Evidence As Role do not duplicate the same semantic in the same model.
