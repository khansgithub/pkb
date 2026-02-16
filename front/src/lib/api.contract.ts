import { z } from 'zod';

// ==================================================
// Query endpoint
// ==================================================

export const QueryRequestSchema = z.object({
    q: z.string(),
});

export const QueryResponseSchema = z.object({
    query: z.string(), // PK
    snippet_ids: z.array(z.number()),
});

export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type Query = z.infer<typeof QueryResponseSchema>;

// ==================================================
// Endpoint metadata (for documentation)
// ==================================================

export const ENDPOINTS_META = {
    query: {
        description:
            'A (partial?) search query sent to the database, for it to perform a FTS with, and return results.',
        request: QueryRequestSchema,
        response: QueryResponseSchema,
    },
    sync: {
        description:
            'Invokes the backend to recreate the snippets database, including reparsing the gist, and reindexing the database(?)',
        request: z.void(),
        response: z.boolean(),
    },
} as const;
