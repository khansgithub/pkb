<script lang="ts">
	import Child from './test.svelte';

	let count = $state<string | null>("");
</script>

<button onclick={() => (count += "")}>
	clicks (parent): {count}
</button>

<Child {count} />