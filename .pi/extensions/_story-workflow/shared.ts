import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { withFileMutationQueue, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

const sharedDir = dirname(fileURLToPath(import.meta.url));
const extensionsDir = resolve(sharedDir, "..");
const userStoryTemplateDir = resolve(sharedDir, "templates", "user-story");

export interface PromptCommandContext {
	cwd: string;
	hasUI: boolean;
	isIdle(): boolean;
	ui: {
		editor(title: string, initial?: string): Promise<string | undefined>;
		notify(message: string, level: "info" | "warning" | "error"): void;
		setWidget(id: string, content: string[] | undefined, options?: { placement?: "aboveEditor" | "belowEditor" }): void;
	};
}

const FALLBACK_USER_STORY_METHOD = `
用户故事方法要点：
- 用户故事优先定义问题，而不是预设技术解决方案。
- 标准卡片格式：作为 <角色>，我希望 <功能/能力>，从而 <价值>。
- 角色-价值定义问题，功能/能力是可协商的解决方案切入点。
- 好的价值陈述通常来自用户目标、整体解决方案规则/流程、用户旅程下一步。
- 验收条件属于 Confirmation，应在掌握整体解决方案与用户旅程后，用 Given/When/Then 编写。
`.trim();

export async function readTextFile(path: string, fallback = ""): Promise<string> {
	try {
		return await readFile(path, "utf8");
	} catch {
		return fallback;
	}
}

export function stripPromptFrontmatter(template: string): string {
	if (!template.startsWith("---\n")) return template;
	const end = template.indexOf("\n---\n", 4);
	return end === -1 ? template : template.slice(end + "\n---\n".length);
}

export function renderPromptTemplate(template: string, args: string[]): string {
	return stripPromptFrontmatter(template)
		.replace(/\$\{@:(\d+):(\d+)\}/g, (_match, start, length) =>
			args.slice(Number(start) - 1, Number(start) - 1 + Number(length)).join(" "),
		)
		.replace(/\$\{@:(\d+)\}/g, (_match, start) => args.slice(Number(start) - 1).join(" "))
		.replace(/\$ARGUMENTS|\$@/g, args.join(" "))
		.replace(/\$(\d+)/g, (_match, index) => args[Number(index) - 1] ?? "");
}

export async function readUserStoryMethod(): Promise<string> {
	return stripPromptFrontmatter(
		await readTextFile(resolve(extensionsDir, "user-story", "prompts", "method.md"), FALLBACK_USER_STORY_METHOD),
	).trim();
}

export async function readProjectFile(cwd: string, path: string): Promise<string> {
	return readTextFile(resolve(cwd, path), "");
}

const USER_STORY_ARTIFACT_TEMPLATES = [
	{
		path: ".pi/user-story/glossary.md",
		template: "glossary.md",
		fallback: `# 用户故事概念字典

> 维护角色、稳定目标、业务术语、关键规则和范围边界。可用 \`/story-context\` 或 \`/story-glossary\` 更新。

## 用户角色与目标
- <角色>：<稳定业务目标>

## 业务术语
| 概念 | 定义 | 关键属性 / 状态 | 关系 / 边界 |
|---|---|---|---|
| <概念> | <一句话定义> | <属性或状态> | <相关概念、同义词、边界> |

## 业务规则
- <规则>：<跨故事复用的约束或判断条件>

## 范围边界
- <已纳入范围>
- <不纳入范围 / 已有独立故事>
`,
	},
	{
		path: ".pi/user-story/domain-model.md",
		template: "domain-model.md",
		fallback: `# 用户故事领域模型

> 维护领域对象、关系、生命周期和业务不变量。可用 \`/story-context\` 或 \`/domain-model\` 更新。

## 模型说明
- <领域模型覆盖的业务范围和关键假设>

## Mermaid 模型

\`\`\`mermaid
classDiagram
  class Concept
\`\`\`

## 关键关系
- <概念 A> 与 <概念 B>：<关系说明>

## 业务不变量
- <不变量 / 约束>

## 待验证点
- <需要通过验收场景验证的概念、关系或规则>
`,
	},
	{
		path: ".pi/user-story/story-map.md",
		template: "story-map.md",
		fallback: `# 用户故事地图

> 维护用户旅程、故事拆分、故事边界和依赖。可用 \`/story-context\` 或 \`/story-map\` 更新。

## 范围 / 业务目标
- <本次故事地图覆盖的业务目标或 Epic>

## 用户旅程
### <角色>
1. <阶段一>
2. <阶段二>
3. <阶段三>

## 故事拆分
### <旅程阶段>
- [Epic] 作为 <角色>，我希望 <能力>，从而 <价值>
- [Journey step] 作为 <角色>，我希望 <能力>，从而 <价值>
- [Thin slice] 作为 <角色>，我希望 <能力>，从而 <价值>

## 故事边界与依赖
- <故事 A>：<边界 / 依赖 / 是否可独立验收>

## 推荐下一张 TQA 故事
- 作为 <角色>，我希望 <能力>，从而 <价值>
`,
	},
] as const;

async function hasNonEmptyFile(path: string): Promise<boolean> {
	try {
		return (await readFile(path, "utf8")).trim().length > 0;
	} catch {
		return false;
	}
}

export async function ensureUserStoryArtifactTemplates(cwd: string): Promise<string[]> {
	const initialized: string[] = [];
	for (const item of USER_STORY_ARTIFACT_TEMPLATES) {
		const targetPath = resolve(cwd, item.path);
		if (await hasNonEmptyFile(targetPath)) continue;

		const template = await readTextFile(resolve(userStoryTemplateDir, item.template), item.fallback);
		await withFileMutationQueue(targetPath, async () => {
			if (await hasNonEmptyFile(targetPath)) return;
			await mkdir(dirname(targetPath), { recursive: true });
			await writeFile(targetPath, template.trimEnd() + "\n", "utf8");
			initialized.push(item.path);
		});
	}
	return initialized;
}

export async function readKnowledgeContext(cwd: string): Promise<string> {
	const [glossary, model, storyMap] = await Promise.all([
		readProjectFile(cwd, ".pi/user-story/glossary.md"),
		readProjectFile(cwd, ".pi/user-story/domain-model.md"),
		readProjectFile(cwd, ".pi/user-story/story-map.md"),
	]);
	return [
		"# 概念字典\n\n" + (glossary.trim() || "（暂无）"),
		"# 领域模型\n\n" + (model.trim() || "（暂无）"),
		"# 故事地图\n\n" + (storyMap.trim() || "（暂无）"),
	].join("\n\n---\n\n");
}

export async function readLatestStorySession(cwd: string): Promise<string> {
	try {
		const dir = resolve(cwd, ".pi", "user-story", "sessions");
		const files = (await readdir(dir)).filter((name) => name.endsWith(".story.md")).sort().reverse();
		if (files.length === 0) return "";
		const latestPath = join(dir, files[0]);
		return `来源：${latestPath}\n\n${await readTextFile(latestPath, "")}`;
	} catch {
		return "";
	}
}

export async function buildPrompt(templatePath: string, fallbackTemplate: string, values: Record<string, string>): Promise<string> {
	const method = await readUserStoryMethod();
	const template = await readTextFile(templatePath, fallbackTemplate);
	const source = template.trim() || fallbackTemplate;
	const scenarioOrNotes = values.scenario ?? values.notes ?? "";
	return renderPromptTemplate(source, [
		method,
		values.glossary ?? "",
		values.model ?? "",
		values.storyMap ?? "",
		scenarioOrNotes,
	]);
}

export async function sendPrompt(pi: ExtensionAPI, ctx: { isIdle(): boolean }, prompt: string) {
	if (ctx.isIdle()) {
		pi.sendUserMessage(prompt);
	} else {
		pi.sendUserMessage(prompt, { deliverAs: "followUp" });
	}
}
