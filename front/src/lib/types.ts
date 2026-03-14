import { z } from "zod";

export const SnippetSchema = z.object({
    id: z.optional(z.number()),
    title: z.string(),
    tags: z.array(z.string()),
    description: z.string().nullable().optional(),
    snippets: z.array(z.string())
});

export type Snippet = z.infer<typeof SnippetSchema>;