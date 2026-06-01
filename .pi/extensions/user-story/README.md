# User Story TQA pi extension

用于辅助编写**单张用户故事**：聚焦问题定义，使用 TQA（Thought-Question-Answer）让 LLM 先向领域专家提问，再生成 Given/When/Then 验收条件。

> 使用者教程见 `.pi/user-story/README.md`。
>
> 完整业务知识管理流程已拆成多个 project-local extensions，见 `.pi/extensions/README.md`。

## 本 extension 职责

```text
已有业务知识（glossary / domain-model / story-map）/ 用户故事
→ TQA 追问领域专家
→ 生成验收条件
→ 保存 .pi/user-story/sessions/*.story.md
```

## 命令

启动或在 pi 中执行 `/reload` 后可用。

- `/user-story`：交互式填写用户故事、业务知识上下文、相关故事，启动 TQA。
- `/story`：`/user-story` 的简写。
- `/story-template`：把 `templates/story-input.md` 粘贴到编辑器。
- `/story-method`：显示 `prompts/method.md` 方法摘要。

## 工具

- `user_story_question`：LLM 用来每次向领域专家提一个澄清问题；回答会进入 TQA 历史。
- `user_story_scenarios`：LLM 在信息足够后输出最终用户故事与 Given/When/Then 验收条件，并自动保存到 `.pi/user-story/sessions/*.story.md`。

## 可编辑文件

- 修改 `.pi/extensions/user-story/prompts/method.md` 调整方法论说明。
- 修改 `.pi/extensions/user-story/prompts/tqa.md` 调整 Agent 工作流。
- 修改 `.pi/extensions/user-story/templates/story-input.md` 调整手动输入模板。
- 修改 `.pi/user-story/glossary.md`、`.pi/user-story/domain-model.md`、`.pi/user-story/story-map.md` 维护跨故事共享的业务知识。
