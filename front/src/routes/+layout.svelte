<script lang="ts">
    import "../app.css";
    // import favicon from '$lib/assets/favicon.svg';

    let { children } = $props();
</script>

<svelte:head>
    <!-- <link rel="icon" href={favicon} /> -->
</svelte:head>

<main
    class="relative flex min-h-screen min-w-screen items-center justify-center overflow-hidden bg-[var(--color-bg)] transition-colors duration-1000 ease-out"
>
    <div class="noise-overlay"></div>
    {@render children?.()}
</main>

<style>
    main {
        /* transition: background 1s cubic-bezier(0.7, 0.09, 0.21, 0.94); */
        /* background: radial-gradient(circle at center, #0f111a 0%, red 100%);
        transition: background 0.2s ease; */
    }

    /* main {
        background: linear-gradient(270deg, #2ddbae, #e6a218);
        background-size: 400% 400%;
        animation: AnimationName 5s ease infinite;
    } */

    @keyframes AnimationName {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    .noise-overlay {
        pointer-events: none;
        position: fixed;
        inset: 0;
        opacity: 0.1;
        /* mix-blend-mode: multiply; */
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 1024 1024' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.5' numOctaves='6' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' fill='black' fill-opacity='1' filter='url(%23noise)'/%3E%3C/svg%3E");

        /* background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 1024 1024' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3CfeComponentTransfer%3E%3CfeFuncA type='table' tableValues='0 0 0 0.15'/%3E%3C/feComponentTransfer%3E%3C/filter%3E%3Crect width='100%25' height='100%25' fill='black' filter='url(%23noise)'/%3E%3C/svg%3E") */
    }
</style>
