/**
 * User Story TQA extension for pi
 *
 * Helps write user stories by asking clarification questions first,
 * then producing Given/When/Then acceptance criteria.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
	DEFAULT_MAX_BYTES,
	DEFAULT_MAX_LINES,
	formatSize,
	type ExtensionAPI,
	type TruncationResult,
	truncateHead,
	withFileMutationQueue,
} from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Text } from "@earendil-works/pi-tui";
import { Type } from "typebox";
import { readFmModelSnapshot } from "../_story-workflow/shared";

const baseDir = dirname(fileURLToPath(import.meta.url));

const QUESTION_CATEGORIES = [
	"business_context",
	"user_story",
	"journey",
	"solution_rule",
	"scope",
	"interaction_detail",
	"other",
] as const;

const ANSWER_KINDS = ["free_text", "yes_no", "choice"] as const;

type QuestionCategory = (typeof QUESTION_CATEGORIES)[number];

type AnswerKind = (typeof ANSWER_KINDS)[number];

interface AskDetails {
	question: string;
	answer: string | null;
	category: QuestionCategory;
	why?: string;
	recommendation: string;
}

interface ScenarioDetails {
	story: string;
	revisedStory?: string;
	scenarios: Array<{
		name: string;
		given: string;
		when: string;
		then: string;
		notes?: string;
	}>;
	contextUpdates: string[];
	storyUpdates: string[];
	openQuestions: string[];
	rationale?: string;
	tqaHistory?: AskDetails[];
	contextSnapshot?: string;
	savedPath?: string;
	truncation?: TruncationResult;
}

const FALLBACK_USER_STORY_METHOD = `
用户故事方法要点：
- 用户故事优先定义问题，而不是预设技术解决方案；LLM 更擅长基于清晰问题寻找解决方案。
- 标准卡片格式：作为 <角色>，我希望 <功能/能力>，从而 <价值>。
- 角色-价值定义要解决的问题，通常更稳定；功能/能力是可协商的解决方案切入点。
- 要追问真正受益者与真正价值；价值不应只是复述功能。
- 好的价值陈述通常来自三类来源：满足某个用户角色的目标、满足整体解决方案的规则/流程、推进用户旅程的下一步。
- 验收条件属于 Confirmation，应在掌握整体解决方案、FM 履约责任链与用户旅程后，用 Given/When/Then 编写。
- TQA（Thought-Question-Answer）模式：LLM 先思考不清楚之处，再向领域专家提问；人回答后继续；足够清楚时输出验收场景。
- 对 LLM 问题的三类处理：若问题暴露基础概念/流程/FM 模型误解，修改 fm-model/glossary/domain-model/story-map；若问题暴露操作误解，修改用户故事；若只是交互细节，直接记录为问答历史。
`.trim();

const FALLBACK_STORY_INPUT_TEMPLATE = `请帮我用 TQA 编写用户故事验收条件。

业务知识上下文（可留空，默认读取 .pi/user-story/glossary.md、domain-model.md、story-map.md）：
- 概念字典 / 关键规则：
- 领域模型 / 关键关系：
- 故事地图 / 当前故事所在用户旅程位置：

用户故事：
作为 <角色>
我希望 <能力/功能>
从而 <业务价值>

相关用户故事 / 已知边界：
- `;

const AskQuestionParams = Type.Object({
	question: Type.String({ description: "Ask exactly one concise clarification question for the domain expert." }),
	why: Type.Optional(Type.String({ description: "Why this question matters for story scope or acceptance criteria." })),
	category: StringEnum(QUESTION_CATEGORIES, {
		description:
			"Question category. Use business_context for missing business knowledge in glossary/domain-model/story-map.",
	}),
	answerKind: Type.Optional(StringEnum(ANSWER_KINDS, { description: "Defaults to free_text." })),
	options: Type.Optional(Type.Array(Type.String(), { description: "Options when answerKind is choice." })),
});

const ScenarioParams = Type.Object({
	story: Type.String({ description: "The final user story in As/I want/So that form, Chinese is OK." }),
	revisedStory: Type.Optional(Type.String({ description: "A revised story if clarification changed role, capability, or value." })),
	scenarios: Type.Array(
		Type.Object({
			name: Type.String({ description: "Scenario title." }),
			given: Type.String({ description: "Given: concrete precondition/system state." }),
			when: Type.String({ description: "When: user action or domain event." }),
			then: Type.String({ description: "Then: expected business outcome." }),
			notes: Type.Optional(Type.String({ description: "Optional scope note, business rule, or example data." })),
		}),
		{ description: "Acceptance criteria scenarios in Given/When/Then style." },
	),
	contextUpdates: Type.Optional(
		Type.Array(Type.String(), { description: "Business-knowledge changes suggested for glossary/domain-model/story-map." }),
	),
	storyUpdates: Type.Optional(
		Type.Array(Type.String(), { description: "User-story wording or scope changes suggested by the TQA conversation." }),
	),
	openQuestions: Type.Optional(Type.Array(Type.String(), { description: "Questions still unresolved." })),
	rationale: Type.Optional(Type.String({ description: "Short explanation of how the scenarios map to user goal, solution, and journey." })),
});

function normalizeCategory(value: unknown): QuestionCategory {
	return QUESTION_CATEGORIES.includes(value as QuestionCategory) ? (value as QuestionCategory) : "other";
}

function normalizeAnswerKind(value: unknown): AnswerKind {
	return ANSWER_KINDS.includes(value as AnswerKind) ? (value as AnswerKind) : "free_text";
}

function recommendationFor(category: QuestionCategory): string {
	switch (category) {
		case "business_context":
		case "solution_rule":
		case "journey":
			return "如果这个问题暴露了基础概念、规则、流程或用户旅程误解，请优先修改 glossary/domain-model/story-map。";
		case "user_story":
		case "scope":
			return "如果这个问题暴露了角色、能力、价值或范围误解，请优先修改用户故事。";
		case "interaction_detail":
			return "如果只是交互或示例细节，请将答案记录进 TQA 历史，用于生成验收条件。";
		default:
			return "根据答案判断它应更新 glossary/domain-model/story-map、用户故事，还是仅作为验收条件细节。";
	}
}

async function readTextFile(path: string, fallback: string): Promise<string> {
	try {
		return await readFile(path, "utf8");
	} catch {
		return fallback;
	}
}

function stripPromptFrontmatter(template: string): string {
	if (!template.startsWith("---\n")) return template;
	const end = template.indexOf("\n---\n", 4);
	return end === -1 ? template : template.slice(end + "\n---\n".length);
}

function renderPromptTemplate(template: string, args: string[]): string {
	return stripPromptFrontmatter(template)
		.replace(/\$\{@:(\d+):(\d+)\}/g, (_match, start, length) =>
			args.slice(Number(start) - 1, Number(start) - 1 + Number(length)).join(" "),
		)
		.replace(/\$\{@:(\d+)\}/g, (_match, start) => args.slice(Number(start) - 1).join(" "))
		.replace(/\$ARGUMENTS|\$@/g, args.join(" "))
		.replace(/\$(\d+)/g, (_match, index) => args[Number(index) - 1] ?? "");
}

async function readUserStoryMethod(): Promise<string> {
	return stripPromptFrontmatter(await readTextFile(join(baseDir, "prompts", "method.md"), FALLBACK_USER_STORY_METHOD)).trim();
}

async function readStoryInputTemplate(): Promise<string> {
	return readTextFile(join(baseDir, "templates", "story-input.md"), FALLBACK_STORY_INPUT_TEMPLATE);
}

async function readProjectFile(cwd: string, path: string): Promise<string> {
	return readTextFile(resolve(cwd, path), "");
}

async function readKnowledgeContext(cwd: string): Promise<string> {
	const [fmModel, glossary, model, storyMap] = await Promise.all([
		readFmModelSnapshot(cwd),
		readProjectFile(cwd, ".pi/user-story/glossary.md"),
		readProjectFile(cwd, ".pi/user-story/domain-model.md"),
		readProjectFile(cwd, ".pi/user-story/story-map.md"),
	]);
	return [
		"# FM YAML 源模型\n\n" + (fmModel.trim() || "（暂无）"),
		"# 概念字典\n\n" + (glossary.trim() || "（暂无）"),
		"# 领域模型\n\n" + (model.trim() || "（暂无）"),
		"# 故事地图\n\n" + (storyMap.trim() || "（暂无）"),
	].join("\n\n---\n\n");
}

function safeSlug(text: string): string {
	const normalized = text
		.replace(/<[^>]+>/g, "")
		.replace(/[\s\n\r\t]+/g, "-")
		.replace(/[\\/:*?\"<>|]+/g, "-")
		.replace(/-+/g, "-")
		.replace(/^-|-$/g, "")
		.slice(0, 48);
	return normalized || "user-story";
}

function timestampForFile(date = new Date()): string {
	return date.toISOString().replace(/[:.]/g, "-");
}

function scenarioMarkdown(details: ScenarioDetails, tqaHistory: AskDetails[] = [], contextSnapshot?: string): string {
	const lines: string[] = [];
	lines.push("# 用户故事验收场景");
	if (contextSnapshot?.trim()) {
		lines.push("");
		lines.push("## 业务知识快照（glossary / domain-model / story-map）");
		lines.push(contextSnapshot.trim());
	}
	if (tqaHistory.length > 0) {
		lines.push("");
		lines.push("## TQA 问答记录");
		for (const [index, item] of tqaHistory.entries()) {
			lines.push("");
			lines.push(`### Q${index + 1}: ${item.question}`);
			if (item.why) lines.push(`- 为什么问：${item.why}`);
			lines.push(`- 分类：${item.category}`);
			lines.push(`- 回答：${item.answer ?? "（未回答）"}`);
			lines.push(`- 处理建议：${item.recommendation}`);
		}
	}
	lines.push("");
	lines.push("## 用户故事");
	lines.push(details.story);
	if (details.revisedStory && details.revisedStory.trim() && details.revisedStory.trim() !== details.story.trim()) {
		lines.push("");
		lines.push("## 建议修订");
		lines.push(details.revisedStory);
	}
	lines.push("");
	lines.push("## 验收条件");
	for (const [index, scenario] of details.scenarios.entries()) {
		lines.push("");
		lines.push(`### Scenario ${index + 1}: ${scenario.name}`);
		lines.push(`Given ${scenario.given}`);
		lines.push(`When ${scenario.when}`);
		lines.push(`Then ${scenario.then}`);
		if (scenario.notes) lines.push(`> ${scenario.notes}`);
	}
	if (details.contextUpdates.length > 0) {
		lines.push("");
		lines.push("## 建议补充到业务知识产物");
		for (const item of details.contextUpdates) lines.push(`- ${item}`);
	}
	if (details.storyUpdates.length > 0) {
		lines.push("");
		lines.push("## 建议调整用户故事");
		for (const item of details.storyUpdates) lines.push(`- ${item}`);
	}
	if (details.openQuestions.length > 0) {
		lines.push("");
		lines.push("## 未决问题");
		for (const item of details.openQuestions) lines.push(`- ${item}`);
	}
	if (details.rationale) {
		lines.push("");
		lines.push("## 推导说明");
		lines.push(details.rationale);
	}
	return lines.join("\n");
}

async function saveScenarioMarkdown(cwd: string, details: ScenarioDetails, tqaHistory: AskDetails[], contextSnapshot: string): Promise<string> {
	const markdown = scenarioMarkdown(details, tqaHistory, contextSnapshot);
	const fileName = `${timestampForFile()}-${safeSlug(details.revisedStory || details.story)}.story.md`;
	const filePath = resolve(cwd, ".pi", "user-story", "sessions", fileName);
	await withFileMutationQueue(filePath, async () => {
		await mkdir(dirname(filePath), { recursive: true });
		await writeFile(filePath, markdown, "utf8");
	});
	return filePath;
}

function truncateToolOutput(markdown: string, savedPath?: string): { text: string; truncation?: TruncationResult } {
	const truncation = truncateHead(markdown, {
		maxLines: DEFAULT_MAX_LINES,
		maxBytes: DEFAULT_MAX_BYTES,
	});
	if (!truncation.truncated) return { text: markdown };

	const omittedLines = truncation.totalLines - truncation.outputLines;
	const omittedBytes = truncation.totalBytes - truncation.outputBytes;
	let text = truncation.content;
	text += `\n\n[Output truncated: showing ${truncation.outputLines} of ${truncation.totalLines} lines`;
	text += ` (${formatSize(truncation.outputBytes)} of ${formatSize(truncation.totalBytes)}).`;
	text += ` ${omittedLines} lines (${formatSize(omittedBytes)}) omitted.`;
	if (savedPath) text += ` Full output saved to: ${savedPath}.`;
	text += "]";
	return { text, truncation };
}

async function buildUserStoryPrompt(input: { context: string; story: string; relatedStories?: string; mode?: string }): Promise<string> {
	const mode = input.mode?.trim() || "标准 TQA：先提问澄清，再输出验收条件";
	const method = await readUserStoryMethod();
	const template = await readTextFile(join(baseDir, "prompts", "tqa.md"), "");
	const fallbackTemplate = `$1\n\n业务知识上下文（概念字典 / 领域模型 / 故事地图）：$3\n\n当前用户故事：$4\n\n相关用户故事：$5\n\n请使用 TQA 提问澄清，并最终输出 Given/When/Then 验收条件。`;
	return renderPromptTemplate(template.trim() || fallbackTemplate, [
		method,
		mode,
		input.context.trim() || "（未提供，请先通过 TQA 提问补齐概念字典、领域模型或故事地图。）",
		input.story.trim() || "（未提供，请先询问我要编写哪张用户故事卡。）",
		input.relatedStories?.trim() || "（未提供。）",
	]);
}

async function sendPrompt(pi: ExtensionAPI, ctx: { isIdle(): boolean }, prompt: string) {
	if (ctx.isIdle()) {
		pi.sendUserMessage(prompt);
	} else {
		pi.sendUserMessage(prompt, { deliverAs: "followUp" });
	}
}

export default function userStoryExtension(pi: ExtensionAPI) {
	let tqaHistory: AskDetails[] = [];
	let currentContextSnapshot = "";

	pi.on("session_start", (_event, ctx) => {
		if (!ctx.hasUI) return;
		ctx.ui.setStatus("user-story", "story:TQA");
	});

	pi.registerTool({
		name: "user_story_question",
		label: "User Story Question",
		description:
			"Ask the domain expert one clarification question while writing user stories with TQA. Use this instead of guessing missing business knowledge, journey, rules, scope, or interaction details.",
		promptSnippet: "Ask one TQA clarification question for user-story writing and wait for the domain expert's answer",
		promptGuidelines: [
			"Use user_story_question when writing user stories and a detail about glossary/domain-model/story-map, user journey, solution rules, scope, or interaction is unclear.",
			"Each user_story_question call must ask exactly one concise question and must not answer it on behalf of the user.",
			"Ask at least three user_story_question questions before finalizing user-story acceptance criteria unless the user explicitly requests a quick draft.",
		],
		parameters: AskQuestionParams,
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const category = normalizeCategory(params.category);
			const answerKind = normalizeAnswerKind(params.answerKind);
			const recommendation = recommendationFor(category);
			const title = params.why ? `${params.question}\n\n为什么问：${params.why}` : params.question;

			if (!ctx.hasUI) {
				const details = { question: params.question, answer: null, category, why: params.why, recommendation } satisfies AskDetails;
				tqaHistory.push(details);
				return {
					content: [
						{
							type: "text" as const,
							text: `需要领域专家回答：${params.question}\n${recommendation}\nUI 不可用，已停止本轮，等待用户提供答案后再继续。`,
						},
					],
					details,
					terminate: true,
				};
			}

			let answer: string | undefined;
			if (answerKind === "yes_no") {
				answer = await ctx.ui.select(title, ["是", "否", "不确定 / 需要讨论"]);
			} else if (answerKind === "choice" && Array.isArray(params.options) && params.options.length > 0) {
				answer = await ctx.ui.select(title, [...params.options, "其他 / 手动输入"]);
				if (answer === "其他 / 手动输入") {
					answer = await ctx.ui.editor("请输入答案", "");
				}
			} else {
				answer = await ctx.ui.editor(title, "");
			}

			const cleaned = answer?.trim() || null;
			const details = {
				question: params.question,
				answer: cleaned,
				category,
				why: params.why,
				recommendation,
			} satisfies AskDetails;
			tqaHistory.push(details);
			return {
				content: [
					{
						type: "text" as const,
						text: cleaned
							? `Question: ${params.question}\nAnswer: ${cleaned}\nGuidance: ${recommendation}`
							: `Question cancelled or left blank: ${params.question}\nGuidance: ${recommendation}\nStop and wait for the domain expert before continuing.`,
					},
				],
				details,
				...(cleaned ? {} : { terminate: true }),
			};
		},
		renderCall(args, theme) {
			const category = typeof args.category === "string" ? args.category : "other";
			const question = typeof args.question === "string" ? args.question : "";
			let text = theme.fg("toolTitle", theme.bold("user_story_question "));
			text += theme.fg("muted", `[${category}] `);
			text += theme.fg("text", question);
			if (typeof args.why === "string" && args.why.trim()) {
				text += `\n${theme.fg("dim", `  why: ${args.why}`)}`;
			}
			return new Text(text, 0, 0);
		},
		renderResult(result, _options, theme) {
			const details = result.details as AskDetails | undefined;
			if (!details) {
				const item = result.content[0];
				return new Text(item?.type === "text" ? item.text : "", 0, 0);
			}
			if (!details.answer) return new Text(theme.fg("warning", "未获得答案"), 0, 0);
			return new Text(theme.fg("success", "✓ answer ") + theme.fg("accent", details.answer), 0, 0);
		},
	});

	pi.registerTool({
		name: "user_story_scenarios",
		label: "User Story Scenarios",
		description:
			"Return the final user story and its acceptance criteria scenarios in Given/When/Then style. Use as the final action after TQA clarification.",
		promptSnippet: "Finalize a user story as Given/When/Then acceptance scenarios",
		promptGuidelines: [
			"Use user_story_scenarios as the final action after enough TQA clarification for user-story writing.",
			"user_story_scenarios scenarios must focus on business outcome and story scope, not UI implementation details unless those details were part of the business knowledge context.",
			"After calling user_story_scenarios, do not emit another assistant response in the same turn.",
		],
		parameters: ScenarioParams,
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const historySnapshot = [...tqaHistory];
			const details: ScenarioDetails = {
				story: params.story,
				revisedStory: params.revisedStory,
				scenarios: params.scenarios,
				contextUpdates: params.contextUpdates ?? [],
				storyUpdates: params.storyUpdates ?? [],
				openQuestions: params.openQuestions ?? [],
				rationale: params.rationale,
				tqaHistory: historySnapshot,
				contextSnapshot: currentContextSnapshot,
			};
			try {
				details.savedPath = await saveScenarioMarkdown(ctx.cwd, details, historySnapshot, currentContextSnapshot);
			} catch (error) {
				details.openQuestions.push(`保存故事文件失败：${error instanceof Error ? error.message : String(error)}`);
			}
			const markdown = scenarioMarkdown(details, historySnapshot, currentContextSnapshot);
			const output = truncateToolOutput(
				details.savedPath ? `${markdown}\n\n---\nSaved to: ${details.savedPath}` : markdown,
				details.savedPath,
			);
			if (output.truncation) details.truncation = output.truncation;
			tqaHistory = [];
			currentContextSnapshot = "";
			return {
				content: [
					{
						type: "text" as const,
						text: output.text,
					},
				],
				details,
				terminate: true,
			};
		},
		renderCall(args, theme) {
			const count = Array.isArray(args.scenarios) ? args.scenarios.length : 0;
			return new Text(
				theme.fg("toolTitle", theme.bold("user_story_scenarios ")) +
					theme.fg("muted", `${count} scenario${count === 1 ? "" : "s"}`),
				0,
				0,
			);
		},
		renderResult(result, { expanded }, theme) {
			const details = result.details as ScenarioDetails | undefined;
			if (!details) {
				const item = result.content[0];
				return new Text(item?.type === "text" ? item.text : "", 0, 0);
			}
			if (expanded) return new Text(scenarioMarkdown(details, details.tqaHistory ?? [], details.contextSnapshot), 0, 0);
			const lines = [
				theme.fg("success", "✓ 用户故事验收条件已生成"),
				...(details.truncation?.truncated ? [theme.fg("warning", "tool output truncated; open saved file for full text")] : []),
				...(details.savedPath ? [theme.fg("dim", `saved: ${details.savedPath}`)] : []),
				theme.fg("muted", details.story),
				...details.scenarios.map((scenario, index) =>
					theme.fg("dim", `${index + 1}. ${scenario.name}: Given ${scenario.given}; When ${scenario.when}; Then ${scenario.then}`),
				),
			];
			return new Text(lines.join("\n"), 0, 0);
		},
	});

	const startUserStoryWizard = async (
		args: string,
		ctx: {
			cwd: string;
			hasUI: boolean;
			isIdle(): boolean;
			ui: {
				editor(title: string, initial?: string): Promise<string | undefined>;
				notify(message: string, level: "info" | "warning" | "error"): void;
				setWidget(id: string, content: string[] | undefined, options?: { placement?: "aboveEditor" | "belowEditor" }): void;
			};
		},
	) => {
		if (!ctx.hasUI) {
			tqaHistory = [];
			currentContextSnapshot = await readKnowledgeContext(ctx.cwd);
			const prompt = await buildUserStoryPrompt({ context: currentContextSnapshot, story: args });
			await sendPrompt(pi, ctx, prompt);
			return;
		}

		const story = await ctx.ui.editor(
			"用户故事（As/作为、I want/我希望、So that/从而）",
			args?.trim() ||
				"字段说明：填写一张用户故事卡；价值应说明为什么重要，不要只复述功能。\n\n示例：\n作为下单客户\n我希望查看已支付订单的配送进度\n从而安排收货或售后计划\n\n请填写：\n作为 <角色>\n我希望 <能力/功能>\n从而 <业务价值>",
		);
		if (!story?.trim()) {
			ctx.ui.notify("已取消：未填写用户故事", "warning");
			return;
		}

		const projectContext = await readKnowledgeContext(ctx.cwd);
		const context = await ctx.ui.editor(
			"业务知识上下文（概念字典 / 领域模型 / 故事地图）",
			projectContext.trim() ||
				"字段说明：可留空；如当前故事有特殊概念、规则、领域关系或旅程位置，请补充。\n\n示例：\n概念字典 / 关键规则：只有已支付订单才展示配送进度；已取消订单不显示配送进度。\n领域模型 / 关键关系：客户拥有订单；订单关联商品；订单包含配送节点；物流记录记录已完成节点。\n故事地图 / 当前旅程位置：订单中心 → 查看已支付订单 → 查看物流。\n\n请填写：\n概念字典：\n- \n\n领域模型：\n- \n\n故事地图 / 当前旅程位置：\n- ",
		);
		if (context === undefined) {
			ctx.ui.notify("已取消：未填写业务知识上下文", "warning");
			return;
		}

		const relatedStories = await ctx.ui.editor(
			"相关用户故事 / 已知边界（可留空）",
			"字段说明：填写上下游故事、依赖、明确不做范围、异常规则或风险。\n\n示例：\n- 前置：客户已登录，订单已支付。\n- 相关：查看物流入口、查看商品详情。\n- 不做：商品推荐、发票生成、退款处理。\n\n请填写：\n- ",
		);
		if (relatedStories === undefined) {
			ctx.ui.notify("已取消", "warning");
			return;
		}

		tqaHistory = [];
		currentContextSnapshot = relatedStories.trim() ? `${context}\n\n## 相关用户故事 / 已知边界\n${relatedStories}` : context;
		const prompt = await buildUserStoryPrompt({ context, story, relatedStories });
		ctx.ui.setWidget("user-story", ["User Story TQA 已启动：LLM 会先提问澄清，再输出 Given/When/Then。"]);
		await sendPrompt(pi, ctx, prompt);
	};

	pi.registerCommand("user-story", {
		description: "用 TQA 向领域专家提问，并生成用户故事验收条件",
		handler: startUserStoryWizard,
	});

	pi.registerCommand("story", {
		description: "user-story 的简写：启动用户故事 TQA 编写向导",
		handler: startUserStoryWizard,
	});

	pi.registerCommand("story-template", {
		description: "把用户故事 TQA 输入模板粘贴到编辑器",
		handler: async (_args, ctx) => {
			if (!ctx.hasUI) return;
			ctx.ui.setEditorText(await readStoryInputTemplate());
		},
	});

	pi.registerCommand("story-method", {
		description: "显示用户故事编写方法摘要",
		handler: async (_args, ctx) => {
			if (ctx.hasUI) {
				ctx.ui.setWidget("user-story-method", (await readUserStoryMethod()).split("\n"), { placement: "belowEditor" });
				ctx.ui.notify("已显示用户故事方法摘要", "info");
			}
		},
	});
}
