<script lang="ts">
    import type { Attachment } from "svelte/attachments";
    import { c, cn, get_noise, updateNoiseInternal } from "./util.svelte";
    let z: Map<number, HTMLElement> = new Map();
    let x = $state(0);
    let y = $state(0);

    let hover_initial_x: number = $state(0);

    function jitterInRange(
        value: number,
        step: number = 0.1,
        min: number = 0.05,
        max: number = 0.08,
    ): number {
        const delta = (Math.random() * 2 - 1) * step; // random between -step and +step
        let result = value + delta;

        // Clamp to [min, max]
        if (result < min) result = min;
        if (result > max) result = max;

        return result;
    }

    let t = updateNoiseInternal();
    clearInterval(t);

    const setInitialX: Attachment<HTMLDivElement> = (
        element: HTMLDivElement,
    ) => {
        if (hover_initial_x != 0) return;
        hover_initial_x = element.getBoundingClientRect().x;
        console.log(hover_initial_x);
    };

    const addToZ: Attachment<HTMLDivElement> = (element: HTMLElement) => {
        let _z: string | null = element.style.zIndex;
        if (_z == "") {
            for (let i = 0; i < element.classList.length; i++) {
                let cls: string = element.classList.item(i) || "";
                if (!(cls[0] == "z" || (cls[0] == "!" && cls[1] == "z")))
                    continue;
                let index: string | undefined = cls.split("-")[1];
                if (index === undefined) {
                    console.error(element);
                    throw new Error("Couldn't find tailwind index class");
                }
                _z = index;
                break;
            }
            if (_z == "") return;
            // console.log("skipping", element.classList)
        }
        let zindex: number = parseInt(_z);
        if (Number.isNaN(zindex)) {
            throw new Error("Error parsing index");
        }
        z.set(zindex, element);
        // console.log(z)
        z.keys()
            .toArray()
            .sort((a, b) => a - b)
            .forEach((k) => {
                // debugger;
                console.log(k, z.get(k));
                // console.log(k)
            });
        // console.log(z.keys().toArray().sort((a, b) => a - b));
        console.log("----");
    };

    function draggableHover(element: HTMLElement) {
        let _x =
            x - hover_initial_x - element.getBoundingClientRect().width / 2;
        if (hover_initial_x == 0) return;
        element.style.left = `${_x}px`;
    }
</script>

<svelte:window
	onmousemove={(e: MouseEvent) => {
		[x, y] = [e.x, e.y];
	}}
	onresize={(_) => {
		// FIXME: on window resize the light doesnt follow the cursor properly
		// hover_initial_x=0;
		// console.log("resize");
	}}
/>

<div id="input_box" class="relative">
    <input
        type="text"
        name=""
        id="search_box"
        {@attach addToZ}
        placeholder="foo"
        class={cn(c.id_middle.input.css, "z-100")}
    />

    <!-- inner cursor light -->
    <div
        id="inner_cursor_light"
        {@attach addToZ}
        class={cn(
            c.id_middle.input.css,
            "z-50 overflow-hidden !p-0 !bg-orange-900/0 !shadow-none blur-xs top-[5px]",
        )}
    >
        {@render div(
            "inner_light_mask",
            cn(
                c.id_middle.input.css,
                "overflow-hidden !-mt-0 !p-0 !bg-black/100 -top-[0.5vw] !shadow-none",
            ),
        )}

        <div
            id="inner_light_highlight"
            {@attach addToZ}
            {@attach draggableHover}
            class={cn(
                c.id_middle.clipper.hover.css,
                "!bg-yellow-200 !shadow-none",
            )}
        ></div>
    </div>
    <!-- / inner cursor light -->
    <!-- 
			<div
				id="input-noise"
				{@attach addToZ}
				class={cn(
					c.id_middle.input.css,
					"!shadow-none radial-noise !mt-[2vw] z-20 opacity-34",
				)}
				style='--noise: url("{get_noise(null)}")'
			></div> -->

    <!-- background cursor light -->
    <div
        id="back-cursor-light"
        class={cn([c.id_middle.input.css, c.id_middle.clipper.css])}
    >
        <div
            {@attach setInitialX}
            {@attach draggableHover}
            {@attach addToZ}
            class={cn(c.id_middle.clipper.hover.css, "!bg-white z-30")}
        ></div>
    </div>

    {@render div(
        "white-glow",
        cn(
            c.id_middle.input.css,
            "!bg-black shadow-md shadow-blue-100 blur-[1px] z-20",
        ),
    )}

    {@render div(
        "back-glow",
        cn([c.id_middle.input.css, c.id_middle.back_glow.css], "z-10"),
    )}

    {@render div(
        "base-layer",
        cn(c.id_middle.input.css, "!bg-black !shadow-none z-0"),
    )}
</div>
{#snippet div(id: string, classes: string, style?: string)}
    <div {id} class={classes} {@attach addToZ} {style}></div>
{/snippet}

<style>
    .test {
        /* background-image: var(--noise); */
        mask-image: var(--noise);
        mask-repeat: repeat;
        mask-size: 100px 100px;
    }
    .noise {
        background-image: var(--noise);
    }

    .radial-noise {
        background:
            var(--noise),
            /* black; */
                /* linear-gradient(to bottom, rgba(0,0,0,0) 60%, black 90%); */
                radial-gradient(
                    100% 110% at center,
                    rgba(0, 0, 0, 0) 0%,
                    var(--color-black) 45%
                );
        background-size: cover;
        background-blend-mode: multiply;
        mix-blend-mode: screen;
    }
</style>
