<script>
	let { currentStep = $bindable(), storyData = $bindable() } = $props();

	function handleNext() {
		console.log('Before click - currentStep:', currentStep);
		console.log('Data check:', storyData.author, storyData.storyteller);

		if (storyData.author && storyData.storyteller) {
			currentStep = 2;
			console.log('After click - currentStep:', currentStep);
		}
	}
</script>

<div class="box">
	<h2 class="title is-4 mb-5">Tell us about you and the storyteller</h2>

	<div class="field">
		<label class="label" for="title">Author's name</label>
		<div class="control">
			<input
				class="input"
				type="text"
				id="title"
				bind:value={storyData.author}
				placeholder="Enter the author's name"
			/>
		</div>
	</div>

	<div class="field">
		<label class="label" for="author">Storyteller Name</label>
		<div class="control">
			<input
				class="input"
				type="text"
				id="author"
				bind:value={storyData.storyteller}
				placeholder="Enter name of the person whose story it is"
			/>
		</div>
	</div>

	<div class="field mt-5 is-flex is-justify-content-flex-end">
		<div class="control">
			<button class="button is-primary" onclick={handleNext}> Next </button>
		</div>
	</div>
</div>
