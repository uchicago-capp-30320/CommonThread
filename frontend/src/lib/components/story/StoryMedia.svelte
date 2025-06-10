<script>
	import { submitStory } from '$lib/components/story/StoryPoster.js';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { accessToken, refreshToken } from '$lib/store.js';

	let { currentStep = $bindable(), storyData = $bindable(), projects } = $props();
	let imagePreview = $state(storyData.image ? URL.createObjectURL(storyData.image) : null);
	let submitted = $state(false);
	let error = $state(null);
	let isUploading = $state(false);
	
	// Camera stuff
	let showCamera = $state(false);
	let stream = $state(null);

	let project = $derived(
		projects.filter((project) => project.project_id === storyData.project_id)[0]
	);

	let storyDataToSubmit = $state({ ...storyData });

	$inspect(project);
	$inspect(storyData);
	$inspect(storyDataToSubmit);

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
		stopCamera();
	}

	async function startCamera() {
		try {
			console.log('Requesting camera permission...');
			stream = await navigator.mediaDevices.getUserMedia({ 
				video: { facingMode: 'user' } 
			});
			console.log('Camera permission granted, showing video...');
			showCamera = true;
			error = null;
			
			// Wait for DOM update then connect stream
			setTimeout(() => {
				const video = document.getElementById('camera-video');
				if (video) {
					video.srcObject = stream;
					console.log('Video connected successfully');
				}
			}, 50);
			
		} catch (err) {
			console.error('Camera error details:', err.name, err.message);
			if (err.name === 'NotAllowedError') {
				error = 'Please allow camera access in your browser';
			} else if (err.name === 'NotFoundError') {
				error = 'No camera found on this device';
			} else {
				error = `Camera error: ${err.message}`;
			}
		}
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
			stream = null;
		}
		showCamera = false;
	}

	function takePhoto() {
		const video = document.getElementById('camera-video');
		if (!video) return;
		
		const canvas = document.createElement('canvas');
		canvas.width = video.videoWidth;
		canvas.height = video.videoHeight;
		const ctx = canvas.getContext('2d');
		ctx.drawImage(video, 0, 0);
		
		canvas.toBlob((blob) => {
			const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
			storyData = { ...storyData, image: file };
			imagePreview = URL.createObjectURL(file);
			stopCamera();
		});
	}

	async function handleSubmit() {
		// first get presigned link for image upload

		if (storyData.image || storyData.audio) {
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

			// if image
			if (storyData.image) {
				const image_upload = presignedResponse.data.image_upload;
				const formImage = new FormData();

				if (image_upload && image_upload.fields) {
					// For image upload form data
					for (const [key, value] of Object.entries(image_upload.fields)) {
						formImage.append(key, value);
					}
				}
				formImage.append('acl', 'private');
				formImage.append('file', storyData.image);

				// upload image to S3
				const imageUploadResponse = await fetch(image_upload.url, {
					method: 'POST',
					body: formImage
				});

				console.log('imageUploadResponse', imageUploadResponse);

				if (imageUploadResponse.ok) {
					console.log('Image uploaded successfully');
					storyDataToSubmit = {
						...storyDataToSubmit,
						image_path: image_upload.fields.key
					};
				} else {
					console.error('Error uploading image:', imageUploadResponse.statusText);
					error = 'Error uploading image';
				}
			}

			if (storyData.audio) {
				const audio_upload = presignedResponse.data.audio_upload;
				const formAudio = new FormData();

				if (audio_upload && audio_upload.fields) {
					// For audio upload form data
					for (const [key, value] of Object.entries(audio_upload.fields)) {
						formAudio.append(key, value);
					}
				}
				formAudio.append('acl', 'private');
				formAudio.append('file', storyData.audio);

				// upload audio to S3
				const audioUploadResponse = await fetch(audio_upload.url, {
					method: 'POST',
					body: formAudio
				});

				console.log('audioUploadResponse', audioUploadResponse);

				if (audioUploadResponse.ok) {
					console.log('Audio uploaded successfully');
					storyDataToSubmit = {
						...storyDataToSubmit,
						audio_path: audio_upload.fields.key
					};
				} else {
					console.error('Error uploading audio:', audioUploadResponse.statusText);
				}
			}
		}

		// change tag format to match backend
		// Extract categories from storyData.tags and check if they are required
		if (projects && storyData.tags) {
			console.log('fix tag format');
			storyDataToSubmit = {
				...storyDataToSubmit,
				required_tags: storyData.tags
					.filter((tag) => project.required_tags.includes(tag.category))
					.map((tag) => ({ name: tag.category, value: tag.value })),
				optional_tags: storyData.tags
					.filter((tag) => project.optional_tags.includes(tag.category))
					.map((tag) => ({ name: tag.category, value: tag.value }))
			};
		}

		// remove image/ audio from storyDataToSubmit for less data transfer
		delete storyDataToSubmit.image;
		delete storyDataToSubmit.audio;

		const uploadStory = authRequest(
			`/story/create`,
			'POST',
			$accessToken,
			$refreshToken,
			storyDataToSubmit
		);
		isUploading = true;

		const uploadResponse = await uploadStory;

		console.log('uploadStory', uploadResponse);

		if (uploadResponse.data) {
			submitted = true;
		}
	}
</script>

{#if !submitted}
	<div class="box">
		<h2 class="title is-4 mb-5">Add an Image</h2>

		{#if !imagePreview}
			<div class="field">
				<label class="label">Upload Image</label>
				<div class="control">
					<input
						class="input"
						type="file"
						accept="image/*"
						onchange={handleFileChange}
					/>
				</div>
			</div>

			<div class="has-text-centered my-4">
				<span class="has-text-grey">or</span>
			</div>

			<div class="field">
				<label class="label">Take Photo</label>
				<div class="control">
					{#if !showCamera}
						<button class="button is-primary is-fullwidth" onclick={startCamera}>
							Use Camera
						</button>
					{/if}
				</div>
			</div>
		{/if}

		{#if showCamera}
			<div class="field">
				<label class="label">Camera</label>
				<video 
					id="camera-video"
					autoplay 
					playsinline 
					muted
					class="camera-preview"
				></video>
				<div class="field mt-3">
					<div class="control">
						<button class="button is-success is-fullwidth" onclick={takePhoto}>
							Capture Photo
						</button>
					</div>
					<div class="control mt-2">
						<button class="button is-light is-fullwidth" onclick={stopCamera}>
							Cancel
						</button>
					</div>
				</div>
			</div>
		{/if}

		{#if imagePreview}
			<div class="field">
				<label class="label">Preview</label>
				<figure class="image is-128x128">
					<img src={imagePreview} alt="Preview" />
				</figure>
				<button class="button is-danger is-small mt-2" onclick={removeImage}>
					Remove Image
				</button>
			</div>
		{/if}

		{#if error}
			<div class="notification is-danger">
				{error}
			</div>
		{/if}

		{#if !isUploading}
			<div class="field mt-5 is-flex is-justify-content-flex-end">
				<div class="control">
					<button class="button is-primary" onclick={handleSubmit}>Submit</button>
				</div>
			</div>
		{:else}
			<div class="field mt-5">
				<p class="help">Submitting your story...</p>
			</div>
		{/if}
	</div>
{:else}
	<div class="field mt-5">
		<h2 class="title is-4 mb-4">Story submitted</h2>
		<p>Thank you for sharing your story!</p>
		<div class="mt-4">
			<a href="/org/{$page.params.org_id}" class="button is-primary">
				Return to Organization Homepage
			</a>
		</div>
	</div>
{/if}

<style>
	.camera-preview {
		width: 100%;
		max-width: 400px;
		border-radius: 6px;
		border: 1px solid #dbdbdb;
	}
</style>
