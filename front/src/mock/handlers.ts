import { http, HttpResponse} from 'msw'
import { type Query } from '../db';
import type { Response as R } from '$lib/api';
import { BACKEND, ENDPOINTS } from '$lib/const';

let base = new URL(BACKEND);
let u = (endpoint: string): string => {
    let url = new URL(endpoint, base).toString();
    console.log("msw: Building url: ", url);
    return url;
};

http.options('*', () => {
    return new Response(null, {
        status: 200,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE',
            'Access-Control-Allow-Headers': '*',
        },
    })
});

// i really don't understand how the parameters of `post` work...
export const handlers = [
    http.get(u("/*"), () => {
        console.log("INTERCEPT");
        return new HttpResponse();
    }),
    http.post(u(ENDPOINTS.query), async ({ request, params }) => {
        const url = new URL(request.url)
        let query = url.searchParams.get("q");
        let response = <R>{
            "query": query,
            "snippet_ids": []
        };
        console.log("msw: query", query);
        console.log("msw: /query response:")
        console.log("msw", response); 

        return HttpResponse.json(response);
    }),
    http.post(u(ENDPOINTS.sync), ({ request, params, cookies }) => {
        return HttpResponse.json({});
    }),
];