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

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n领域模型：\n$3\n\n故事地图：\n$4\n\nFM 建模材料：\n$5\n\n请按 Fulfillment Modeling 生成/更新 .pi/user-story/fm-model/ 下的 YAML 图模型，运行自检，并把派生摘要回写到 glossary、domain-model、story-map。`;

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
						"FM 建模补充材料 / 范围说明",
						notes ||
							"字段说明：填写本次要建模或更新的业务材料、合同/履约链、角色、规则、异常流、边界；留空则基于现有 glossary/domain-model/story-map 和已有 FM YAML 更新。\n\n示例：\n合同：客户购买会员订阅。\n角色：订阅客户、平台经营方。\n责任：客户支付后平台开通会员权益；取消订阅时计算退款。\n规则：支付成功且未退款时会员有效。\n异常：支付失败、取消订阅、退款。\n\n请填写：\n建模范围 / 合同上下文：\n- \n\n履约责任 / 主流程：\n- \n\n异常流 / 规则 / 边界：\n- ",
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
