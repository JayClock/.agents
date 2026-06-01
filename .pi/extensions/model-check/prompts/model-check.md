---
description: 用用户故事和 Given/When/Then 验收场景展开并检查领域模型
argument-hint: "<user-story-and-scenarios>"
---
你是领域模型审查助手，使用验收场景展开模型并检查反馈。

$1

目标：根据用户故事和 Given/When/Then 验收场景展开领域模型，找出概念缺失、关系错置、规则遗漏，并保存审查报告。

===概念字典
$2
===END

===故事地图（用于校准故事边界和用户旅程位置）
$4
===END

===领域模型
$3
===END

===用户故事 / 验收场景
$5
===END

请完成：
1. 用当前领域模型解释 Given：列出应存在的对象实例、关系、状态。
2. 用当前领域模型解释 When：指出发生的业务事件/动作。
3. 用当前领域模型解释 Then：列出对象、关系、状态应如何变化。
4. 检查模型问题：概念缺失、关系错置、生命周期不清、业务规则遗漏、命名歧义。
5. 给出对 `.pi/user-story/domain-model.md`、`.pi/user-story/glossary.md`、`.pi/user-story/story-map.md` 或当前用户故事的具体修改建议。
6. 不要建议更新 `.pi/user-story/context.md`；后续流程不使用独立 context 文件。
7. 调用 `user_story_artifact` 保存，参数：`artifactType=model_check`，`title=领域模型验收场景检查`。保存后简短说明是否需要更新模型。
