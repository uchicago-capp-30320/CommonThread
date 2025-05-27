<script>
	import ProjectHeader from '$lib/components/ProjectHeader.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { accessToken, refreshToken } from '$lib/store.js';

	let stories = $state([]);
	let projectData = $state({
		name: 'Loading...',
		insight: 'Loading...',
		org_id: 'Loading...',
		stories: 0
	});
	let projectsTotal = $state('...');
	let themeColor = $state('#133335');
	let type = $state('dash');
	let searchValue = $state('');
	let storiesTotalSearch = $state(0);
	let isLoading = $state(true);

	const org_id = $page.params.org_id;

	$inspect(projectData);
	$inspect(stories);
	$inspect(searchValue);

	onMount(async () => {
		// Fetch the data when the component mounts
		const project_id = $page.params.project_id;

		// Make both requests concurrently using Promise.all
		const [storiesResponse, projectResponse] = await Promise.all([
			authRequest(`/stories?project_id=${project_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/project/${project_id}`, 'GET', $accessToken, $refreshToken)
		]);

		projectData = projectResponse.data;

		const loadedData = storiesResponse.data;

		if (storiesResponse.data !== null) {
			isLoading = false;
		}
		stories = loadedData['stories'];

		storiesTotalSearch = projectData.stories;
	});

	// Create a function to filter items based on search value
	function getFilteredItems() {
		if (searchValue === '') {
			return stories;
		}
		const searchTerm = searchValue.toLowerCase();
		return stories.filter((story) => story.text_content.includes(searchTerm));
	}

	// Create derived state for filtered items
	let filteredItems = $derived(getFilteredItems());

	// Update counts based on filtered items
	$effect(() => {
		storiesTotalSearch = filteredItems.length;
	});
</script>

<svelte:head>
	<title>Project Dashboard</title>
</svelte:head>

<div class="container">
	<div class="breadcrumb-nav mb-5">
		<nav class="breadcrumb nav-color" aria-label="breadcrumbs">
			<ul>
				<li><a href="/">Home</a></li>
				<li>
					<a href="/org/{projectData.org_id}"
						><b>Organization</b>: {projectData.org_name || 'Organization'}</a
					>
				</li>
				<li class="is-active">
					<a href="/org/{projectData.org_id}/project/{projectData.name}" aria-current="page"
						><b>Project</b>: {projectData.project_name}</a
					>
				</li>
			</ul>
		</nav>
	</div>
	<div class="p-5">
		<ProjectHeader
			project_name={projectData.project_name}
			insight={projectData.insight}
			stories={projectData.stories}
			org_id={projectData.org_id}
			--card-color={themeColor}
		/>
	</div>

	<div class="pt-6">
		<div class="level">
			<div class="level-left">
				<div class="level-item">
					<div class="buttons has-addons">
						<button class="button {type === 'dash' ? 'active' : ''}" onclick={() => (type = 'dash')}
							>Dashboard</button
						>
						<button
							class="button {type === 'story' ? 'active' : ''}"
							onclick={() => (type = 'story')}>Story View</button
						>
					</div>
				</div>
				<div class="level-item pl-6">
					<a href="/org/{projectData.org_id}/story/new" class="button">
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
						<strong>{storiesTotalSearch}</strong> Stories
					</p>
				</div>
				{#if type === 'story'}
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
							<p class="control">
								<button class="button">Search</button>
							</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<hr />

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
	{:else if !isLoading && stories.length !== 0}
		{#if type === 'dash'}
			<DataDashboard {stories} />
		{:else if type === 'story'}
			{#each filteredItems as story}
				<div class="">
					<StoryPreview {story} />
				</div>
			{/each}
		{/if}
	{:else}
		<div class="has-text-centered my-6">
			<p class="mb-2">No stories have been created for this project. Please create some stories.</p>
			<a href="/org/{org_id}/story/new" class="button is-primary is-small"> Create a Story</a>
		</div>
	{/if}
</div>

<style>
	.container {
		margin: 30px;
	}

	li a {
		color: black;
	}

	li.is-active {
		color: #133335 !important;
	}

	button.active {
		background-color: #133335;
		color: white;
	}
</style>
