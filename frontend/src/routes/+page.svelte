<script>
	import background_texture from '$lib/assets/background_texture.png';
	import thread1 from '$lib/assets/illustrations/thread1.png';
	import thread2 from '$lib/assets/illustrations/thread2.png';
	import thread3 from '$lib/assets/illustrations/thread3.png';
	import { slide } from 'svelte/transition';
	import { onMount, onDestroy } from 'svelte';

	let greetings = ['Connection', 'Change', 'Community', 'Impact', 'Growth'];
	let index = $state(0);
	let roller;

	onMount(() => {
		roller = setInterval(() => {
			if (index === greetings.length - 1) index = 0;
			else index++;
		}, 3000);
	});

	onDestroy(() => {
		clearInterval(roller);
	});
</script>

<svelte:head>
	<title>Common Thread</title>
</svelte:head>

<div id="container">
	<div class="banner">
		<img src={background_texture} alt="" />
		<div class="container-content">
			<div class="welcome-text">
				<p>Weaving Together <br />Your Stories for</p>
				{#key index}
					<p class="rotate" transition:slide>{greetings[index]}</p>
				{/key}
			</div>
			<div class="welcome-image">
				<img src={thread1} alt="Thread illustration 1" />
				<img src={thread3} alt="Thread illustration 3" />
			</div>
		</div>
	</div>
</div>

<style>
	.banner {
		/* height: 600px;
		z-index: -1;
		position: relative;
		overflow: hidden; */
		height: 85vh; /*vw 	Relative to 1% of the width of the viewport*/
		z-index: -1;
		position: relative;
		overflow: hidden;
	}

	.banner img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.container-content {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 5%;
	}

	.welcome-text {
		flex: 1;
		font-size: 4rem;
		color: #fff;
		width: 500px;
		line-height: normal;
	}

	.welcome-text p {
		margin: 0;
	}

	.rotate {
		transition: transform 0.5s ease-in-out;
		font-style: italic;
		color: var(--green);
		font-weight: bold;
	}
	.welcome-image {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.welcome-image img {
		height: 40%;
		max-height: 300px;
		width: auto;
		margin: 0 10px;
	}
</style>
