<script lang="ts">
    let {
        errorMessage = $bindable(),
        inputValue = $bindable(),
        onSubmit,
        onInput,
        onErrorClose,
        form = $bindable(),
        input = $bindable(),
    }: {
        errorMessage: string | null;
        inputValue: string;
        onSubmit: (e: SubmitEvent) => Promise<void>;
        onInput: () => Promise<void>;
        onErrorClose: () => void;
        form: HTMLFormElement | null;
        input: HTMLInputElement | null;
    } = $props();
</script>

{#if errorMessage}
    <div
        role="alert"
        class="alert alert-error fixed top-0 w-full flex flex-row items-center justify-between md:justify-center alert-vertical md:alert-vertical"
    >
        <span
            class="mx-auto md:mx-0 break-words text-sm md:text-base md:max-w-fit"
            >{errorMessage}</span
        >
        <button
            class="btn btn-square btn-dash"
            aria-label="Dismiss"
            onclick={onErrorClose}
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
                    d="M6 18 18 6M6 6l12 12"
                />
            </svg>
        </button>
    </div>
{/if}
<div class="pill">
    <div class="pill-inner"></div>
    <form bind:this={form} onsubmit={onSubmit}>
        <input
            bind:this={input}
            aria-label="Search"
            autocapitalize="off"
            autocomplete="off"
            autocorrect="off"
            data-sveltekit-keepfocus
            lang="en"
            maxlength="20"
            minlength="3"
            placeholder="type here"
            spellcheck="false"
            type="text"
            bind:value={inputValue}
            oninput={onInput}
        />
    </form>
    <div class="pill-backdrop absolute left-0 bottom-0 w-full h-full"></div>
</div>

<style>
    /* ==========================================================================
       PILL CONTAINER
       ========================================================================== */

    .pill {
        /* Layout */
        align-items: center;
        display: flex;
        justify-content: center;
        position: relative;

        /* Sizing */
        height: clamp(40px, 6vw, 48px);
        width: min(90%, 560px);

        /* Spacing */
        padding-left: clamp(10px, 3%, calc(560px * 0.1));
        padding-right: clamp(10px, 3%, calc(560px * 0.1));

        /* Visual */
        background: transparent;
        border-radius: 100px;

        /* Effects */
        transition: all 0.1s ease-in;

        /* Overflow */
        overflow: visible;
    }

    /* ----- Search icon (::before) ----- */
    .pill::before {
        /* Layout */
        content: "";
        left: clamp(8px, 3vw, 16px);
        position: absolute;
        top: 50%;
        transform: translateY(-45%);

        /* Sizing */
        height: clamp(18px, 4vw, 28px);
        width: clamp(18px, 4vw, 28px);

        /* Visual */
        /* background-image: url("data:image/svg+xml,..."); */
        background-position: center;
        background-repeat: no-repeat;
        background-size: contain;

        /* Stacking */
        z-index: 2;
    }

    /* ----- Inner gradient layer ----- */
    .pill-inner {
        /* Layout */
        inset: 0;
        position: absolute;

        /* Visual */
        background: linear-gradient(
            90deg,
            #b8b8b8 0%,
            #e8e8e8 20%,
            #ffffff 50%,
            #e8e8e8 80%,
            #b8b8b8 100%
        );
        border-radius: 100px;
        box-shadow:
            0 0 0 1px rgba(144, 224, 239, 0.6),
            0 0 12px 1px rgba(144, 224, 239, 0.4),
            0 12px 40px 0 rgba(144, 224, 239, 0.25),
            0 0px 70px 0 rgba(144, 224, 239, 0.1);

        /* Effects */
        transition: box-shadow 1s cubic-bezier(0, 1.84, 0.59, 0.64);

        /* Stacking & behaviour */
        pointer-events: none;
        z-index: 1;
    }

    /* ==========================================================================
       INPUT
       ========================================================================== */

    .pill form {
        height: 100%;
        position: relative;
        width: 100%;
    }

    .pill input {
        /* Layout */
        flex: 1;
        left: 0;
        min-width: 0;
        position: absolute;
        top: 0;

        /* Sizing */
        height: 100%;
        width: 100%;

        /* Visual */
        background: transparent;
        border: none;
        outline: none;

        /* Typography */
        font-size: clamp(30px, min(4dvh, 90%), 40px);
        text-align: center;
        text-transform: lowercase;
        color: hsl(0, 0%, 45%);
        text-overflow: ellipsis;
        white-space: nowrap;

        /* Stacking & behaviour */
        user-select: none;
        z-index: 100;
    }

    /* ==========================================================================
       FOCUS STATES
       ========================================================================== */

    .pill:focus-within {
        outline: unset;
    }

    .pill:focus-within input {
        color: hsl(0, 0%, 35%);
    }

    .pill:focus-within .pill-inner {
        background: linear-gradient(
            90deg,
            #b8b8b8 0%,
            #e8e8e8 20%,
            #ffffff 50%,
            #e8e8e8 80%,
            hsl(0, 0%, 90%) 100%
        );
        box-shadow:
            0 0 0 1px rgba(255, 89, 0, 0.7),
            0 0 12px 1px rgba(255, 89, 0, 0.3),
            0 12px 40px 0 rgba(255, 89, 0, 0.1),
            0 0px 70px 0 rgba(255, 89, 0, 0.05);
    }

    /* Parent page background when pill is focused */
    :global(main):has(.pill:focus-within) {
        background-color: hsl(229, 27%, 4%);
    }

    /* ==========================================================================
       BACKDROP (animated gradient)
       ========================================================================== */

    .pill-backdrop {
        /* Visual */
        background: linear-gradient(270deg, #00f0ff, #ff9100);
        background-size: 400% 400%;
        filter: blur(30px);
        opacity: 0.5;

        /* Effects */
        animation: TweenBackgroundPosition 4s ease infinite;

        /* Stacking */
        z-index: 0;
    }

    /* ==========================================================================
       ANIMATIONS
       ========================================================================== */

    @keyframes TweenBackgroundPosition {
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

    /* ==========================================================================
       RESPONSIVE (mobile)
       ========================================================================== */

    @media (max-width: 640px) {
        .pill {
            height: clamp(36px, 10vw, 48px);
            width: min(95%, 560px);
        }

        .pill::before {
            left: clamp(7px, 6vw, 12px);
            height: clamp(16px, 6vw, 22px);
            width: clamp(16px, 6vw, 22px);
        }
    }
</style>
