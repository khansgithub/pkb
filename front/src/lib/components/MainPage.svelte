<script lang="ts">
    import Results from "$lib/components/Results.svelte";
    import SearchBox from "$lib/components/SearchBox.svelte";
    import { DEBOUNCE_T } from "$lib/const";
    import { getSnippetsFromQuery } from "$lib/function";
    import { logger } from "$lib/logger";
    import { queryStore } from "$lib/queryStore";
    import { debounce } from "lodash-es";
    import type { Snippet } from "$lib/types";

    const cards = $derived($queryStore);
    const log = logger.child({ module: "search_box" });

    let show_button_spinner = $state(false);
    let form: HTMLFormElement | null = $state(null);
    let input: HTMLInputElement | null = $state(null);
    let inputValue: string = $state("");
    let errorMessage: string | null = $state(null);
    let _debounceCallCount = 0;
    
    let snippets: Snippet[] = [];

    const onSubmitDebounced = debounce(async () => {
        _debounceCallCount++;
        log.info(
            { call: _debounceCallCount, inputValue },
            "Debounced submit fired",
        );
        if (inputValue.trim().length <= 2) return;
        onSubmit();
    }, DEBOUNCE_T);

    async function onSubmit(e?: SubmitEvent) {
        e && e.preventDefault();
        log.info({ inputValue }, "onSubmit called");

        const queryString = $state.snapshot(inputValue);

        [snippets, errorMessage] = await getSnippetsFromQuery(queryString, errorMessage);

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
