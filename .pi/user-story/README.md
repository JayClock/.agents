# User Story workflow

推荐流程：

```text
/fm-model
  → /story
  → /model-check
  → /fm-model
```

## 产物

- `fm-model/`：Fulfillment Modeling YAML 源模型。
- `glossary.md`：从 FM 源模型派生的角色、目标、术语、业务规则、范围边界。
- `domain-model.md`：从 FM 源模型派生的领域对象、关系、业务不变量。
- `story-map.md`：从 FM 履约责任链派生的用户旅程、故事拆分、故事边界、依赖。
- `sessions/`：单张用户故事 TQA 与 Given/When/Then。
- `model-checks/`：验收场景驱动的模型检查报告。

## 常用命令

- `/fm-model`：生成/更新 FM YAML 源模型，运行自检，并派生更新三份 Markdown 视图。
- `/story`：对单张用户故事做 TQA 并生成验收条件。
- `/model-check`：用验收场景检查模型缺失、规则遗漏和边界问题。
