import type { ErrorResponse, QueryResponse } from '$lib/api.contract';
import { runQuery } from '$lib/server/sql/client';
import type { Snippet } from '$lib/types';
import type { RequestHandler } from './$types';

const headers = { 'Content-Type': 'application/json' };
const noQueryResponse = () => new Response(
    JSON.stringify({
        error: {
            message: 'No query provided',
            name: 'NoQueryProvided',
            stack: 'NoQueryProvided'
        }
    } as ErrorResponse), {
    status: 400,
    headers: headers
});

const successResponse = (snippets: Snippet[]) => new Response(
    JSON.stringify({
        snippets: snippets
    } as QueryResponse), {
    status: 200,
    headers: headers
});

export const GET: RequestHandler = async ({ request }) => {
    const { searchParams } = new URL(request.url);
    
    const query = searchParams.get('q');
    if (!query) return noQueryResponse();
    
    const res = await runQuery(query);
    if ('error' in res) {
        return new Response(JSON.stringify(res), {
            status: 500,
            headers
        });
    }
    return successResponse(res.snippets);
};

// export const prerender = true;