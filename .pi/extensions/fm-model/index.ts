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

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n领域模型：\n$3\n\n故事地图：\n$4\n\nFM 建模材料：\n$5\n\n输入要求：优先从 Epic / 角色-价值目标切入；Epic 只用于发现 Contract / Bounded Context 与履约责任链，不作为 FM 实体。\n\n请按 Fulfillment Modeling 生成/更新 .pi/user-story/fm-model/ 下的 YAML 图模型，运行自检，并把派生摘要回写到 glossary、domain-model、story-map。`;

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
							"输入要求：优先从 Epic / 角色-价值目标切入；Epic 用来识别 Contract / Bounded Context 和履约责任链，不要在 FM YAML 中建 Epic 实体。留空则基于现有 glossary/domain-model/story-map 和已有 FM YAML 更新。\n\n建议填写：\nEpic：作为 <角色>，我希望 <能力>，从而 <价值>。\n真正受益者 / 稳定目标：\n- \n业务价值（不要复述能力）：\n- \n建模范围 / 合同上下文候选：\n- \n履约责任 / 主流程（Request -> Confirmation）：\n- \n异常流 / 规则 / 边界：\n- \n已有故事 / 依赖 / 不纳入范围：\n- \n\n示例：\nEpic：作为订阅客户，我希望购买会员订阅，从而持续获得会员权益。\n真正受益者 / 稳定目标：订阅客户希望在付款后获得有效会员权益。\n业务价值：权益开通可被证明，后续取消或退款有明确责任边界。\n建模范围 / 合同上下文候选：客户购买会员订阅。\n履约责任 / 主流程：客户支付后平台开通会员权益。\n异常流 / 规则 / 边界：支付失败、取消订阅、退款；支付成功且未退款时会员有效。",
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
