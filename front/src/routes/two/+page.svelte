<script lang="ts">
    import { send } from "$lib/api";
    import { debounce } from "lodash-es"; // or write a small helper
    import { db, type Query } from "../../db";
    import { cn } from "../../util.svelte";

    var button_classes = [
        "px-4",
        "py-2",
        "rounded-lg",
        "bg-black",
        "text-white",
        "shadow-sm",
        "shadow-blue-300/20",
        "hover:shadow-orange-500",
        "transition",
    ];

    var text = $state("");
    var response = $state();

    var i = 0;

    var d_send = debounce(async (q: string) => {
        console.log("debounce", i++);
        try {
            response = await send(q);
            let row_id = await db.queries.add($state.snapshot(response));
            console.log("Response:", $state.snapshot(response));
            console.log("id", row_id);
        } catch (e) {
            console.error(e);
        }
    }, 700);

    function f(e: Event) {
        d_send(text);
    }

    async function sync(e: MouseEvent){
        e.preventDefault();
        await sync
    }
</script>

<main>
    <div class="">
        <input
            id=""
            type="text"
            oninput={f}
            class="border-2"
            bind:value={text}
        />
        <p>Input text: {text}</p>
        <p>Respones: {JSON.stringify(response)}</p>
    </div>

    <div class="jw-full nplace-self-center">
        <button onclick={sync} class={cn(button_classes, "w-full")}> Sync </button>
    </div>
</main>

<style>
</style>
