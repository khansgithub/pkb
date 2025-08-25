import type { ServerInit } from "@sveltejs/kit";
export const init: ServerInit = async () => {
    console.log("App start")
    if (import.meta.env.DEV) {
        const { worker } = await import('./mock/browser');
        worker.start({
            serviceWorker: {
                url: '/mockServiceWorker.js',
            },
        });
    }
};