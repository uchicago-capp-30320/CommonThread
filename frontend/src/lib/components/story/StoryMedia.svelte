<script>
	import { submitStory } from '$lib/components/story/StoryPoster.js';
	let { currentStep = $bindable(), storyData = $bindable() } = $props();
	let imagePreview = $state(storyData.image ? URL.createObjectURL(storyData.image) : null);
	let submitted = $state(false);
	let error = $state(null);

	function handleFileChange(event) {
		const file = event.target.files[0];
		if (file) {
			storyData = { ...storyData, image: file };
			imagePreview = URL.createObjectURL(file);
		}
	}

	function removeImage() {
		storyData = { ...storyData, image: null };
		imagePreview = null;
	}

	async function handleSubmit() {
		try {
			error = null;
			const response = await submitStory(storyData);
			submitted = true;
		} catch (err) {
			error = err.message;
		}
	}

	$inspect(storyData);
</script>

{#if !submitted}
	<div class="box">
		<h2 class="title is-4 mb-5">Add an Image</h2>

		<div class="field">
			<label class="label" for="story-image">Upload Image</label>
			<div class="control">
				<input
					id="story-image"
					class="input"
					type="file"
					accept="image/*"
					onchange={handleFileChange}
				/>
			</div>
		</div>

		{#if imagePreview}
			<div class="field mt-4">
				<div class="label">Preview</div>
				<figure class="image is-128x128">
					<img src={imagePreview} alt="Story preview" />
				</figure>
				<button class="button is-danger is-small mt-2" onclick={removeImage}>Remove Image</button>
			</div>
		{/if}

		{#if error}
			<div class="notification is-danger">
				{error}
			</div>
		{/if}

		<div class="field mt-5 is-flex is-justify-content-flex-end">
			<div class="control">
				<button class="button is-primary" onclick={handleSubmit}> Submit </button>
			</div>
		</div>
	</div>
{:else}
	<div class="field mt-5">
		<h2 class="title is-4 mb-4">Story submitted</h2>
		<p>Thank you for sharing</p>
	</div>
{/if}
