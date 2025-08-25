<script lang="ts">
    import { cacheResponse, queryInDb, send, type Response } from "$lib/api";
    import { debounce } from "lodash-es"; // or write a small helper
    import { db, type Query } from "../../db";
    import { cn } from "$lib/util.svelte";

    const DEBOUNCE_T = 700;

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
`.split(" ")

    var text = $state("");
    var response: Response = $state({} as Response);

    var i = 0;

    var d_send = debounce(async (q: string) => {
        console.log("debounce", i++);

        console.log("Check cache");
        let cached_query: Response | undefined;
        if (cached_query = await queryInDb(q)) return cached_query

        console.log("Send POST");
        response = await send(q).then(cacheResponse);
    }, DEBOUNCE_T);

    async function sync(e: MouseEvent){
        e.preventDefault();
        
    }
</script>

<main>
    <div class="">
        <input
            id=""
            type="text"
            oninput={async _ => await d_send(text)}
            class="border-2"
            bind:value={text}
        />
        <p>Input text: {text}</p>
        <p>Respones: {JSON.stringify(response)}</p>
    </div>

    <div class="w-full place-self-center">
        <button onclick={sync} class={cn(button_classes, "w-full")}> Sync </button>
    </div>
</main>

<style>
</style>
