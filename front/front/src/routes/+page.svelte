<script lang="ts">
	let x = $state(0);
	let y = $state(0);
	let circleClip: HTMLDivElement | null = null;

	function captureMouse(e: MouseEvent) {
		// console.log("x: ", e.x, "y: ", e.y);
		[x, y] = [e.x, e.y];

		if (circleClip != null){
			let clipper_x = circleClip.getBoundingClientRect().x
			let clipper_y = circleClip.getBoundingClientRect().y

			x -= clipper_x;
			y -= clipper_y;
			console.log("x: ", x, "y: ", y);
			// console.log()
			console.log("clipper_x: ", clipper_x, "clipper_y: ", clipper_y);
		}
		console.log("x: ", x, "y: ", y);
	}
</script>

<svelte:window onmousemove={captureMouse} />

<!-- bg-radial from-white from-0% to-gray-900 to-60% -->

<div class=" min-h-screen w-full grid grid-rows-[auto,1fr,auto]">
	<div class="">top</div>
	<div class="m-20">
		middle
		<br />
		<div class="relative">
			<div
				bind:this={circleClip}
				class="
				absolute
				left-0
				-top-2
				p-2
				w-full
				blur-lg
				bg-none
				rounded-full
				-z-10
				text-4xl
				pointer-events-none
				overflow-clip
			"
			>
				<p class="opacity-0">.</p>
				<div class="w-full h-full bg-pink absolute top-0 left-0"></div>
				<div
					class="
						absolute
						w-40
						-m-20
						aspect-square
						rounded-full
						-z-10
						bg-white
						blur-xl
						"
					id="circle"
					style="left: {x}px; top: {y}px;"
				></div>
			</div>

			<div
				class="
				absolute
				left-0
				w-full
				shadow-lg
				shadow-emerald-400
				rounded-full
				text-4xl
				text-gray-100
				px-5
				z-10
				pointer-events-none
				opacity-75
			"
			>
				<p class="opacity-0">.</p>
			</div>
			<input
				type="text"
				name=""
				id=""
				placeholder="foo"
				class="
				absolute
				w-full
				shadow-md
				shadow-blue-100
				rounded-full
				text-4xl
				text-gray-100
				px-5
				z-0
			"
			/>
		</div>
	</div>
	<div class="">bottom</div>
</div>
