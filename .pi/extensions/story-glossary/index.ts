import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { buildPrompt, readProjectFile, sendPrompt, type PromptCommandContext } from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n已有概念字典：\n$2\n\n已有领域模型：\n$3\n\n已有故事地图：\n$4\n\n材料：\n$5\n\n请生成/更新概念字典，并调用 user_story_artifact 保存 artifactType=glossary。`;

export default function storyGlossaryExtension(pi: ExtensionAPI) {
	pi.registerCommand("story-glossary", {
		description: "从用户故事/Epic 提取或更新概念字典 glossary.md",
		handler: async (args, ctx: PromptCommandContext) => {
			const [glossary, model, storyMap] = await Promise.all([
				readProjectFile(ctx.cwd, ".pi/user-story/glossary.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/domain-model.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/story-map.md"),
			]);
			let notes = args?.trim() || "";
			if (ctx.hasUI) {
				notes =
					(await ctx.ui.editor(
						"用户故事 / Epic / 补充材料（用于提取概念）",
						notes ||
							"字段说明：填写要提取概念的用户故事、Epic、术语、规则、边界或容易混淆的说法。\n\n示例：\n用户故事：作为下单客户，我希望查看已支付订单的配送进度，从而安排收货时间。\n补充术语：配送进度 = 已完成配送节点数 / 总配送节点数。\n规则：已取消订单不显示配送进度。\n\n请填写：\n用户故事 / Epic：\n- \n\n补充术语或规则：\n- ",
					)) ?? "";
				ctx.ui.setWidget("story-glossary", ["Story Glossary：提取概念字典，完成后会保存到 .pi/user-story/glossary.md"]);
			}
			const prompt = await buildPrompt(join(baseDir, "prompts", "glossary.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: model.trim() || "（暂无）",
				storyMap: storyMap.trim() || "（暂无）",
				notes: notes.trim() || "（无补充材料）",
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
