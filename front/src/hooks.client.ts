import type { ServerInit } from "@sveltejs/kit";

export const init: ServerInit = async () => {
    console.log("App start")
};