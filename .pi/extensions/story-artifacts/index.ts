import { mkdir, writeFile } from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { withFileMutationQueue } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Text } from "@earendil-works/pi-tui";
import { Type } from "typebox";

const ARTIFACT_TYPES = ["glossary", "model", "story_map", "model_check", "other"] as const;

type ArtifactType = (typeof ARTIFACT_TYPES)[number];

interface ArtifactDetails {
	artifactType: ArtifactType;
	title: string;
	path: string;
}

const ArtifactParams = Type.Object({
	artifactType: StringEnum(ARTIFACT_TYPES, {
		description: "Artifact type. Do not use context; this workflow does not maintain .pi/user-story/context.md.",
	}),
	title: Type.String({ description: "Artifact title." }),
	content: Type.String({ description: "Markdown content to save." }),
	path: Type.Optional(
		Type.String({ description: "Optional path under .pi/user-story/. If omitted, a canonical/default path is used." }),
	),
});

function normalizeArtifactType(value: unknown): ArtifactType {
	return ARTIFACT_TYPES.includes(value as ArtifactType) ? (value as ArtifactType) : "other";
}

function safeSlug(text: string): string {
	const normalized = text
		.replace(/<[^>]+>/g, "")
		.replace(/[\s\n\r\t]+/g, "-")
		.replace(/[\\/:*?\"<>|]+/g, "-")
		.replace(/-+/g, "-")
		.replace(/^-|-$/g, "")
		.slice(0, 48);
	return normalized || "artifact";
}

function timestampForFile(date = new Date()): string {
	return date.toISOString().replace(/[:.]/g, "-");
}

function defaultArtifactPath(cwd: string, artifactType: ArtifactType, title: string): string {
	switch (artifactType) {
		case "glossary":
			return resolve(cwd, ".pi", "user-story", "glossary.md");
		case "model":
			return resolve(cwd, ".pi", "user-story", "domain-model.md");
		case "story_map":
			return resolve(cwd, ".pi", "user-story", "story-map.md");
		case "model_check":
			return resolve(cwd, ".pi", "user-story", "model-checks", `${timestampForFile()}-${safeSlug(title)}.model-check.md`);
		default:
			return resolve(cwd, ".pi", "user-story", "artifacts", `${timestampForFile()}-${safeSlug(title)}.md`);
	}
}

function resolveArtifactPath(cwd: string, artifactType: ArtifactType, title: string, path?: string): string {
	const userStoryRoot = resolve(cwd, ".pi", "user-story");
	const cleanedPath = path?.trim().replace(/^@+/, "");
	const filePath = cleanedPath ? resolve(cwd, cleanedPath) : defaultArtifactPath(cwd, artifactType, title);
	const rel = relative(userStoryRoot, filePath);
	if (!rel || rel.startsWith("..")) {
		throw new Error("Artifact path must be under .pi/user-story/.");
	}
	return filePath;
}

function artifactMarkdown(title: string, content: string): string {
	const trimmed = content.trim();
	if (trimmed.startsWith("#")) return `${trimmed}\n`;
	return `# ${title.trim() || "用户故事工件"}\n\n${trimmed}\n`;
}

export default function storyArtifactsExtension(pi: ExtensionAPI) {
	pi.registerTool({
		name: "user_story_artifact",
		label: "User Story Artifact",
		description:
			"Save business-analysis artifacts for the user-story workflow, such as glossary, domain model, story map, and model-check reports.",
		promptSnippet: "Save user-story workflow artifacts as markdown under .pi/user-story/",
		promptGuidelines: [
			"Use user_story_artifact to save outputs from story-context, story-glossary, domain-model, story-map, and model-check workflows.",
			"When using user_story_artifact, keep paths under .pi/user-story/ and prefer the default path unless the user requested another path.",
		],
		parameters: ArtifactParams,
		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			const artifactType = normalizeArtifactType(params.artifactType);
			const filePath = resolveArtifactPath(ctx.cwd, artifactType, params.title, params.path);
			const markdown = artifactMarkdown(params.title, params.content);
			await withFileMutationQueue(filePath, async () => {
				await mkdir(dirname(filePath), { recursive: true });
				await writeFile(filePath, markdown, "utf8");
			});
			const details: ArtifactDetails = { artifactType, title: params.title, path: filePath };
			return {
				content: [{ type: "text" as const, text: `Saved ${artifactType} artifact to ${filePath}` }],
				details,
			};
		},
		renderCall(args, theme) {
			const artifactType = typeof args.artifactType === "string" ? args.artifactType : "artifact";
			const title = typeof args.title === "string" ? args.title : "";
			return new Text(
				theme.fg("toolTitle", theme.bold("user_story_artifact ")) +
					theme.fg("muted", `[${artifactType}] `) +
					theme.fg("text", title),
				0,
				0,
			);
		},
		renderResult(result, _options, theme) {
			const details = result.details as ArtifactDetails | undefined;
			if (!details) {
				const item = result.content[0];
				return new Text(item?.type === "text" ? item.text : "", 0, 0);
			}
			return new Text(theme.fg("success", "✓ saved ") + theme.fg("dim", details.path), 0, 0);
		},
	});
}
