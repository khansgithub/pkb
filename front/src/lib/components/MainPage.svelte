<script lang="ts">
    import Results from "$lib/components/Results.svelte";
    import SearchBox from "$lib/components/SearchBox.svelte";
    import { DEBOUNCE_T } from "$lib/const";
    import { getSnippetsFromQuery, isMobile } from "$lib/functions";
    import { logger } from "$lib/logger";
    import { queryStore } from "$lib/queryStore";
    import type { Snippet } from "$lib/types";
    import { debounce } from "lodash-es";

    const cards = $derived($queryStore);
    const log = logger.child({ module: "search_box" });

    let input: HTMLInputElement | null = $state(null);
    let inputValue: string = $state("");
    let queryStringWhenNoResult = $state("");
    let errorMessage: string | null = $state(null);
    let loading = $state(false);
    let _debounceCallCount = 0;

    let snippets: Snippet[] = [];

    const onSubmitDebounced = debounce(
        async () => {
            const p = new Promise<void>(async (resolve) => {
                _debounceCallCount++;
                log.info(
                    { call: _debounceCallCount, inputValue },
                    "Debounced submit fired",
                );

                if (inputValue.trim().length == 0) {
                    resolve();
                    return false;
                }

                if (inputValue.trim().length <= 2) {
                    log.info({ inputValue }, "too short");
                    input?.setCustomValidity(`Please lengthen this text to 10 characters or more (you're currently using ${inputValue.trim().length} characters)`);
                    input?.reportValidity();
                    resolve();
                    return false;
                } else {}

                await onSubmit();
                loading = false;
                resolve();
            }).then((res) => (loading = false))
            await p;
        },
        DEBOUNCE_T * (isMobile() ? 3 : 1),
    );

    async function onSubmit(e?: SubmitEvent) {
        e && e.preventDefault();
        log.info({ inputValue }, "onSubmit called");

        const queryString = $state.snapshot(inputValue);

        [snippets, errorMessage] = await getSnippetsFromQuery(
            queryString,
            errorMessage,
        );

        log.info(
            { queryString, responseSnapshot: $state.snapshot(snippets) },
            "POST complete, response received",
        );

        loading = false;
        if (snippets.length == 0)
            queryStringWhenNoResult = inputValue.toLowerCase();
        $queryStore = snippets;
    }

    async function callOnSubmit() {
        log.info("onChange (user typed), scheduling debounced submit");
        onSubmitDebounced.cancel();
        onSubmitDebounced();
    }

    async function onInput(
        e: Event & { currentTarget: EventTarget & HTMLInputElement },
    ) {
        log.info(
            { inputValue },
            "onInput (user typed), scheduling debounced submit",
        );
        loading = true;
        input?.setCustomValidity("")
        await callOnSubmit()
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
            bind:input
            {onInput}
            {onErrorClose}
        />
    </div>
    <div class="relative h-0 w-full overflow-visible">
        {#if loading}
            <span
                class="loading loading-spinner loading-md absolute transform left-1/2 -translate-x-1/2"
            ></span>
        {/if}
    </div>
    <!-- <button
		class="btn btn-outline btn-wide"
		onclick={() => {
			$queryStore = $queryStore.slice(0, -1);
		}}>Pop</button
	> -->
    <div
        class="w-full h-full flex-1 flex-col items-center relative md:mt-0 gap-2 overflow-y-scroll overflow-x-hidden"
    >
        <Results {cards} queryString={queryStringWhenNoResult} />
    </div>
</div>
