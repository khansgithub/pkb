<script lang="ts">
    import type { Snippet } from "$lib/types";
    import { fly, fade, scale } from "svelte/transition";
    import ResultsCard from "./ResultsCard.svelte";

    type Props = {
        cards: Snippet[] | null;
        queryString: string;
    };

    let { cards = null, queryString }: Props = $props();

    let placeholderCards: Snippet[] = $state(
        Array.from({ length: 6 }, (_, i) => ({
            title: `Example Card ${i + 1}`,
            tags: ["Tag 1", "Tag 2", "Tag 3"],
            description: "This is a **description** with _markdown_ support.",
            snippets: [
                {
                    type: "code" as const,
                    lang: "js",
                    lines: [
                        "function helloWorld() {",
                        "  console.log('Hello, world!');",
                        "}",
                    ],
                    snippet_id: 0,
                    pos: 0,
                },
            ],
        })),
    );

    const displayCards = $derived(
        cards ? (cards.length > 0 ? cards : [null]) : [],
    );
</script>

<div
    class="bot h-full w-full md:w-4/5 lg:w-3/5 absolute top-0 bottom-0 self-start justify-self-center z-10"
>
    <div class="flex flex-col gap-5 items-stretch w-full mx-auto">
        {#each displayCards as card, i}
            <div
                class="[all:inherit]"
                in:fly={{ x: 100, duration: 1000 + i * 100 }}
                out:fly={{ x: -40, duration: 350 + i * 100 }}
            >
                <!-- <p>{card.title}</p> -->
                {#if card}
                    <ResultsCard {card} index={i} />
                {:else}
                    {@render noResults()}
                {/if}
            </div>
        {/each}
    </div>
</div>

{#snippet noResults()}
    <div
        class="text-center text-lg font-semibold mt-10 opacity-25 flex items-center justify-center gap-2"
        in:fly={{ x: 0, duration: 1000 }}
        out:fly={{ x: 0, duration: 350 }}
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="size-6"
        >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
            />
        </svg>
        <p>No results found for: '{queryString}'</p>
    </div>
{/snippet}

<style>
    .bot {
        background-color: hsl(0, 0%, 9.7%);
    }

    @media (min-width: 768px) {
        .bot {
            box-shadow:
                0px -4px 100px 8px rgba(0, 0, 0, 0.01),
                0px 0px 30px -6px rgba(0, 0, 0, 0.02) inset;
        }
    }
</style>
