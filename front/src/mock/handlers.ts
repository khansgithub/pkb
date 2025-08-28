import { http, HttpResponse } from 'msw'
import type { Response as R } from '$lib/api';
import { BACKEND, ENDPOINTS } from '$lib/const';
import { logger as app_logger } from '$lib/logger';

const logger = app_logger.child({ service: 'msw' });

let base = new URL(BACKEND);
let u = (endpoint: string): string => {
    let url = new URL(endpoint, base).toString();
    return url;
};

// cors
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

let query = http.post(
    u(ENDPOINTS.query),
    async ({ request, params }) => {
        const url = new URL(request.url)
        let query = url.searchParams.get("q");
        let response = <R>{
            "query": query,
            "snippet_ids": []
        };
        logger.info(query, "query");
        logger.info(response, "response");

        return HttpResponse.json(response);
    }
);

let sync = http.post(
    u(ENDPOINTS.sync),
    async ({ request, params, cookies }) => {
        let delay = 5000;
        logger.info(delay, "Delay")
        await new Promise(f => setTimeout(f, delay));
        return HttpResponse.json({});
    }
);

let _handler = {
    [ENDPOINTS.query]: query,
    [ENDPOINTS.sync]: sync
}

export const handlers = [
    http.get(u("/*"), () => {
        logger.info("INTERCEPT");
        return new HttpResponse();
    }),
    ...Object.values(_handler)
];