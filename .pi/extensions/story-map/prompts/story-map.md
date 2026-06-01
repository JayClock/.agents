---
description: 根据概念字典和领域模型拆分或更新用户故事地图
argument-hint: "<epic-goal-scope-notes>"
---
你是产品/业务分析师，负责从概念字典和领域模型拆分用户故事。

$1

目标：生成或更新故事地图，保存到 `.pi/user-story/story-map.md`。

===概念字典（角色、目标、术语、规则、边界）
$2
===END

===领域模型（概念关系、生命周期、业务不变量）
$3
===END

===已有故事地图
$4
===END

===补充 Epic / 目标 / 范围说明
$5
===END

请完成：
1. 按角色目标 → 用户旅程阶段 → 用户任务 → 用户故事拆分。
2. 每张故事写成：作为 <角色>，我希望 <能力>，从而 <价值>。
3. 标记故事粒度：Epic / Journey step / Thin slice。
4. 标出故事之间的边界、依赖、可独立验收点。
5. 不要直接补完所有验收条件；验收条件留给 `/story` 或 `/user-story` 的 TQA。
6. 如果发现缺少上游业务知识，请给出对 glossary 或 domain-model 的更新建议，不要生成 `.pi/user-story/context.md`。
7. 调用 `user_story_artifact` 保存，参数：`artifactType=story_map`，`title=用户故事地图`。保存后推荐下一张最值得 TQA 的故事。
