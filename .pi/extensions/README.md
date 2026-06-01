# User Story workflow extensions

把从业务材料到概念字典、领域模型、故事地图、验收条件、模型检查的链路拆成多个 pi extension。

## 文档分工

- 使用者教程：`.pi/user-story/README.md`
  - 说明 Epic 怎么开始、各命令怎么选、`/story-map` 与 `/story` 的区别、产物保存位置和推荐闭环。
- 扩展维护说明：本文档 `.pi/extensions/README.md`
  - 说明 extension 列表、命令/工具关系、prompt 参数约定、共享文件和维护注意事项。
- 单个 TQA extension 说明：`.pi/extensions/user-story/README.md`
  - 说明 `/story`、`/user-story`、TQA 工具和可编辑 prompt。

> 当前约定：后续流程**不读取** `.pi/user-story/context.md`。业务知识直接落地并复用这三份文件：
>
> - `.pi/user-story/glossary.md`
> - `.pi/user-story/domain-model.md`
> - `.pi/user-story/story-map.md`

## 推荐流程

```text
/story-context      # 从原始材料一次性更新 glossary / domain-model / story-map
  → /story-glossary # 可选：细化术语、角色目标、规则、边界
  → /domain-model   # 可选：细化领域对象、关系、不变量
  → /story-map      # 可选：细化用户旅程和故事拆分
  → /story 或 /user-story
  → /model-check
  → 回写 glossary / domain-model / story-map
```

## Extensions

| Extension | 命令 / 工具 | 产物 | 作用 |
|---|---|---|---|
| `story-context` | `/story-context` | `glossary.md`、`domain-model.md`、`story-map.md` | 从 Epic、访谈、零散材料一次性更新三份业务知识产物。 |
| `story-glossary` | `/story-glossary` | `.pi/user-story/glossary.md` | 提取/更新角色、目标、术语、业务规则、范围边界。 |
| `domain-model` | `/domain-model` | `.pi/user-story/domain-model.md` | 根据概念字典和故事地图生成/更新领域模型。 |
| `story-map` | `/story-map` | `.pi/user-story/story-map.md` | 从概念字典和领域模型拆分用户旅程、用户故事、故事边界。 |
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

- `.pi/user-story/glossary.md`：角色、目标、术语、业务规则、范围边界。
- `.pi/user-story/domain-model.md`：领域对象、关系、生命周期、业务不变量。
- `.pi/user-story/story-map.md`：用户旅程、故事拆分、故事边界、依赖。
- `.pi/user-story/sessions/`：单张故事的 TQA 与验收条件。
- `.pi/user-story/model-checks/`：模型展开与检查报告。

## 模板初始化

- `.pi/user-story/*.md` 是项目运行时产物，不作为 extension 自动发现入口。
- 发布 extension 时，模板随包放在 `.pi/extensions/_story-workflow/templates/user-story/`。
- 第一次执行 `/story-context` 时，如果目标项目缺少 `glossary.md`、`domain-model.md` 或 `story-map.md`，会先从模板初始化缺失文件，再把这些模板内容作为“已有产物”交给 Agent 基于业务素材生成正式产物。
- 初始化只处理缺失或空文件，不覆盖已有业务知识。

## 使用建议

- 新领域/新产品：从 `/story-context` 开始，一次性生成三份业务知识产物。
- 已有一批故事：先 `/story-glossary`，再 `/domain-model`，最后 `/story-map`。
- 已有模型但没有验收条件：先 `/story`，再 `/model-check`。
- `/model-check` 发现的问题，优先回写到 `glossary.md`、`domain-model.md` 或 `story-map.md`。

## 维护者检查清单

修改 workflow extension 时建议同时检查：

- 命令是否仍符合推荐流程：`/story-context → /story-map → /story → /model-check`。
- prompt 字段顺序是否仍符合共享约定：`$1=method`、`$2=glossary`、`$3=domain-model`、`$4=story-map`、`$5=notes/scenario`。
- 是否误引入 `.pi/user-story/context.md` 作为运行时依赖；当前约定是不读取它。
- 如果新增 artifact 类型，是否同步更新 `story-artifacts/index.ts`、本文档和 `.pi/user-story/README.md`。
- 如果新增命令，是否在 `Extensions` 表格和使用者教程中说明入口、输入和产物。
