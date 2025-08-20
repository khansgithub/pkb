<script lang="ts">
	import '../app.css';
	// import favicon from '$lib/assets/favicon.svg';
	
	let { children } = $props();
</script>

<svelte:head>
	<!-- <link rel="icon" href={favicon} /> -->
</svelte:head>

<main class="text-white min-h-screen min-w-screen flex justify-center items-center">
	{@render children?.()}
</main>
