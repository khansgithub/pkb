<script lang="ts">
    import type { Snippet } from "$lib/types";
    import { blur, fly, fade } from "svelte/transition";
    import ResultsCard from "./ResultsCard.svelte";

    let { cards = [] }: { cards?: Snippet[] } = $props();

    let placeholderCards: Snippet[] = $state(
        Array.from({ length: 6 }, (_, i) => ({
            title: `Example Card ${i + 1}`,
            tags: ["Tag 1", "Tag 2", "Tag 3"],
            description: "This is a **description** with _markdown_ support.",
            snippets: [
                "```js\nfunction helloWorld() {\n  console.log('Hello, world!');\n}\n```",
            ],
        })),
    );

    // const displayCards = $derived(cards.length > 0 ? cards : placeholderCards);
    const displayCards = $derived(cards);
</script>

<div
    class="bot h-full w-full md:w-4/5 lg:w-3/5 absolute top-0 bottom-0 self-start justify-self-center z-10"
>
    <div class="flex flex-col gap-5 items-stretch w-full mx-auto">
        {#each displayCards as card, i (card.title + "-" + i)}
            <div
                class="[all:inherit]"
                transition:fly={{ x: 100, duration: 1000 }}
            >
                <ResultsCard {card} index={i} />
            </div>
        {/each}
    </div>
</div>

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
