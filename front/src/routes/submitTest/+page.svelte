<script lang="ts">
    /* TO DO  
    -  fix ui issue with the sync button    
    */
    import {
        cacheResponseSnippets,
        queryInDb,
        query,
        sync as db_sync,
    } from "$lib/api";
    import { isQueryResponse } from "$lib/api.contract";
    import type { Snippet } from "$lib/types";
    import { debounce } from "lodash-es"; // or write a small helper
    import { cn } from "$lib/util.svelte";
    import { sync_button } from "$lib/css";
    import { logger } from "$lib/logger";

    const DEBOUNCE_T = 700;
    var show_button_spinner = $state(false);

    var text = $state("");
    var response: Snippet[] = $state([]);
    var form: HTMLFormElement;

    var i = 0;

    var d_send = debounce(async (q: string) => {
        logger.info(["debounce", i++]);

        logger.info("Check cache");
        const cached = await queryInDb(q);
        if (cached) {
            response = cached;
            return;
        }

        logger.info("Send POST");
        const r = await query(q);
        if (isQueryResponse(r)) {
            await cacheResponseSnippets({ query: q, snippets: r.snippets });
            response = r.snippets;
        } else {
            response = [];
        }
        logger.info(["response snapshot", $state.snapshot(response)]);
    }, DEBOUNCE_T);

    async function sync(e: MouseEvent) {
        // TODO: error handle
        // TODO: unittest
        e.preventDefault();
        show_button_spinner = true;
        await db_sync();
        form.reset();
        response = [];
        show_button_spinner = false;
    }
</script>

<main>
    <div class="">
        <form bind:this={form}>
            <input
                disabled
                id=""
                type="text"
                oninput={async (_) => await d_send(text)}
                onkeydown={(e) => {
                    e.key == "Enter" ? e.currentTarget.click() : null;
                }}
                class="border-2"
                bind:value={text}
            />
        </form>
        <p>Input text: {text}</p>
        <p>Respones: {JSON.stringify(response)}</p>
    </div>

    <div class="w-full place-self-center">
        <button class="btn btn-outline btn-wide" onclick={sync}>
            {#if show_button_spinner}
                <span class="loading loading-spinner"></span>
                <p>Loading</p>
            {:else}
                <p>Sync</p>
            {/if}
        </button>
    </div>
</main>

<style>
</style>
