<script lang="ts">
	import { elementRoles } from "aria-query";
	import type { Action } from "svelte/action";
    import type { Attachment } from "svelte/attachments";
	let z: Map<number, HTMLElement> = new Map();
	// let z: Set<HTMLElement> = new Set();
	let x = $state(0);
	let y = $state(0);

	let hover_initial_x: number = 0;

	let noise_freq = $state(0.2);
	// let noise = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><filter id='noiseFilter'><feTurbulence type='fractalNoise' baseFrequency='${noise_freq}' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23noiseFilter)'/></svg>`
	let noise = (f: number) => {
		return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><filter id='noiseFilter'><feTurbulence type='fractalNoise' baseFrequency='${f}' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23noiseFilter)'/></svg>`;
	};

	let noise2 = (f: number) => {
		return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' version='1.1' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:svgjs='http://svgjs.dev/svgjs' viewBox='0 0 700 700' width='700' height='700' opacity='1'%3E%3Cdefs%3E%3Cfilter id='nnnoise-filter' x='-20%25' y='-20%25' width='140%25' height='140%25' filterUnits='objectBoundingBox' primitiveUnits='userSpaceOnUse' color-interpolation-filters='linearRGB'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='${f}' numOctaves='4' seed='15' stitchTiles='stitch' x='0%25' y='0%25' width='100%25' height='100%25' result='turbulence'%3E%3C/feTurbulence%3E%3CfeSpecularLighting surfaceScale='11' specularConstant='3' specularExponent='20' lighting-color='%23ffffff' x='0%25' y='0%25' width='100%25' height='100%25' in='turbulence' result='specularLighting'%3E%3CfeDistantLight azimuth='3' elevation='98'%3E%3C/feDistantLight%3E%3C/feSpecularLighting%3E%3CfeColorMatrix type='saturate' values='0' x='0%25' y='0%25' width='100%25' height='100%25' in='specularLighting' result='colormatrix'%3E%3C/feColorMatrix%3E%3C/filter%3E%3C/defs%3E%3Crect width='700' height='700' fill='transparent'%3E%3C/rect%3E%3Crect width='700' height='700' fill='%23ffffff' filter='url(%23nnnoise-filter)'%3E%3C/rect%3E%3C/svg%3E`;
	};

	let t = setInterval(() => {
		let n = Math.random() * (1.1 - 0.9) + 0.9;
		noise_freq *= n;
	}, 1000 / 6);

	clearInterval(t);

	function get_noise(freq: number) {
		return noise(freq);
	}

	function get_noise_url(freq: number){
		return `url("${get_noise(freq)}")`
	}

	const setInitialX: Action<HTMLDivElement, any, any> = (
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
				if(!(cls[0] == 'z' || (cls[0] == "!" && cls[1] == "z"))) continue;
				let index: string | undefined = cls.split("-")[1];
				if (index === undefined){
					console.error(element);
					throw new Error("Couldn't find tailwind index class");
				}
				_z = index;
				break;
			}
			if(_z == "") return
			// console.log("skipping", element.classList)
		}
		let zindex: number  = parseInt(_z);
		if (Number.isNaN(zindex)){
			throw new Error("Error parsing index");
		}
		z.set(zindex, element);
		console.log(z)
	};

	function draggableHover(element: HTMLElement) {
		let _x =
			x - hover_initial_x - element.getBoundingClientRect().width / 2;
		if (hover_initial_x == 0) return;
		element.style.left = `${_x}px`;
	}

	function cn(class_array: string[], class_names?: string): string;
	function cn(class_array: string[][], class_names?: string): string;
	function cn(
		class_array: string[][] | string[],
		class_names?: string,
	): string {
		return `${class_array.flat().join(" ")} ${class_names || ""}`;
	}

	let c = {
		noise: {
			css: [
				"fixed",
				"h-screen",
				// "invert-100",
				"left-0",
				"m-0",
				// "mix-blend-luminosity",
				"mix-blend-overlay",
				"opacity-0",
				"p-0",
				"point-none",
				"top-0",
				"w-screen",
			],
		},
		id_middle: {
			clipper: {
				css: [
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
						"blur-xl",
						"h-[500px]",
						"mix-blend-overlay",
						"rounded-full",
						"w-[100px]",
						// "aspect-square",
						// "h-screen",
						// "opacity-0"
						// "w-40",
					],
				},
			},
			back_glow: {
				css: [
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
					// "text-4xl",
					"text-center",
					"text-gray-100",
					"w-full",
					"shadow-blue-100",
					"shadow-md",
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

<div
	id="noise"
	class={cn(c.noise.css, "z-90")}
	{@attach addToZ}
	style='background-image:url("{get_noise(noise_freq)}");'
></div>

<div {@attach addToZ}
	class="min-h-screen w-full grid grid-rows-[auto,1fr,auto] overflow-hidden text-gray-300]"
>
	<div class="">top</div>
	<div id="middle" class="m-[20vw] [font-size:_clamp(1em,5vw,10em)]">
		<div class="relative">
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
				id="inner_light_container"
				{@attach addToZ}
				class={cn(
					c.id_middle.input.css,
					"z-50 overflow-hidden !p-0 !bg-orange-900/0 !shadow-none blur-xs",
				)}
			>
				<div
					id="inner_light_mask"
					{@attach addToZ}
					class={cn(
						c.id_middle.input.css,
						"overflow-hidden !p-0 !bg-black/100 -top-[0.5vw] !shadow-none",
					)}
				></div>
				<div
					id="inner_light_highlight"
					{@attach addToZ}
					{@attach draggableHover}
					class={cn(c.id_middle.clipper.hover.css, "!bg-orange-800 !shadow-none")}
				></div>
			</div>
			<!-- / inner cursor light -->

				<div class="relative w-100 aspect-square overflow-hidden">
					<div class="w-full h-full object-cover radial-noise" style="--noise: {get_noise_url(0.2)}"></div>

					<!-- Feathered overlay using after pseudo-element -->
					<!-- <div class="absolute inset-0 pointer-events-none
								after:content-[''] after:absolute after:inset-0
								after:bg-gradient-to-b after:from-transparent after:to-white">
					</div> -->
				</div>

				<!-- <div
					id="input-noise"
					{@attach addToZ}
					class={cn(
						c.id_middle.input.css,
						"!shadow-none radial-noise scale-y-115 scale-x-102 !mt-[0.5vw] z-40 mix-blend-overlay opacity-50",
					)}
					style='--noise: url("{get_noise(0.2)}")'
				></div> -->

			<!-- background cursor light -->
			 {@render div("foo", cn(c.id_middle.input.css, "!bg-black z-30"))}
			<div class={cn([c.id_middle.input.css, c.id_middle.clipper.css])}>
				<div
					{@attach draggableHover}
					use:setInitialX
					{@attach addToZ}
					style='--noise: url("{get_noise(0.2)}")'
					class={cn(c.id_middle.clipper.hover.css, "!bg-emerald-200 z-20")}
				></div>
			</div>

			<!-- background-glow -->
			{@render div(
				"back_glow",
				cn([c.id_middle.input.css, c.id_middle.back_glow.css]),
			)}
		</div>
	</div>
	<div class="">bottom</div>
</div>

{#snippet div(id: string, classes: string)}
	<div {id} class={classes} {@attach addToZ}></div>
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
			radial-gradient(circle at center, rgb(255,255,255) 0%, rgba(0,0,0,1) 50%);
		background-size: cover;	
		background-blend-mode: multiply;
		mix-blend-mode: screen;
	}
</style>
