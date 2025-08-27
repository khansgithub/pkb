<script lang="ts">
    import {
        cacheResponse,
        queryInDb,
        send,
        sync as db_sync,
        type Response,
    } from "$lib/api";
    import { debounce } from "lodash-es"; // or write a small helper
    import { cn } from "$lib/util.svelte";
    import { spring } from "svelte/motion";

    const DEBOUNCE_T = 700;
    var show_button_spinner = $state(true);
    var button_classes: Array<string> = `
active:from-cyan-600
active:to-orange-600
bg-gradient-to-r
from-indigo-500
to-pink-500
via-purple-500
duration-300
ease-out
font-semibold
hover:shadow-pink-500/40
hover:shadow-sm
px-6
py-3
rounded-2xl
shadow-indigo-500/30
shadow-xs
text-white
transition-all
`.split("\n");

    var text = $state("");
    var response: Response = $state({} as Response);

    var i = 0;

    var d_send = debounce(async (q: string) => {
        console.log("debounce", i++);

        console.log("Check cache");
        let cached_query: Response | undefined;
        if ((cached_query = await queryInDb(q))) return cached_query;

        console.log("Send POST");
        response = await send(q).then(cacheResponse);
        console.log("response snapshot", $state.snapshot(response));
    }, DEBOUNCE_T);

    async function sync(e: MouseEvent) {
        e.preventDefault();
        show_button_spinner = !show_button_spinner;
    }
</script>

<main>
    <div class="">
        <input
            id=""
            type="text"
            oninput={async (_) => await d_send(text)}
            class="border-2"
            bind:value={text}
        />
        <p>Input text: {text}</p>
        <p>Respones: {JSON.stringify(response)}</p>
    </div>

    <div class="w-full place-self-center">
        <button
            onclick={sync}
            class={cn(
                button_classes,
                "w-full flex items-center justify-center",
            )}
        >
            <p class="{show_button_spinner ? 'hidden': ''}">Sync</p>
            {@render spinner()}
            <!-- <p>Test</p> -->
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
