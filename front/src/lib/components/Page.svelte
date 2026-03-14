<script lang="ts">
    import { cacheResponseSnippets, query, queryInDb } from "$lib/api";
    import Results from "$lib/components/Results.svelte";
    import SearchBox from "$lib/components/SearchBox.svelte";
    import { DEBOUNCE_T } from "$lib/const";
    import { logger } from "$lib/logger";
    import { queryStore } from "$lib/queryStore";
    import type { Snippet } from "$lib/types";
    import { debounce } from "lodash-es";

    const cards = $derived($queryStore);
    const log = logger.child({ module: "search_box" });

    let show_button_spinner = $state(false);
    let form = $state<HTMLFormElement | null>(null);
    let input = $state<HTMLInputElement | null>(null);
    let inputValue = $state("");
    let errorMessage = $state<string | null>(null);
    let _debounceCallCount = 0;

    const onSubmitDebounced = debounce(async () => {
        _debounceCallCount++;
        log.info(
            { call: _debounceCallCount, inputValue },
            "Debounced submit fired",
        );
        if (inputValue.trim().length <= 2) return;
        alert("debounce");
        onSubmit();
    }, DEBOUNCE_T);

    async function onSubmit(e?: SubmitEvent) {
        e && e.preventDefault();
        log.info({ inputValue }, "onSubmit called");
        const queryString = $state.snapshot(inputValue);
        const cached_query = await queryInDb(queryString);

        var snippets: Snippet[] = [];

        if (cached_query && cached_query.length > 0) {
            log.info({ cached_query }, "Cached result found");
            snippets = cached_query;
        } else {
            log.info({ queryString }, "No cached result found, sending POST");
            const response = await query(queryString);
            if ("error" in response) {
                log.error(
                    { error: response.error },
                    "Error received from query",
                );
                errorMessage =
                    response.error.message ??
                    response.error.name ??
                    "Something went wrong";
                return;
            }
            errorMessage = null;
            snippets = await cacheResponseSnippets({
                query: queryString,
                snippets: response.snippets,
            });
        }

        log.info(
            { queryString, responseSnapshot: $state.snapshot(snippets) },
            "POST complete, response received",
        );
        $queryStore = snippets;
    }

    async function doOnSubmit() {
        log.info("onChange (user typed), scheduling debounced submit");
        onSubmitDebounced.cancel();
        onSubmitDebounced();
    }

    async function onInput() {
        log.info(
            { inputValue },
            "onInput (user typed), scheduling debounced submit",
        );
        doOnSubmit();
    }

    function onErrorClose() {
        errorMessage = null;
        input?.focus();
    }
</script>

<div
    class="min-w-dvw min-h-dvh h-full relative flex flex-col items-center overflow-auto gap-10 md:gap-15"
>
    <div
        class="w-full relative mt-[15dvh] md:mt-[25dvh] flex flex-col items-center"
    >
        <SearchBox
            bind:errorMessage
            bind:inputValue
            bind:form
            bind:input
            {onSubmit}
            {onInput}
            {onErrorClose}
        />
    </div>
    <!-- <button
		class="btn btn-outline btn-wide"
		onclick={() => {
			$queryStore = $queryStore.slice(0, -1);
		}}>Pop</button
	> -->
    <div
        class="w-full h-full flex-1 flex-col items-center relative mt-15 md:mt-0 gap-2 overflow-y-scroll overflow-x-hidden"
    >
        <Results {cards} />
    </div>
</div>
