<script lang="ts">
	import type { Action } from "svelte/action";
	let x = $state(0);
	let y = $state(0);

	let hover_initial_x: number = 0;

	let noise_freq = $state(6.7)
	// let noise = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><filter id='noiseFilter'><feTurbulence type='fractalNoise' baseFrequency='${noise_freq}' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23noiseFilter)'/></svg>`
	let noise = (f: number) => {return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><filter id='noiseFilter'><feTurbulence type='fractalNoise' baseFrequency='${f}' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23noiseFilter)'/></svg>`}

	let t = setInterval(() => {
		let n = Math.random() * (1.1 - 0.9) + 0.9;
		noise_freq *= n;
	}, 1000/6)

	// clearInterval(t)

	function get_noise(freq: number){
		return noise(freq);
	}

	const setInitialX: Action<HTMLDivElement, any, any> = (
		element: HTMLDivElement,
	) => {
		if (hover_initial_x != 0) return;
		hover_initial_x = element.getBoundingClientRect().x;
		console.log(hover_initial_x);
	};

	function draggableHover(element: HTMLElement) {
		let _x = x - hover_initial_x - (element.getBoundingClientRect().width/2);
		if (hover_initial_x == 0) return;
		element.style.left = `${_x}px`
	}

	let c = {
		noise:{
			css: [
				"fixed",
				"h-screen",
				"invert-100",
				"left-0",
				"m-0",
				"mix-blend-multiply",
				"opacity-80",
				"p-0",
				"point-none",
				"top-0",
				"w-screen",
				"z-100",
			]
		},
		id_middle: {
			clipper: {
				css: [
					"!-z-1",
					"!bg-none/0",
					"!blur-sm",
					"!overflow-hidden",
					"!p-0",
					"!pointer-events-none",
					"!shadow-none",
					"!top-3",
					// "!bg-opacity-0",
					// "!p-2",
				],
				hover: {
					css: [
						"-mt-[250px]",
						"absolute",
						"bg-white",
						"blur-3xl",
						"h-[500px]",
						"mix-blend-overlay",
						"rounded-full",
						"w-[100px]",
						"z-10",
						// "aspect-square",
						// "h-screen",
						// "opacity-0"
						// "w-40",
					],
				},
			},
			back_glow: {
				css: [
					"!-z-10",
					"!shadow-emerald-400",
					"!shadow-lg",
					"opacity-75",
					"pointer-events-none",
				],
			},
			input: {
				css: [
					"absolute",
					"bg-black/0",
					"h-[5vw]",
					"px-5",
					"rounded-full",
					"text-4xl",
					"text-center",
					"text-gray-100",
					"w-full",
					"z-10",
					"z-100",
					// "shadow-blue-100",
					// "shadow-md",
				],
			},
		},
	};
</script>

<svelte:window
	onmousemove={(e: MouseEvent) => {
		[x, y] = [e.x, e.y];
		// noise_freq=Math.random() * (5 - 1) + 1;
	}}
/>

<div id="noise" class={c.noise.css.join(" ")} style='background-image:url("{get_noise(noise_freq)}");'></div>

<div
	class="min-h-screen w-full grid grid-rows-[auto,1fr,auto] overflow-hidden text-gray-300]"
>
	<div class="">top</div>
	<div class="m-[20vw]" id="middle">
		<div class="relative">
			<input
				type="text"
				name=""
				id=""
				placeholder="foo"
				class={c.id_middle.input.css.concat(..."".split(" ")).join(" ")}
			/>

			<!-- inner cursor light -->
			<div class={c.id_middle.input.css
					.concat(..."!z-20 overflow-hidden !p-0 !bg-orange-900/0 ".split(" "))
					.join(" ")}
			>
				<div class={c.id_middle.input.css
					.concat(..."overflow-hidden !p-0 !bg-black/100 -top-2 !z-11 blur-xs".split(" "))
					.join(" ")}>
				</div>
				<div {@attach draggableHover} class={c.id_middle.clipper.hover.css
					.concat(..."!bg-orange-600".split(" "))
				.join(" ")}></div>
			</div>

			{@render clipped_cursor_glow()}
			<div
				id="back_glow"
				class={c.id_middle.input.css
					.concat(c.id_middle.back_glow.css)
					.join(" ")}
			>
				{@render hidden_p()}
			</div>
		</div>
	</div>
	<div class="">bottom</div>
</div>

{#snippet hidden_p()}
	<!-- <p class="opacity-0">.</p> -->
{/snippet}

{#snippet clipped_cursor_glow()}
	<div
		class={c.id_middle.input.css
			.concat(c.id_middle.clipper.css)
			.join(" ")}
	>
		{@render hidden_p()}
		<div
			{@attach draggableHover}
			use:setInitialX
			class={c.id_middle.clipper.hover.css
				.concat(..."!bg-emerald-200".split(" "))
				.join(" ")}
		></div>
	</div>
{/snippet}