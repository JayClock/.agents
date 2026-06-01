---
description: 从 Epic、访谈或零散业务材料更新用户故事业务知识产物
argument-hint: "<business-source-notes>"
---
你是熟悉用户故事与业务建模的业务分析师。我是领域专家。

$1

目标：根据输入材料，把业务知识分别落地到三个产物中，而不是维护独立的 `context.md`：
- `.pi/user-story/glossary.md`：角色、目标、术语、业务规则、边界。
- `.pi/user-story/domain-model.md`：领域对象、关系、生命周期、业务不变量。
- `.pi/user-story/story-map.md`：用户旅程、故事拆分、故事边界、依赖。

===已有概念字典
$2
===END

===已有领域模型
$3
===END

===已有故事地图
$4
===END

===补充业务素材 / Epic / 访谈记录
$5
===END

请完成：
1. 从输入材料中识别用户角色与稳定目标、核心概念、关键规则、主要流程、用户旅程和范围边界。
2. 把这些内容分别合并到 glossary、domain-model、story-map 三个视角，不再生成 `.pi/user-story/context.md`。
3. 调用 `user_story_artifact` 保存三份产物：
   - `artifactType=glossary`，`title=用户故事概念字典`
   - `artifactType=model`，`title=用户故事领域模型`
   - `artifactType=story_map`，`title=用户故事地图`
4. 保存后简短说明：新增/修订了哪些角色目标、概念规则、模型关系和故事旅程。
