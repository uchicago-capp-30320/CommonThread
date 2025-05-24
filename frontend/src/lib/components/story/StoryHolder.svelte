<script>
	import StoryBasicInfo from './StoryBasicInfo.svelte';
	import StoryDetails from './StoryDetails.svelte';
	import StoryMedia from './StoryMedia.svelte';

	let { projects } = $props();

	let currentStep = $state(1);
	let storyData = $state({
		storyteller: '',
		author: '',
		project: '',
		text_content: '',
		tags: [],
		image: null,
		audio: null,
		proj_id: '',
		audio_path: null,
		image_path: null
	});

	$inspect(storyData);

	function handleStepClick(step) {
		if (step < currentStep || canNavigateToStep(step)) {
			currentStep = step;
		}
	}

	function canNavigateToStep(step) {
		switch (step) {
			case 2:
				return storyData.storyteller && storyData.author;
			case 3:
				return (
					storyData.storyteller && storyData.author && (storyData.text_content || storyData.audio)
				);
			default:
				return false;
		}
	}
</script>

<div class="container">
	<!-- Hero section for title -->
	<section class="hero has-background-dark-blue is-small mb-5">
		<div class="hero-body">
			<p class="title has-text-white">Create Your Story</p>
			<p class="subtitle has-text-white">Share your narrative with the world</p>
		</div>
	</section>

	<!-- Progress navigation -->
	<div class="columns is-centered mb-6">
		<div class="column is-8">
			<nav class="level">
				<div class="level-item has-text-centered">
					<button
						class="step-box has-text-white"
						class:is-active={currentStep === 1}
						onclick={() => handleStepClick(1)}
					>
						<p class="heading has-text-white has-text-weight-bold">Step 1</p>
						<p class="title is-5 has-text-white has-text-weight-bold">Basic Info</p>
					</button>
				</div>
				<div class="level-item has-text-centered">
					<button
						class="step-box has-text-white"
						class:is-active={currentStep === 2}
						onclick={() => handleStepClick(2)}
					>
						<p class="heading has-text-white has-text-weight-bold">Step 2</p>
						<p class="title is-5 has-text-white has-text-weight-bold">Content</p>
					</button>
				</div>
				<div class="level-item has-text-centered">
					<button
						class="step-box has-text-white"
						class:is-active={currentStep === 3}
						onclick={() => handleStepClick(3)}
					>
						<p class="heading has-text-white has-text-weight-bold">Step 3</p>
						<p class="title is-5 has-text-white has-text-weight-bold">Media</p>
					</button>
				</div>
			</nav>
		</div>
	</div>

	<!-- Form content -->
	<div class="columns is-centered">
		<div class="column is-8">
			<div class="box">
				<pre>Current Step: {currentStep}</pre>
				{#if currentStep === 1}
					<StoryBasicInfo bind:currentStep bind:storyData {projects} />
				{:else if currentStep === 2}
					<StoryDetails bind:currentStep bind:storyData {projects} />
				{:else if currentStep === 3}
					<StoryMedia bind:currentStep bind:storyData {projects} />
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.step-box {
		padding: 1rem;
		border-radius: 6px;
		color: white;
		transition: all 0.3s ease;
		border: 2px solid white;
		width: 150px;
		cursor: pointer;
	}

	.step-box.is-active {
		border-color: white;
		background-color: #56bcb3;
		color: var(--white);
		box-shadow: 0 2px 15px rgba(19, 51, 53, 0.2);
	}

	.step-box:not(.is-active) {
		opacity: 0.7;
		color: var(--white);
	}

	.step-box:not(.is-active):hover {
		opacity: 0.9;
		transform: translateY(-2px);
		background-color: var(--light-blue);
	}

	.step-box .heading {
		text-transform: uppercase;
		letter-spacing: 1px;
		font-size: 0.8rem;
		margin-bottom: 0.5rem;
	}

	.level-item:not(:last-child)::after {
		content: '';
		position: absolute;
		top: 50%;
		right: -25%;
		width: 50%;
		height: 2px;
		background-color: var(--white);
		z-index: -1;
	}

	/* Animation for transitions */
	.box {
		animation: fadeIn 0.3s ease-in-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Add visual feedback for clickable/non-clickable states */
	.step-box {
		cursor: pointer;
	}

	.step-box:not(.is-active):not(:hover) {
		opacity: 0.7;
	}
</style>
