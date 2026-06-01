import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { buildPrompt, readProjectFile, sendPrompt, type PromptCommandContext } from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n领域模型：\n$3\n\n已有故事地图：\n$4\n\n补充：\n$5\n\n请拆分故事地图，并调用 user_story_artifact 保存 artifactType=story_map。`;

export default function storyMapExtension(pi: ExtensionAPI) {
	pi.registerCommand("story-map", {
		description: "根据概念字典和领域模型拆分故事地图 story-map.md",
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
						"补充 Epic / 目标 / 范围说明（可留空）",
						notes ||
							"字段说明：填写本次要拆分的 Epic、业务目标、角色旅程、范围、依赖和明确不做范围。\n\n示例：\nEpic：客户自助查询订单履约。\n业务目标：减少客服手工查询配送状态。\n本次范围：查看已支付订单、查看配送进度、查看物流入口。\n不做范围：商品推荐、发票生成、退款。\n\n请填写：\nEpic / 业务目标：\n- \n\n本次拆分范围：\n- \n\n已知不做的范围：\n- ",
					)) ?? "";
				ctx.ui.setWidget("story-map", ["Story Map：拆分用户故事地图，完成后会保存到 .pi/user-story/story-map.md"]);
			}
			const prompt = await buildPrompt(join(baseDir, "prompts", "story-map.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: model.trim() || "（暂无）",
				storyMap: storyMap.trim() || "（暂无）",
				notes: notes.trim() || "（无补充）",
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
