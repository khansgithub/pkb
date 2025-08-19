<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	let x = $state(0);
	let y = $state(0);

	function captureMouse(e: MouseEvent) {
		// console.log("x: ", e.x, "y: ", e.y);
		x = e.x
		y = e.y
		console.log("x: ", x, "y: ", y);

	}

</script>

<svelte:window onmousemove={captureMouse} />

<div
	class="
	fixed
	w-20
	-m-10
	aspect-square
	rounded-full
	-z-10
	bg-white
	blur-2`xl
	"
	id="circle"
	style="left: {x}px; top: {y}px;"
></div>
	<!-- bg-radial from-white from-0% to-gray-900 to-60% -->

<div class=" min-h-screen w-full grid grid-rows-[auto,1fr,auto]">
	<div class="">top</div>
	<div class="m-20">
		middle
		<br />
		<div class="relative">
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
