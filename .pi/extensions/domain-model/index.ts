import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { buildPrompt, readProjectFile, sendPrompt, type PromptCommandContext } from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n已有故事地图：\n$4\n\n已有模型：\n$3\n\n补充：\n$5\n\n请生成领域模型，并调用 user_story_artifact 保存 artifactType=model。`;

export default function domainModelExtension(pi: ExtensionAPI) {
	pi.registerCommand("domain-model", {
		description: "根据概念字典和故事地图生成/更新领域模型 domain-model.md",
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
						"补充材料 / 建模偏好（可留空）",
						notes ||
							"字段说明：可填写建模方法偏好、补充故事、业务规则、特别关注的关系或不变量。\n\n示例：\n建模偏好：普通领域模型 + Mermaid classDiagram。\n补充规则：订单在支付成功后进入“待确认”，客服确认后进入“待发货”。\n关注点：退款后订单、支付、配送进度之间的关系。\n\n请填写：\n建模方法偏好（如四色法/事件风暴/普通领域模型）：\n- \n\n补充故事或规则：\n- ",
					)) ?? "";
				ctx.ui.setWidget("domain-model", ["Domain Model：生成领域模型，完成后会保存到 .pi/user-story/domain-model.md"]);
			}
			const prompt = await buildPrompt(join(baseDir, "prompts", "model.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: model.trim() || "（暂无）",
				storyMap: storyMap.trim() || "（暂无）",
				notes: notes.trim() || "（无补充）",
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
