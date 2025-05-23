<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import StoryCard from '$lib/components/StoryCard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { accessToken, refreshToken } from '$lib/store.js';

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

	let searchValue = $state('');

	let changeOrgs = $state([
		{
			org_id: null,
			org_name: 'Loading...'
		}
	]);

	$inspect(orgData);

	onMount(async () => {
		// Fetch the data when the component mounts

		// Make both requests concurrently using Promise.all
		const [storiesResponse, orgResponse, userRequest] = await Promise.all([
			authRequest(`/stories?org_id=${org_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/user`, 'GET', $accessToken, $refreshToken)
		]);

		console.log('orgResponse', orgResponse.data);

		orgData = orgResponse.data;

		changeOrgs = userRequest.data.orgs.filter((org) => org.org_id !== org_id);

		if (storiesResponse.newAccessToken) {
			accessToken.set(storiesResponse.newAccessToken);
		}

		const loadedData = storiesResponse.data;

		stories = loadedData['stories'];
		projectsTotal = new Set(stories.map((story) => story.project_id)).size;
		storiesTotal = stories.length;

		// Group stories by project_id
		const projectGroups = {};
		stories.forEach((story) => {
			const projectId = story.project_id || 'unknown';
			if (!projectGroups[projectId]) {
				projectGroups[projectId] = {
					id: projectId,
					name: story.project_name || 'Unnamed Project',
					description: story.project_description || 'No description available',
					stories: []
				};
			}
			projectGroups[projectId].stories.push(story);
		});

		// Convert to array and add story count
		projects = Object.values(projectGroups).map((project) => ({
			id: project.id,
			name: project.name,
			description: project.description,
			total_stories: project.stories.length
		}));
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
					<a href="/org/{org_id}/stories/new" class="button">
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
		{#if stories.length === 0}
			{#each [1, 2, 3] as project}
				<div class="columns mt-4 is-multiline">
					{#each [1, 2, 3] as _}
						<div class="column is-one-third">
							<div class="skeleton-block" style="height: 250px;"></div>
						</div>
					{/each}
				</div>
			{/each}
		{:else if type === 'project'}
			<div class="columns mt-4 is-multiline">
				{#each filteredItems as project}
					<div class="column is-one-third">
						<ProjectCard {project} />
					</div>
				{/each}
			</div>
		{:else if type === 'story'}
			{#each filteredItems as story}
				<div class="">
					<StoryPreview {story} />
				</div>
			{/each}
		{:else}
			<p class="has-text-centered">No stories available</p>
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
