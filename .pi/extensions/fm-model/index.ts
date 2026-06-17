import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
	buildPrompt,
	ensureUserStoryArtifactTemplates,
	readFmModelSnapshot,
	readProjectFile,
	sendPrompt,
	type PromptCommandContext,
} from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n领域模型：\n$3\n\n故事地图：\n$4\n\nFM 建模材料：\n$5\n\n输入要求：优先从 Epic / 角色-价值目标切入；Epic 只用于发现 Contract / Bounded Context 与履约责任链，不作为 FM 实体。区分现实主体 Party 与上下文身份 Party Role；关键签约方、受益方、履约方需要判断是否建立 Participant Party，并保持 Participant Party -> Party Role -> Contract 链路。\n\n请按 Fulfillment Modeling 生成/更新 .pi/user-story/fm-model/ 下的 YAML 图模型，运行自检，并把派生摘要回写到 glossary、domain-model、story-map。`;

export default function fmModelExtension(pi: ExtensionAPI) {
	pi.registerCommand("fm-model", {
		description: "按 Fulfillment Modeling 生成/更新 .pi/user-story/fm-model YAML 源模型并派生用户故事视图",
		handler: async (args, ctx: PromptCommandContext) => {
			const initialized = await ensureUserStoryArtifactTemplates(ctx.cwd);
			if (initialized.length > 0 && ctx.hasUI) {
				ctx.ui.notify(`已基于模板初始化：${initialized.join("、")}`, "info");
			}

			const [glossary, model, storyMap, fmSnapshot] = await Promise.all([
				readProjectFile(ctx.cwd, ".pi/user-story/glossary.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/domain-model.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/story-map.md"),
				readFmModelSnapshot(ctx.cwd),
			]);

			let notes = args?.trim() || "";
			if (ctx.hasUI) {
				notes =
					(await ctx.ui.editor(
						"FM 建模输入：Epic / 范围 / 履约链",
						notes ||
							"输入要求：优先从 Epic / 角色-价值目标切入；Epic 用来识别 Contract / Bounded Context 和履约责任链，不要在 FM YAML 中建 Epic 实体。留空则基于现有 glossary/domain-model/story-map 和已有 FM YAML 更新。\n\n建议填写：\nEpic：作为 <角色>，我希望 <能力>，从而 <价值>。\n真正受益者 / 稳定目标：\n- \n现实主体 Party 候选（现实中独立存在的人、组织或机构）：\n- \nParty Role 映射（上述主体在本合同 / 上下文中的身份、责任、权限）：\n- \n业务价值（不要复述能力）：\n- \n建模范围 / 合同上下文候选：\n- \n履约凭证 / 主流程（Request / Confirmation，如有）：\n- \n异常流 / 规则 / 边界：\n- \n已有故事 / 依赖 / 不纳入范围：\n- \n\n通用示例（仅说明填法，不限定行业）：\nEpic：作为权益申请方，我希望完成某项业务承诺所需的申请或支付，从而获得可被证明的权益或服务结果。\n真正受益者 / 稳定目标：申请方希望在满足约定条件后获得明确、可追踪的业务结果。\n现实主体 Party 候选：申请方主体；履约方主体；必要时包括第三方机构或代理主体。\nParty Role 映射：申请方主体在本上下文中承担请求方 / 购买方 / 委托方等身份；履约方主体承担提供方 / 受托方 / 确认方等身份。\n业务价值：权利义务、履约结果和异常责任边界可被证明。\n建模范围 / 合同上下文候选：一次清晰的业务承诺与履约链。\n履约凭证 / 主流程：按业务需要记录履约请求、履约确认或二者之间的关系。\n异常流 / 规则 / 边界：条件不满足、履约失败、撤销、退款、补偿、外部争议等按业务范围决定是否建模。",
					)) ?? "";
				ctx.ui.setWidget("fm-model", [
					"FM Model：生成/更新 .pi/user-story/fm-model YAML，并派生 glossary/domain-model/story-map。",
				]);
			}

			const fmNotes = [
				"===现有 FM YAML 模型快照",
				fmSnapshot.trim() || "（暂无 FM YAML 模型）",
				"===END",
				"",
				"===本次补充材料 / 建模范围",
				notes.trim() || "（无补充；请基于现有三份用户故事产物和 FM YAML 更新）",
				"===END",
			].join("\n");

			const prompt = await buildPrompt(join(baseDir, "prompts", "fm-model.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: model.trim() || "（暂无）",
				storyMap: storyMap.trim() || "（暂无）",
				notes: fmNotes,
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
