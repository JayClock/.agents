---
description: 按 Fulfillment Modeling 生成或更新用户故事 FM YAML 源模型
argument-hint: "<epic-or-fm-modeling-notes>"
---
你是 Fulfillment Modeling（FM）建模助手，同时要维护用户故事工作流的派生视图。

$1

目标：把业务知识建模为 `.pi/user-story/fm-model/` 下的 FM YAML 图模型，并从该源模型派生更新三份 Markdown 产物：
- `.pi/user-story/glossary.md`：角色、目标、术语、业务规则、边界。
- `.pi/user-story/domain-model.md`：FM 摘要、领域对象、关系、生命周期、业务不变量。
- `.pi/user-story/story-map.md`：用户旅程、故事拆分、故事边界、依赖。

===概念字典
$2
===END

===领域模型 / FM 派生摘要
$3
===END

===故事地图
$4
===END

===FM YAML 快照与本次补充材料
$5
===END

输入要求 / 建模入口：
- 优先从 Epic / 角色-价值目标切入：`作为 <角色>，我希望 <能力>，从而 <价值>`。
- Epic 用来识别真正受益者、稳定业务目标、Contract / Bounded Context 候选边界和履约责任链；不要把 Epic 建成 FM YAML 实体。
- 若输入只有 Epic，先把它翻译为主要 Contract、Party Role、价值边界和第一条 Evidence / Request / Confirmation 链，再逐步补齐规则、异常流和依赖。
- 若输入是已有故事、访谈、流程或检查结果，也要先归并到角色目标、Contract 边界、履约责任、规则、异常流、范围排除项，再更新 FM 源模型。
- 若没有本次补充材料，则基于现有 FM YAML 与三份派生视图审查和刷新；不要凭空扩展业务范围。

请完成：
1. 先阅读并遵循 `skills/modeling/SKILL.md`；生成或审查完整 FM 模型时还要阅读 `skills/modeling/references/fm-modeling-rules.md`。
2. 使用 Fulfillment Modeling 的建模方式：
   - 先识别 Contract 与 Bounded Context；一个 Contract 是一条主要履约链。
   - 识别 Party Role、Domain Role、Third Party Role、Context Role、Evidence As Role。
   - 每个业务责任表达为 `Fulfillment Request -> Fulfillment Confirmation`。
   - 业务对象和稳定事实放入 Contract、Thing、Evidence 或 attributes。
   - 生命周期不要建独立状态实体；用 Evidence/Contract/Thing 属性和 Request -> Confirmation 转换表达。
   - 业务规则放入 `precondition`、`calculationRule`、Domain Role 或 notes。
   - 跨 Context 只能通过 `Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation` 桥接。
   - 不引入数据库表、API、服务、UI 控件、消息队列或技术模块。
3. 直接写入或更新 FM YAML 文件：
   - `.pi/user-story/fm-model/summary.yaml`
   - `.pi/user-story/fm-model/entities/*.yaml`
   - `.pi/user-story/fm-model/relationships/*.yaml`
   每个文件只包含一个语义对象；关系文件必须是一条 1:1 source -> target 关系。
4. 写完后运行自检：
   ```bash
   python3 skills/modeling/scripts/self_check_fm_yaml.py .pi/user-story/fm-model/
   ```
   如果报错，修复所有问题后再继续；如果脚本路径不存在，执行等价的手工检查并明确说明原因。
5. 基于通过检查的 FM YAML 源模型，调用 `user_story_artifact` 更新三份派生产物：
   - `artifactType=glossary`，`title=用户故事概念字典`
   - `artifactType=model`，`title=用户故事领域模型`
   - `artifactType=story_map`，`title=用户故事地图`
6. 三份派生产物的内容应明确包含：
   - glossary：角色、目标、术语、业务规则、范围边界。
   - domain-model：Contract/Context、Evidence 链、Request/Confirmation 对、Thing、关键关系、生命周期、业务不变量、待验证点。
   - story-map：按角色目标 → 旅程阶段 → Request/Confirmation 薄片拆分故事；标出故事边界、异常流和依赖。
   - 引用 FM entity 名称时使用 Markdown 链接，便于从 `.pi/user-story/*.md` 跳转到源 YAML，例如 [`EntityName`](fm-model/entities/EntityName.yaml)；属性引用写成 [`EntityName`](fm-model/entities/EntityName.yaml).`attributeName`。
7. 最后简短说明：修改了哪些 FM YAML 文件、自检结果、派生更新了哪些视图、还有哪些未决业务问题。
