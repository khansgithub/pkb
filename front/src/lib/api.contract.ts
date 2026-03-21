import { z } from 'zod';
import { SnippetSchema } from './types';

// =======================
// Schemas
// =======================
const QueryRequestSchema = z.object({
    q: z.string()
});

const QueryResponseSchema = z.object({
    snippets: z.array(SnippetSchema)
});

const ErrorResponseSchema = z.object({
    error: z.object({
        message: z.string(),
        name: z.string(),
        stack: z.string().optional(),
    })
});

export const QueryEndpointResponseSchema = z.union([QueryResponseSchema, ErrorResponseSchema]);

// =======================
// Types
// =======================
export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type QueryResponse = z.infer<typeof QueryResponseSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type QueryEndpointResponse = z.infer<typeof QueryEndpointResponseSchema>;

export function isQueryResponse(r: QueryEndpointResponse): r is QueryResponse {
    return 'snippets' in r;
}

export function isErrorResponse(r: QueryEndpointResponse): r is ErrorResponse {
    return 'error' in r;
}

// =======================
// Endpoint metadata
// =======================
export const ENDPOINTS_META = {
    query: {
        description: 'FTS query endpoint (search and return snippets).',
        request: QueryRequestSchema,
        response: QueryResponseSchema,
        error: ErrorResponseSchema,
    },
    sync: {
        description: 'Rebuild/reindex snippets database from gist.',
        request: z.void(),
        response: z.boolean(),
        error: ErrorResponseSchema,
    },
} as const;
