import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
	buildPrompt,
	readFmModelSnapshot,
	readLatestStorySession,
	readProjectFile,
	sendPrompt,
	type PromptCommandContext,
} from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const FALLBACK_TEMPLATE = `$1\n\n概念字典：\n$2\n\n故事地图：\n$4\n\n领域模型：\n$3\n\n用户故事/验收场景：\n$5\n\n请展开模型并检查问题，调用 user_story_artifact 保存 artifactType=model_check。`;

export default function modelCheckExtension(pi: ExtensionAPI) {
	pi.registerCommand("model-check", {
		description: "用用户故事验收条件展开 FM/领域模型并生成检查报告",
		handler: async (args, ctx: PromptCommandContext) => {
			const [glossary, model, storyMap, latestStory, fmModel] = await Promise.all([
				readProjectFile(ctx.cwd, ".pi/user-story/glossary.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/domain-model.md"),
				readProjectFile(ctx.cwd, ".pi/user-story/story-map.md"),
				readLatestStorySession(ctx.cwd),
				readFmModelSnapshot(ctx.cwd),
			]);
			let scenario = args?.trim() || latestStory;
			if (ctx.hasUI) {
				scenario =
					(await ctx.ui.editor(
						"用户故事 / Given-When-Then 验收场景",
						scenario ||
							"字段说明：填写一张用户故事和一个或多个 Given/When/Then 场景；用于展开领域模型并检查缺失概念、关系和规则。\n\n示例：\n用户故事：作为下单客户，我希望查看已支付订单的配送进度，从而安排收货或售后计划。\n\nScenario: 显示配送中的订单进度\nGiven 客户已登录且存在一笔已支付订单，订单包含 4 个配送节点，已完成 2 个\nWhen 客户查看订单中心\nThen 系统应呈现该订单配送进度为 2/4，状态为配送中\n\n请填写：\n用户故事：\n作为 <角色>\n我希望 <能力>\n从而 <价值>\n\n验收场景：\nGiven \nWhen \nThen ",
					)) ?? "";
				if (!scenario.trim()) {
					ctx.ui.notify("已取消：未填写用户故事或验收场景", "warning");
					return;
				}
				ctx.ui.setWidget("model-check", ["Model Check：展开验收场景检查模型，报告会保存到 .pi/user-story/model-checks/"]);
			}
			const modelContext = [
				"# 领域模型派生视图",
				model.trim() || "（暂无）",
				"# FM YAML 源模型快照",
				fmModel.trim() || "（暂无）",
			].join("\n\n");
			const prompt = await buildPrompt(join(baseDir, "prompts", "model-check.md"), FALLBACK_TEMPLATE, {
				glossary: glossary.trim() || "（暂无）",
				model: modelContext,
				storyMap: storyMap.trim() || "（暂无）",
				scenario: scenario.trim(),
			});
			await sendPrompt(pi, ctx, prompt);
		},
	});
}
