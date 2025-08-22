<script lang="ts">
    import { send } from "$lib/api";
    import { debounce } from 'lodash-es'; // or write a small helper
    var text = $state("");
    var response = $state("")

    var i = 0;

    var d_send = debounce(async (q: string) => {
        console.log("debounce", i++);
        try{
            response = await send(q);
            console.log("Response:", $state.snapshot(response));
        }
        catch (e) {
            console.error(e);
        }
    }, 700)

    function f(e: Event) {
        d_send(text);
    }
</script>

<div class="">
    <input id="" type="text" oninput={f} class="border-2" bind:value={text} />
    <p>Input text: {text}</p>
    <p>Respones: {JSON.stringify(response)}</p>
</div>

<style>
</style>
