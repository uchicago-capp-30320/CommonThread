<script>
	import { submitStory } from '$lib/components/story/StoryPoster.js';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { accessToken, refreshToken } from '$lib/store.js';

	let { currentStep = $bindable(), storyData = $bindable(), projects } = $props();
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
		// first get presigned link for image upload
		const presignedResponse = await authRequest(
			`/story/create`,
			'GET',
			$accessToken,
			$refreshToken
		);

		console.log('presignedResponse', presignedResponse);

		if (presignedResponse.newAccessToken) {
			accessToken.set(presignedResponse.newAccessToken);
		}

		const audio_upload = presignedResponse.data.audio_upload;
		const image_upload = presignedResponse.data.image_upload;

		// create a new FormData object
		const formAudio = new FormData();

		const formImage = new FormData();

		if (image_upload && image_upload.fields) {
			// For image upload form data
			for (const [key, value] of Object.entries(image_upload.fields)) {
				formImage.append(key, value);
			}
		}

		formImage.append('file', storyData.image);

		console.log('image_upload.url', image_upload.url);

		// upload image to S3
		const uploadResponse = await fetch(image_upload.url, {
			method: 'POST',
			headers: {
				'Content-Type': 'image/png'
			},
			body: formImage
		});

		console.log('uploadResponse', uploadResponse);

		// then submit the story
		if (uploadResponse.status !== 200) {
			error = 'Error uploading image';
		} else {
			// change tag format to match backend
			// create list of requried tags
			const requiredTags = storyData.tags.filter((tag) =>
				storyData.required_tags.includes(tag.category)
			);

			const storyDataToSubmit = {
				...storyData,
				image: image_upload.fields.key,
				audio: audio_upload.fields.key
			};

			console.log('storyDataToSubmit', storyDataToSubmit);

			await submitStory(storyDataToSubmit);
			submitted = true;
		}
		try {
			error = null;
			//const response = await submitStory(storyData);
			//submitted = true;
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
