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

	// TODO for now
	let projects = [
		{ id: 1, name: 'Project A' },
		{ id: 2, name: 'Project B' },
		{ id: 3, name: 'Project C' }
	];
</script>

<div class="box">
	<h2 class="title is-4 mb-5">Which project is this a part of?</h2>

	<div class="field">
		<label class="label" for="project">Project</label>
		<div class="control">
			<div class="select is-fullwidth">
				<select id="project" bind:value={storyData.project}>
					<option value="" disabled selected>Choose the project name</option>
					{#each projects as project}
						<option value={project.id}>{project.name}</option>m
					{/each}

					<!-- Add more options as needed -->
				</select>
			</div>
		</div>
	</div>

	<h2 class="title is-4 mb-5 mt-5">Tell us about you and the storyteller</h2>

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
