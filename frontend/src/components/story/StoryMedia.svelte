<script>
	let { currentStep = $bindable(), storyData = $bindable() } = $props();
	let imagePreview = $state(storyData.image ? URL.createObjectURL(storyData.image) : null);
	let submitted = $state(false);

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

	function handleSubmit() {
        console.log(storyData);
		submitted = true;
	}
</script>

{#if !submitted}
	<div class="box">
		<h2 class="title is-4 mb-5">Add an Image</h2>

		<div class="field">
			<label class="label">Upload Image</label>
			<div class="control">
				<input class="input" type="file" accept="image/*" onchange={handleFileChange} />
			</div>
		</div>

		{#if imagePreview}
			<div class="field mt-4">
				<label class="label">Preview</label>
				<figure class="image is-128x128">
					<img src={imagePreview} alt="Story image preview" />
				</figure>
				<button class="button is-danger is-small mt-2" onclick={removeImage}>Remove Image</button>
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
