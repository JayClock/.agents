import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
	buildPrompt,
	ensureUserStoryArtifactTemplates,
	readProjectFile,
	sendPrompt,
	type PromptCommandContext,
} from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n已有概念字典：\n$2\n\n已有领域模型：\n$3\n\n已有故事地图：\n$4\n\n补充素材：\n$5\n\n请把业务知识分别更新到 glossary、domain-model、story-map，并调用 user_story_artifact 保存三份产物。`;

export default function storyContextExtension(pi: ExtensionAPI) {
	pi.registerCommand("story-context", {
		description: "从 Epic/访谈/零散材料更新 glossary、domain-model、story-map 三份业务知识产物",
		handler: async (args, ctx: PromptCommandContext) => {
			let notes = args?.trim() || "";
			if (ctx.hasUI) {
				notes =
					(await ctx.ui.editor(
						"业务素材 / Epic / 访谈记录",
						notes ||
							"字段说明：请粘贴 Epic、访谈记录、流程、规则、痛点、范围边界；不确定的地方也可以写。\n\n示例：\n业务目标：降低客服手工确认订单状态的次数。\n用户角色：下单客户、客服人员。\n当前流程：客户付款后等待客服人工确认。\n规则：只有支付成功且库存锁定后，订单才算完成。\n困惑：退款后的订单状态是否保留历史记录。\n\n请填写：\n用户角色与目标：\n- \n\n业务目标 / Epic：\n- \n\n已有流程、规则、约束：\n- \n\n当前困惑：\n- ",
					)) ?? "";
				if (!notes.trim()) {
					ctx.ui.notify("已取消：未填写业务素材", "warning");
					return;
				}
				ctx.ui.setWidget("story-context", [
					"Story Context：会更新 glossary.md、domain-model.md、story-map.md；后续流程不读取 context.md。",
				]);
			}
			const initialized = await ensureUserStoryArtifactTemplates(ctx.cwd);
			if (initialized.length > 0 && ctx.hasUI) {
				ctx.ui.notify(`已基于模板初始化：${initialized.join("、")}`, "info");
			}
			const [glossary, model, storyMap] = await Promise.all([
				readProjectFile(ctx.cwd, ".pi/user-story/glossary.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/domain-model.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/story-map.md"),
			]);
			const prompt = await buildPrompt(join(baseDir, "prompts", "context.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: model.trim() || "（暂无）",
				storyMap: storyMap.trim() || "（暂无）",
				notes,
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
