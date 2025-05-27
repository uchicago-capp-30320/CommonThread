<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { accessToken, refreshToken } from '$lib/store.js';
	import { showError } from '$lib/errorStore.js';

	const org_id = page.params.org_id;

	let stories = $state([]);
	let projectsTotal = $state('...');
	let storiesTotal = $state('...');
	let projects = $state([]);
	let orgData = $state({
		org_id: null,
		name: 'Loading...',
		description: 'Loading...',
		profile_pic_path: 'https://bulma.io/assets/images/placeholders/96x96.png'
	});
	let themeColor = $state('#133335');
	let type = $state('project'); // or 'story', depending on your logic
	let isLoading = $state(true);

	let searchValue = $state('');

	let changeOrgs = $state([
		{
			org_id: null,
			org_name: 'Loading...'
		}
	]);

	$inspect(orgData);
	$inspect(projects);

	onMount(async () => {
		try {
			// Make both requests concurrently using Promise.all
			const [storiesResponse, orgResponse, userRequest] = await Promise.all([
				authRequest(`/stories?org_id=${org_id}`, 'GET', $accessToken, $refreshToken),
				authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
				authRequest(`/user`, 'GET', $accessToken, $refreshToken)
			]);

			// Check for org errors
			if (orgResponse?.error) {
				console.error('Error fetching organization:', orgResponse.error);
				if (orgResponse.code === 'ORG_NOT_FOUND' || orgResponse.code === 'USER_NOT_IN_ORG') {
					showError(orgResponse.error.code);
				} else {
					showError(orgResponse.error);
				}

				isLoading = false;
				return;
			}

			// Check for stories errors
			if (storiesResponse?.error) {
				showError('STORIES_NOT_FOUND');
				isLoading = false;
				return;
			}

			// Check for user errors
			if (userRequest?.error) {
				showError('USER_NOT_FOUND');
				isLoading = false;
				return;
			}

			// get project info from all projects concurrently
			const project_ids = orgResponse.data.project_ids;
			const projectPromises = project_ids.map((project_id) =>
				authRequest(`/project/${project_id}`, 'GET', $accessToken, $refreshToken)
			);
			const projectResponses = await Promise.all(projectPromises);

			// Check for project errors in responses
			for (const response of projectResponses) {
				if (response?.error) {
					showError('PROJECT_NOT_FOUND');
					isLoading = false;
					return;
				}
			}

			// Extract project data from the responses
			projects = projectResponses.map((response) => {
				return response.data;
			});

			// Sort projects by number of stories (largest to smallest)
			projects = projects.sort((a, b) => {
				// Check if projects have a stories property, otherwise use 0
				const aStories = a.stories ? a.stories : 0;
				const bStories = b.stories ? b.stories : 0;
				// Sort in descending order (largest to smallest)
				return bStories - aStories;
			});

			orgData = orgResponse.data;
			changeOrgs = userRequest.data.orgs.filter((org) => org.org_id !== org_id);

			const loadedData = storiesResponse.data;
			stories = loadedData['stories'];
			projectsTotal = new Set(stories.map((story) => story.project_id)).size;
			storiesTotal = stories.length;

			isLoading = false;
		} catch (error) {
			console.error('Unexpected error loading org page:', error);
			// showError('INTERNAL_ERROR');
			// isLoading = false;
		}
	});

	// Create a function to filter items based on search value
	function getFilteredItems() {
		if (searchValue === '') {
			if (type === 'project') {
				return projects;
			} else if (type === 'story') {
				return stories;
			}
		}

		const searchTerm = searchValue.toLowerCase();

		if (type === 'project') {
			return projects.filter((project) => project.name.toLowerCase().includes(searchTerm));
		} else if (type === 'story') {
			return stories.filter((story) => story.text_content.toLowerCase().includes(searchTerm));
		}

		return [];
	}

	// Create derived state for filtered items
	let filteredItems = $derived(getFilteredItems());

	// Update counts based on filtered items
	$effect(() => {
		if (type === 'project') {
			projectsTotal = filteredItems.length;
		} else if (type === 'story') {
			storiesTotal = filteredItems.length;
		}
	});
</script>

<svelte:head>
	<title>Org Dashboard</title>
</svelte:head>

<div class="container">
	<div class="p-5">
		<OrgHeader
			org_name={orgData.name}
			description="This is a description of my organization"
			,
			profile_pic_path={orgData.profile_pic_path}
			numProjects={projectsTotal}
			numStories={storiesTotal}
			orgs={changeOrgs}
			--card-color={themeColor}
		/>
	</div>

	<div class="pt-6">
		<div class="level">
			<div class="level-left">
				<div class="level-item">
					<div class="buttons has-addons">
						<button
							class="button {type === 'project' ? 'active' : ''}"
							onclick={() => (type = 'project')}>Project View</button
						>
						<button
							class="button {type === 'story' ? 'active' : ''}"
							onclick={() => (type = 'story')}>Story View</button
						>
					</div>
				</div>
				<div class="level-item pl-6">
					<a href="/org/{org_id}/story/new" class="button">
						<span class="icon">
							<i class="fa fa-plus"></i>
						</span>
						<span>Add Story</span>
					</a>
				</div>
			</div>
			<div class="level-right">
				<div class="level-item">
					<p class="subtitle is-5">
						<strong>{type === 'project' ? projectsTotal : storiesTotal}</strong>
						{type === 'project' ? 'Projects' : 'Stories'}
					</p>
				</div>

				<div class="level-item">
					<div class="field has-addons">
						<p class="control">
							<input
								class="input"
								type="text"
								bind:value={searchValue}
								placeholder={`Search for ${type}`}
							/>
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>

	<hr />

	<div class="container">
		{#if isLoading}
			{#each [1, 2, 3] as project}
				<div class="columns mt-4 is-multiline">
					{#each [1, 2, 3] as _}
						<div class="column is-one-third">
							<div class="skeleton-block" style="height: 250px;"></div>
						</div>
					{/each}
				</div>
			{/each}
		{:else if !isLoading && projects.length !== 0}
			{#if type === 'project'}
				<div class="columns mt-4 is-multiline">
					{#each filteredItems as project}
						<div class="column is-one-third">
							<ProjectCard {project} />
						</div>
					{/each}
				</div>
			{:else if type === 'story'}
				{#each filteredItems as story}
					<div class="mb-4">
						<StoryPreview {story} />
					</div>
				{/each}
			{/if}
		{:else}
			<div class="has-text-centered my-6">
				<p class="mb-2">
					No projects have been created for this organizations. Please create a project first before
					you can see a project.
				</p>
				<a href="/org/{org_id}/admin" class="button is-primary is-small"> Create a Project</a>
			</div>
		{/if}
	</div>
</div>

<style>
	.container {
		margin: 30px;
	}

	button.active {
		background-color: #133335;
		color: white;
	}
</style>
