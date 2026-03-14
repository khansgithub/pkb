<script lang="ts">
    import { renderMarkdown } from "$lib/markdown";
    import type { Snippet } from "$lib/types";
    import { onDestroy } from "svelte";

    let { card, index = 0 }: { card: Snippet; index?: number } = $props();
    let expanded = $state(false);
    const expandId = $derived(`results-card-${index}`);
    const descriptionHtml = $derived(renderMarkdown(card.description ?? ""));

    onDestroy(() => {
        console.log("[ResultsCard] the component is being destroyed");
    });
</script>

<div class="card-row w-full">
    <div class="card bg-base-100 shadow-xl overflow-hidden">
        <input
            type="checkbox"
            id={expandId}
            class="card-toggle"
            bind:checked={expanded}
        />
        <div class="card-header">
            <div class="card-header-inner p-6 pb-4">
                <h2 class="card-title text-xl font-bold mb-2">
                    {card.title ?? "Untitled"}
                </h2>
                <div class="flex flex-wrap gap-2">
                    {#each card.tags as tag, idx (idx)}
                        {#if tag.length > 1}
                            <span
                                class="inline-flex items-center rounded-md bg-gray-400/10 px-2 py-1 text-xs font-medium text-gray-400 inset-ring inset-ring-gray-400/20"
                                >{tag}</span
                            >
                        {/if}
                    {/each}
                </div>
            </div>
        </div>

        <div class="card-expandable">
            <div class="card-expand-inner">
                <div class="space-y-4 mx-6 mb-6">
                    {#if descriptionHtml}
                        <div
                            class="prose prose-invert prose-sm max-w-none text-neutral-content overflow-y-auto prose-p:my-1"
                        >
                            {@html descriptionHtml}
                        </div>
                    {/if}
                    <div
                        class="card-content-area border border-dashed bg-[rgba(0,0,0,0.2)] border-gray-800 text-neutral-content rounded-md p-3 text-sm overflow-y-auto"
                    >
                        <div
                            class="prose prose-invert prose-sm max-w-none prose-pre:bg-transparent prose-pre:p-0 prose-pre:my-0 prose-pre:border-0 prose-pre:font-mono prose-code:font-mono prose-code:before:content-none prose-code:after:content-none"
                        >
                            {#each card.snippets as snippet, idx (idx)}
                                <div class="snippet hljs-wrapper">
                                    {@html renderMarkdown(snippet)}
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-center pb-3">
            <label
                for={expandId}
                class="btn btn-sm btn-outline btn-primary rounded-full shadow-lg cursor-pointer"
            >
                {expanded ? "collapse" : "expand"}
            </label>
        </div>
    </div>
</div>

<style>
    .card-row {
        min-height: 0;
    }

    .card {
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
        position: relative;
        outline: none;
        box-shadow:
            0 4px 16px 0 rgba(0, 0, 0, 0.1),
            0 0.5px 2px 0 rgba(0, 0, 0, 0.04);
    }

    .card-toggle {
        display: none;
        opacity: 0;
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .card-header {
        display: block;
        min-height: 4rem;
        transition: background 0.2s ease;
    }

    .card-header-inner {
        padding-left: 1.5rem;
    }

    .card-expandable {
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card-toggle:checked ~ .card-expandable {
        grid-template-rows: 1fr;
    }

    .card-expand-inner {
        min-height: 0;
        overflow: hidden;
        min-width: 0;
    }

    :global(.hljs-wrapper pre),
    :global(.hljs-wrapper code),
    :global(.hljs-wrapper .hljs) {
        font-family:
            ui-monospace,
            SFMono-Regular,
            SF Mono,
            Menlo,
            Consolas,
            Liberation Mono,
            monospace;
        font-size: 0.875rem;
    }
</style>
