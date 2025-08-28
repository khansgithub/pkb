<script lang="ts">
    /* TO DO  
    -  fix ui issue with the sync button    
    */
    import {
        cacheResponse,
        queryInDb,
        send,
        sync as db_sync,
        type Response,
    } from "$lib/api";
    import { debounce } from "lodash-es"; // or write a small helper
    import { cn } from "$lib/util.svelte";
    import { sync_button } from "$lib/css";
    import { logger } from "$lib/logger";

    const DEBOUNCE_T = 700;
    var show_button_spinner = $state(false);


    var text = $state("");
    var response: Response = $state({} as Response);
    var form: HTMLFormElement;

    var i = 0;

    var d_send = debounce(async (q: string) => {
        logger.info(["debounce", i++]);

        logger.info("Check cache");
        let cached_query: Response | undefined;
        if ((cached_query = await queryInDb(q))) return cached_query;

        logger.info("Send POST");
        response = await send(q).then(cacheResponse);
        logger.info(["response snapshot", $state.snapshot(response)]);
    }, DEBOUNCE_T);

    async function sync(e: MouseEvent) {
        // TODO: error handle
        // TODO: unittest
        e.preventDefault();
        show_button_spinner = true;
        await db_sync();
        form.reset();
        response = {} as Response;
        show_button_spinner = false;
    }
</script>

<main>
    <div class="">
        <form bind:this={form}>
            <input
                id=""
                type="text"
                oninput={async (_) => await d_send(text)}
                class="border-2"
                bind:value={text}
            />
        </form>
        <p>Input text: {text}</p>
        <p>Respones: {JSON.stringify(response)}</p>
    </div>

    <div class="w-full place-self-center">
        <button
            onclick={sync}
            class={cn(sync_button)}
        >
            <p class="{show_button_spinner ? 'hidden': ''}">Sync</p>
            {@render spinner()}
        </button>
    </div>
</main>

{#snippet spinner()}
    <svg
        class="size-5 animate-spin {!show_button_spinner ? 'hidden': ''}"
        viewBox="0 0 24 24"
    >
        <path
            d="M12 22c5.421 0 10-4.579 10-10h-2c0 4.337-3.663 8-8 8s-8-3.663-8-8c0-4.336 3.663-8 8-8V2C6.579 2 2 6.58 2 12c0 5.421 4.579 10 10 10z"
            data-original="#000000"
        />
    </svg>
{/snippet}

<style>
</style>
