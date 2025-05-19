<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import { accessToken, refreshToken } from '$lib/store.js';
	import { onMount } from 'svelte';
	import { authRequest } from '$lib/authRequest.js';
	import { page } from '$app/stores';

	let themeColor = $state('#133335');
	let saveResponse = $state('...');
	let orgData = $state({
		orgName: 'Loading...',
		description: 'Loading...',
		projectsTotal: 0,
		storiesTotal: 0
	});
	let userData = $state({
		name: 'Loading...',
		email: 'Loading...',
		data_added: 'Loading...'
	});
	let projects = $state([]);
	let projectResponses = $state([]);

	$inspect(projects);
	$inspect(userData);
	$inspect(orgData);

	const org_id = $page.params.org_id;

	// get project data from the backend
	onMount(async () => {
		const orgResponse = await authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken);

		orgData = orgResponse.data;
		userData = orgData.users;

		const project_ids = orgData.project_ids;

		// get project info from all projects concurrently

		const projectPromises = project_ids.map((project_id) =>
			authRequest(`/project/${project_id}`, 'GET', $accessToken, $refreshToken)
		);

		projectResponses = await Promise.all(projectPromises);

		// Extract project data from the responses
		projects = projectResponses.map((response) => {
			const project = response.data;
			return {
				...project,
				isOpen: false
			};
		});
	});

	let totalUsers = $derived(userData.length);

	// async function editProject(project) {
	// 	// logic to edit the project
	//
	// 	saveResponse = await authRequest(
	// 		'/api/projects/edit',
	// 		'POST',
	// 		$accessToken,
	// 		$refreshToken,
	// 		project
	// 	);
	// 	console.log('Project edited:', saveResponse);
	// }

	//$inspect(projects);
</script>

<div class="content">
	<div class="header p-6">
		<OrgHeader
			org_name={orgData.name}
			description={orgData.description}
			numProjects={orgData.project_count}
			numStories={orgData.story_count}
			--card-color={themeColor}
		/>
	</div>
	<hr />
	<div class="container mt-5">
		<h2 class="title is-4">Users ({totalUsers})</h2>

		<div class="mb-5">
			<div class="field has-addons">
				<div class="control is-expanded" style="max-width: 25%;">
					<input class="input" type="text" placeholder="Enter email address" id="newUserEmail" />
				</div>
				<div class="control">
					<button
						class="button is-primary"
						style="background-color: #56BDB3;"
						onclick={() => {
							const email = document.getElementById('newUserEmail').value;
							if (email) {
								users = [
									{
										name: 'New User',
										email: email,
										data_added: new Date().toISOString().split('T')[0]
									},
									...users
								];
								document.getElementById('newUserEmail').value = '';
							}
						}}
					>
						<span class="icon">
							<i class="fa fa-plus"></i>
						</span>
						<span>Add User</span>
					</button>
				</div>
			</div>

			<div class="table-container">
				<table class="table is-fullwidth is-striped is-hoverable">
					<thead>
						<tr>
							<th>Name</th>
							<th>Email</th>
							<th>Date Added</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each userData as user, i}
							<tr>
								<td>
									{user.name}
								</td>
								<td>
									{user.email}
								</td>
								<td>1/1/2024</td>
								<td>
									<div class="buttons">
										<button
											class="button is-small is-danger"
											onclick={() => {
												users = users.filter((_, index) => index !== i);
											}}
										>
											Remove
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<hr />

			<h2 class="title is-4">Projects</h2>

			<div class="mb-5">
				<button
					class="button is-primary is-medium"
					style="background-color: #56BDB3;"
					onclick={() => {
						projects = [
							{
								name: 'New Project',
								description: 'Description of new project',
								requiredTags: [],
								optionalTags: [],
								isOpen: true
							},
							...projects
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
								<p class="mb-1 is-size-4">{project.project_name}</p>
								<p class="is-size-6 has-text-grey">{project.insight}</p>
							</div>
							<div class="is-flex is-flex-direction-column is-align-items-flex-end">
								<p class="mb-1 is-size-5"><strong>{project.stories}</strong> stories</p>
								<p class="is-size-6 has-text-grey">Created: {project.date}</p>
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
								<i class="fa fa-angle-down" aria-hidden="true" class:is-rotated={project.isOpen}
								></i>
							</span>
						</button>
					</header>

					{#if project.isOpen}
						<div class="card-content">
							<div class="field">
								<label class="label">Project Name</label>
								<div class="control">
									<input class="input" type="text" bind:value={project.project_name} />
								</div>
							</div>

							<div class="field">
								<label class="label">Description</label>
								<div class="control">
									<textarea class="textarea" bind:value={project.insight}></textarea>
								</div>
							</div>

							<div class="field">
								<label class="label">Required Tags</label>
								<div class="control">
									{#each project.required_tags as tag, tagIndex}
										<div class="field has-addons mb-2">
											<div class="control is-expanded">
												<input
													class="input"
													type="text"
													bind:value={project.required_tags[tagIndex]}
												/>
											</div>
											<div class="control">
												<button
													class="button is-danger"
													onclick={() =>
														(project.required_tags = project.required_tags.filter(
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
										onclick={() => (project.required_tags = [...project.required_tags, ''])}
									>
										Add Required Tag
									</button>
								</div>
							</div>

							<div class="field">
								<label class="label">Optional Tags</label>
								<div class="control">
									{#each project.optional_tags as tag, tagIndex}
										<div class="field has-addons mb-2">
											<div class="control is-expanded">
												<input
													class="input"
													type="text"
													bind:value={project.optional_tags[tagIndex]}
												/>
											</div>
											<div class="control">
												<button
													class="button is-danger"
													onclick={() =>
														(project.optional_tags = project.optional_tags.filter(
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
										onclick={() => (project.optional_tags = [...project.optional_tags, ''])}
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
													editProject(project);
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
	</div>

	<style>
		.is-rotated {
			transform: rotate(180deg);
		}
	</style>
</div>
