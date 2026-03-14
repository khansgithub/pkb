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
}
);
const dbErrorResponse = (error: Error) => new Response(
    JSON.stringify({
        error: {
            message: error.message,
            name: error.name,
            stack: error.stack
        }
    } as ErrorResponse), {
    status: 500,
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
    console.log(res, "res");
    if (!res.ok) return dbErrorResponse(res.error);

    return successResponse(res.snippets);
};