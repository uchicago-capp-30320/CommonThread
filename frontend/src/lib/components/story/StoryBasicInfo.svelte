<script>
	let { currentStep = $bindable(), storyData = $bindable(), projects } = $props();

	function handleNext() {
		console.log('Before click - currentStep:', currentStep);
		console.log('Data check:', storyData.storyteller);

		if (storyData.storyteller) {
			currentStep = 2;
			console.log('After click - currentStep:', currentStep);
		}
	}

	let loaded = $derived(projects[0].project_name !== 'Loading...');
</script>

<div class="box">
	{#if projects.length === 0}
		<p class="mb-2">
			No projects have been created for this organizations. Please create a project first before you
			can add a project.
		</p>
		<a href="/org/{storyData.org_id}/admin" class="button is-primary is-small">
			Create a Project
		</a>
	{:else if !loaded}
		<p class="mb-2">Loading...</p>
	{:else if loaded}
		<h2 class="title is-4 mb-5">Which project is this a part of?</h2>

		<div class="field">
			<label class="label" for="project">Project</label>
			<div class="control">
				<div class="select is-fullwidth">
					<select id="project" bind:value={storyData.project_id}>
						<option value="" disabled selected>Choose the project name</option>
						{#each projects as project}
							<option value={project.project_id}>{project.project_name}</option>m
						{/each}

						<!-- Add more options as needed -->
					</select>
				</div>
			</div>
		</div>

		<h2 class="title is-4 mb-5 mt-5">Tell us about you and the storyteller</h2>

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
	{/if}
</div>
