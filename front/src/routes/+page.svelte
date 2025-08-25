<script lang="ts">
	import SearchBox from "$lib/search_box.svelte";
</script>

<div
	class="min-h-screen w-full grid grid-rows-[auto,1fr,auto] overflow-hidden text-gray-300]"
>
	<div class="">top</div>
	<div id="middle" class="m-[20vw] [font-size:_clamp(1em,5vw,10em)]">
		<SearchBox/>
	</div>
	<div class="">bottom</div>
</div>

<style>
</style>
