import { http, HttpResponse } from 'msw'
import type { QueryResponse } from '$lib/api.contract';
import { BACKEND, ENDPOINTS } from '$lib/const';
import { logger as app_logger } from '$lib/logger';

const logger = app_logger.child({ service: 'msw' });

let base = new URL(BACKEND);

/**
 * Constructs a full URL string for a given API endpoint by resolving it against the BACKEND base URL.
 *
 * @param endpoint - The API endpoint path (e.g., "/api/foo").
 * @returns The full URL as a string.
 */
function buildUrl(endpoint: string): string {
    return new URL(endpoint, base).toString();
}

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
    buildUrl(ENDPOINTS.query),
    async ({ request, params }) => {
        const url = new URL(request.url)
        let query = url.searchParams.get("q");
        let response: QueryResponse = {
            snippets: [
                {
                    id: 1,
                    title: "Hello World Example",
                    tags: ["js", "example"],
                    snippets: [
                        {
                            type: "code",
                            lang: "js",
                            lines: ["console.log('Hello, world!')"],
                            snippet_id: 1,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["", "**This is a mocked markdown response.**"],
                            snippet_id: 1,
                            pos: 1,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["Simple _markdown_ and `inline code` is **supported**."],
                            snippet_id: 1,
                            pos: 2,
                        },
                    ],
                },
                {
                    id: 2,
                    title: "Python Greeting",
                    tags: ["python", "example"],
                    snippets: [
                        {
                            type: "code",
                            lang: "python",
                            lines: ["print('Hello, world!')"],
                            snippet_id: 2,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["", "_This is another mocked code block in Python._"],
                            snippet_id: 2,
                            pos: 1,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["**Python** is great for quick scripting!"],
                            snippet_id: 2,
                            pos: 2,
                        },
                    ],
                },
                {
                    id: 3,
                    title: "TypeScript Function",
                    tags: ["typescript", "add"],
                    snippets: [
                        {
                            type: "code",
                            lang: "typescript",
                            lines: [
                                "function add(a: number, b: number): number {",
                                "  return a + b;",
                                "}",
                            ],
                            snippet_id: 3,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["", "**Simple TypeScript addition function.**"],
                            snippet_id: 3,
                            pos: 1,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["You _could_ use this in your projects."],
                            snippet_id: 3,
                            pos: 2,
                        },
                    ],
                },
                {
                    id: 4,
                    title: "Usage Example (bash)",
                    tags: ["bash", "curl"],
                    snippets: [
                        {
                            type: "text",
                            lang: null,
                            lines: ["### Usage Example", ""],
                            snippet_id: 4,
                            pos: 0,
                        },
                        {
                            type: "code",
                            lang: "bash",
                            lines: [
                                "curl -X POST https://api.example.com/query -d '{\"q\": \"example\"}'",
                            ],
                            snippet_id: 4,
                            pos: 1,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["", "> Feel free to change the query to experiment."],
                            snippet_id: 4,
                            pos: 2,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["_Try using in your shell!_"],
                            snippet_id: 4,
                            pos: 3,
                        },
                    ],
                },
                {
                    id: 5,
                    title: "Markdown Features",
                    tags: ["markdown", "docs"],
                    snippets: [
                        {
                            type: "text",
                            lang: null,
                            lines: [
                                "- Markdown supports:",
                                "    - **Bold**",
                                "    - _Italic_",
                                "    - `Inline code`",
                                "    - Code blocks",
                            ],
                            snippet_id: 5,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["Great for documentation."],
                            snippet_id: 5,
                            pos: 1,
                        },
                    ],
                },
                {
                    id: 6,
                    title: "Mocked JSON Output",
                    tags: ["json", "output"],
                    snippets: [
                        {
                            type: "code",
                            lang: "json",
                            lines: ["{", '  "result": "This is a mock response"', "}"],
                            snippet_id: 6,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["", "Sample JSON output."],
                            snippet_id: 6,
                            pos: 1,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["You can copy/paste this into a tool."],
                            snippet_id: 6,
                            pos: 2,
                        },
                    ],
                },
                {
                    id: 7,
                    title: "Horizontal Rule & Note",
                    tags: ["markdown", "divider"],
                    snippets: [
                        {
                            type: "text",
                            lang: null,
                            lines: [
                                "---",
                                "",
                                "You can add multiple code snippets and markdown text in one snippet array, as shown here.",
                            ],
                            snippet_id: 7,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["Use `---` for a horizontal rule."],
                            snippet_id: 7,
                            pos: 1,
                        },
                    ],
                },
                {
                    id: 8,
                    title: "Multi-Language Example",
                    tags: ["multi", "demo"],
                    snippets: [
                        {
                            type: "code",
                            lang: "go",
                            lines: ['fmt.Println("Hello from Go")'],
                            snippet_id: 8,
                            pos: 0,
                        },
                        {
                            type: "text",
                            lang: null,
                            lines: ["Or try Ruby:", ""],
                            snippet_id: 8,
                            pos: 1,
                        },
                        {
                            type: "code",
                            lang: "ruby",
                            lines: ["puts 'Hello from Ruby!'"],
                            snippet_id: 8,
                            pos: 2,
                        },
                    ],
                },
            ],
        };
        logger.info(query, "query");
        logger.info(response, "response");

        return HttpResponse.json(response);
    }
);

let sync = http.post(
    buildUrl(ENDPOINTS.sync),
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
    http.get(buildUrl("/*"), () => {
        logger.info("INTERCEPT");
        return new HttpResponse();
    }),
    ...Object.values(_handler)
];
