import { z } from "zod";

export const BlockTypeEnum = z.enum(["code", "text"]);

export const SnippetTableSchema = z.object({
    id: z.number().int().optional(),
    title: z.string().default(''),
    tags: z.array(z.string()),
    description: z.string().default(''),
});

export const BlockSchema = z.object({
    id: z.number().int().optional(),
    type: BlockTypeEnum,
    lang: z.string().nullable().optional(),
    lines: z.array(z.string()),
    snippet_id: z.number().int(),
    pos: z.number().int(),
});

export const SnippetSchema = z.object({
    id: z.optional(z.number()),
    title: z.string(),
    tags: z.array(z.string()),
    description: z.string().nullable().optional(),
    snippets: z.array(BlockSchema)
});

export type BlockType = z.infer<typeof BlockTypeEnum>;
export type SnippetTable = z.infer<typeof SnippetTableSchema>;
export type Block = z.infer<typeof BlockSchema>;
export type Snippet = z.infer<typeof SnippetSchema>;

/** Legacy API / SQL returned markdown chunks as strings; map each to a text block. */
export function legacyStringsToBlocks(snippetId: number, parts: string[]): Block[] {
	return parts.map((s, pos) => ({
		type: "text" as const,
		lang: null,
		lines: s.length > 0 ? s.split("\n") : [],
		snippet_id: snippetId,
		pos,
	}));
}

