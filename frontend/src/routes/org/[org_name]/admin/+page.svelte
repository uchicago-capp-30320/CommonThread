<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';

	let themeColor = $state('#133335');

	let projects = $state([
		{
			name: 'Project 1',
			description: 'Description of Project 1',
			requiredTags: ['tag1', 'tag2'],
			optionalTags: ['tag3', 'tag4'],
			isOpen: false,
			storyCount: 50,
			createdAt: '2023-01-01'
		},
		{
			name: 'Project 2',
			description: 'Description of Project 2',
			requiredTags: ['tag1', 'tag2'],
			optionalTags: ['tag3', 'tag4'],
			isOpen: false,
			storyCount: 30,
			createdAt: '2023-02-01'
		}
	]);

	$inspect(projects);
</script>

<div class="content">
	<div class="header p-6">
		<OrgHeader org_name="My Organization" --card-color={themeColor} />
	</div>
	<hr />
	<div class="container mt-5">
		<h2 class="title is-4">Projects</h2>

		<div class="mb-5">
			<button
				class="button is-primary is-medium"
				style="background-color: #56BDB3;"
				onclick={() => {
					projects = [
						...projects,
						{
							name: 'New Project',
							description: 'Description of new project',
							requiredTags: [],
							optionalTags: [],
							isOpen: true
						}
					];
				}}
			>
				<span class="icon">
					<i class="fa fa-plus"></i>
				</span>
				<span>Add New Project</span>
			</button>
		</div>

		{#each projects as project, i}
			<div class="card mb-4">
				<header class="card-header">
					<div class="card-header-title is-justify-content-space-between is-flex-wrap-wrap">
						<div class="is-flex is-flex-direction-column is-align-items-flex-start">
							<p class="mb-1 is-size-4">{project.name}</p>
							<p class="is-size-6 has-text-grey">{project.description}</p>
						</div>
						<div class="is-flex is-flex-direction-column is-align-items-flex-end">
							<p class="mb-1 is-size-5"><strong>{project.storyCount}</strong> stories</p>
							<p class="is-size-6 has-text-grey">Created: {project.createdAt}</p>
						</div>
					</div>
					<button
						class="card-header-icon is-size-5"
						aria-label="more options"
						onclick={() => (project.isOpen = !project.isOpen)}
						style="background-color: {themeColor}; color: white; border-radius: 5px;"
					>
						Edit
						<span class="icon">
							<i class="fa fa-angle-down" aria-hidden="true" class:is-rotated={project.isOpen}></i>
						</span>
					</button>
				</header>

				{#if project.isOpen}
					<div class="card-content">
						<div class="field">
							<label class="label">Project Name</label>
							<div class="control">
								<input class="input" type="text" bind:value={project.name} />
							</div>
						</div>

						<div class="field">
							<label class="label">Description</label>
							<div class="control">
								<textarea class="textarea" bind:value={project.description}></textarea>
							</div>
						</div>

						<div class="field">
							<label class="label">Required Tags</label>
							<div class="control">
								{#each project.requiredTags as tag, tagIndex}
									<div class="field has-addons mb-2">
										<div class="control is-expanded">
											<input
												class="input"
												type="text"
												bind:value={project.requiredTags[tagIndex]}
											/>
										</div>
										<div class="control">
											<button
												class="button is-danger"
												onclick={() =>
													(project.requiredTags = project.requiredTags.filter(
														(_, i) => i !== tagIndex
													))}
											>
												Remove
											</button>
										</div>
									</div>
								{/each}
								<button
									class="button is-primary is-small"
									onclick={() => (project.requiredTags = [...project.requiredTags, ''])}
								>
									Add Required Tag
								</button>
							</div>
						</div>

						<div class="field">
							<label class="label">Optional Tags</label>
							<div class="control">
								{#each project.optionalTags as tag, tagIndex}
									<div class="field has-addons mb-2">
										<div class="control is-expanded">
											<input
												class="input"
												type="text"
												bind:value={project.optionalTags[tagIndex]}
											/>
										</div>
										<div class="control">
											<button
												class="button is-danger"
												onclick={() =>
													(project.optionalTags = project.optionalTags.filter(
														(_, i) => i !== tagIndex
													))}
											>
												Remove
											</button>
										</div>
									</div>
								{/each}
								<button
									class="button is-primary is-small"
									onclick={() => (project.optionalTags = [...project.optionalTags, ''])}
								>
									Add Optional Tag
								</button>
								<div class="field is-grouped mt-4">
									<div class="control">
										<button
											class="button is-success"
											onclick={() => {
												// logic to save the project
												project.isOpen = false;
												// Example: saveProject(project);
												alert('Project saved!');
											}}
										>
											Save Changes
										</button>
									</div>
									<div class="control">
										<button class="button is-light" onclick={() => (project.isOpen = false)}>
											Cancel
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/each}
	</div>

	<style>
		.is-rotated {
			transform: rotate(180deg);
		}
	</style>
</div>
