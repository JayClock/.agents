# User Story workflow extensions

把从业务材料到 FM 源模型、概念字典、领域模型、故事地图、验收条件、模型检查的链路拆成多个 pi extension。

## 文档分工

- 使用者教程：`.pi/user-story/README.md`
  - 说明 Epic 怎么开始、派生视图与 `/story` 的区别、产物保存位置和推荐闭环。
- 扩展维护说明：本文档 `.pi/extensions/README.md`
  - 说明 extension 列表、命令/工具关系、prompt 参数约定、共享文件和维护注意事项。
- 单个 TQA extension 说明：`.pi/extensions/user-story/README.md`
  - 说明 `/story`、`/user-story`、TQA 工具和可编辑 prompt。

> 当前约定：业务知识直接落地并复用 FM 源模型与三份派生视图：
>
> - `.pi/user-story/fm-model/`
> - `.pi/user-story/glossary.md`
> - `.pi/user-story/domain-model.md`
> - `.pi/user-story/story-map.md`

## 推荐流程

```text
/fm-model       # 生成/更新 FM YAML 源模型并派生三份视图
  → /story 或 /user-story
  → /model-check
  → /fm-model   # 根据检查结果回写源模型并刷新派生视图
```

## Extensions

| Extension | 命令 / 工具 | 产物 | 作用 |
|---|---|---|---|
| `fm-model` | `/fm-model` | `.pi/user-story/fm-model/**`、三份 Markdown 派生视图 | 按 Fulfillment Modeling 生成/更新 YAML 源模型，运行自检，并派生 glossary/domain-model/story-map。 |
| `user-story` | `/story`, `/user-story` | `.pi/user-story/sessions/*.story.md` | 对单张用户故事做 TQA，并生成 Given/When/Then 验收条件。 |
| `model-check` | `/model-check` | `.pi/user-story/model-checks/*.model-check.md` | 用验收场景展开领域模型，检查缺失概念、关系错置和规则遗漏。 |
| `story-artifacts` | `user_story_artifact` tool | `.pi/user-story/**` | 通用保存工具，供其它 workflow extension 调用。 |

## Prompt template 变量约定

这些 extension 内部的 `prompts/*.md` 按 Pi prompt template 规范编写：

- frontmatter 使用 `description` 和 `argument-hint`。
- 模板变量使用 Pi 支持的 `$1`、`$2`、`$@`、`${@:N}`，不使用 Mustache 风格变量。
- prompt 正文不维护“输入字段说明”和示例，避免把模板说明混入业务上下文。
- 通用建模 prompt 的参数约定：`$1=method`，`$2=glossary`，`$3=domain-model`，`$4=story-map`，`$5=notes/scenario`。
- `user-story/prompts/tqa.md` 的参数约定：`$1=method`，`$2=workflow mode`，`$3=knowledge context`，`$4=user story`，`$5=related stories`。

## 共享业务知识文件

- `.pi/user-story/fm-model/`：FM YAML 源模型，包含 Contract、Role、Evidence、Request/Confirmation、关系和上下文边界。
- `.pi/user-story/glossary.md`：角色、目标、术语、业务规则、范围边界。
- `.pi/user-story/domain-model.md`：FM 派生的领域对象、关系、生命周期、业务不变量。
- `.pi/user-story/story-map.md`：从履约责任链派生的用户旅程、故事拆分、故事边界、依赖。
- `.pi/user-story/sessions/`：单张故事的 TQA 与验收条件。
- `.pi/user-story/model-checks/`：模型展开与检查报告。

## 模板初始化

- `.pi/user-story/*.md` 是项目运行时产物，不作为 extension 自动发现入口。
- 发布 extension 时，模板随包放在 `.pi/extensions/_story-workflow/templates/user-story/`。
- 第一次执行 `/fm-model` 时，如果目标项目缺少 `glossary.md`、`domain-model.md` 或 `story-map.md`，会先从模板初始化缺失文件，再把这些模板内容作为“已有产物”交给 Agent 基于业务素材生成正式产物。
- 初始化只处理缺失或空文件，不覆盖已有业务知识。

## `/fm-model` 输入要求

- 优先从 Epic / 角色-价值目标切入：`作为 <角色>，我希望 <能力>，从而 <价值>`。
- Epic 是 Contract / Bounded Context 与履约责任链的发现入口，不写成 FM YAML 实体。
- 建议同时给出：真正受益者、稳定业务目标、业务价值、范围边界、主流程 Request -> Confirmation、异常流、规则、依赖和不纳入范围。
- 如果没有补充输入，`/fm-model` 只基于现有 FM YAML 与三份派生视图审查刷新，不应凭空扩展业务范围。

## 使用建议

- 新领域/新产品：直接从 `/fm-model` 开始，输入 Epic、访谈、流程、规则和边界材料。
- 已有一批故事：先 `/fm-model` 稳定源模型并刷新派生视图，再进入 `/story`。
- 已有模型但没有验收条件：先 `/story`，再 `/model-check`。
- `/model-check` 发现的问题，优先回写到 `fm-model/`，再派生刷新 `glossary.md`、`domain-model.md` 或 `story-map.md`。

## 维护者检查清单

修改 workflow extension 时建议同时检查：

- 命令是否仍符合推荐流程：`/fm-model → /story → /model-check → /fm-model`。
- prompt 字段顺序是否仍符合共享约定：`$1=method`、`$2=glossary`、`$3=domain-model`、`$4=story-map`、`$5=notes/scenario`。
- 如果新增 artifact 类型，是否同步更新 `story-artifacts/index.ts`、本文档和 `.pi/user-story/README.md`。
- 如果新增命令，是否在 `Extensions` 表格和使用者教程中说明入口、输入和产物。
