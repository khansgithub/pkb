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
            "snippets": [
                {
                    "title": "Hello World Example",
                    "tags": ["js", "example"],
                    "snippets": [
                        "```js\nconsole.log('Hello, world!')\n```\n\n**This is a mocked markdown response.**",
                        "Simple _markdown_ and `inline code` is **supported**.",
                    ]
                },
                {
                    "title": "Python Greeting",
                    "tags": ["python", "example"],
                    "snippets": [
                        "```python\nprint('Hello, world!')\n```\n\n_This is another mocked code block in Python._",
                        "**Python** is great for quick scripting!"
                    ]
                },
                {
                    "title": "TypeScript Function",
                    "tags": ["typescript", "add"],
                    "snippets": [
                        "```typescript\nfunction add(a: number, b: number): number {\n  return a + b;\n}\n```\n\n**Simple TypeScript addition function.**",
                        "You _could_ use this in your projects."
                    ]
                },
                {
                    "title": "Usage Example (bash)",
                    "tags": ["bash", "curl"],
                    "snippets": [
                        "### Usage Example\n\n```bash\ncurl -X POST https://api.example.com/query -d '{\"q\": \"example\"}'\n```\n\n> Feel free to change the query to experiment.",
                        "_Try using in your shell!_"
                    ]
                },
                {
                    "title": "Markdown Features",
                    "tags": ["markdown", "docs"],
                    "snippets": [
                        "- Markdown supports:\n    - **Bold**\n    - _Italic_\n    - `Inline code`\n    - Code blocks",
                        "Great for documentation."
                    ]
                },
                {
                    "title": "Mocked JSON Output",
                    "tags": ["json", "output"],
                    "snippets": [
                        "```json\n{\n  \"result\": \"This is a mock response\"\n}\n```\n\nSample JSON output.",
                        "You can copy/paste this into a tool."
                    ]
                },
                {
                    "title": "Horizontal Rule & Note",
                    "tags": ["markdown", "divider"],
                    "snippets": [
                        "---\n\nYou can add multiple code snippets and markdown text in one snippet array, as shown here.",
                        "Use `---` for a horizontal rule."
                    ]
                },
                {
                    "title": "Multi-Language Example",
                    "tags": ["multi", "demo"],
                    "snippets": [
                        "```go\nfmt.Println(\"Hello from Go\")\n```",
                        "Or try Ruby:\n\n```ruby\nputs 'Hello from Ruby!'\n```"
                    ]
                }
            ]
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