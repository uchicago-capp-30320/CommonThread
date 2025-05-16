<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import StoryCard from '$lib/components/StoryCard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';

	// import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	// import { accessToken, refreshToken } from '$lib/store.js';

	let stories = $state([
		{
			id: 1,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'John Doe',
			storyteller: 'Fatima',
			date: '2023-01-01',
			content: 'I love horses so much',
			project_name: 'I Love Horses',
			project_id: '1'
		},
		{
			id: 2,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'Jane Doe',
			storyteller: 'Austin',
			date: '2023-01-02',
			content: 'My first experience with python was last year.',
			project_name: 'Python for Beginners',
			project_id: '2'
		},
		{
			id: 2,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'Jane Doe',
			storyteller: 'Austin',
			date: '2023-01-02',
			content: 'Here is a story about horses',
			project_name: 'I Love Horses',
			project_id: '1'
		}
	]);
	let projectsTotal = $state('...');
	let storiesTotal = $state('...');
	let projects = $state([]);
	let orgName = $state('Loading...');
	let searchValue = $state('');
	let themeColor = $state('#133335');
	let type = $state('project');
	let dataLoaded = $state(false);

	let params = $state(page.params);

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
			return stories.filter((story) => story.content.toLowerCase().includes(searchTerm));
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

	$inspect(stories);

	onMount(async () => {
		// first make a request to get list of orgs that user is a part of
		// const orgs = await authRequest(`/orgs`, 'GET', $accessToken, $refreshToken);
		// const orgsData = await orgs.json();
		// console.log('Orgs fetched:', orgsData);
		// const defaultOrg = orgsData[0].org_id;
		// orgName = orgsData[0].org_name;

		// // Fetch the data when the component mounts
		// const data = await authRequest(`/orgs/${defaultOrg}`, 'GET', $accessToken, $refreshToken);
		// const loadedData = await data.json();
		// console.log('Data fetched:', loadedData);

		// if (loadedData.newAccessToken) {
		// 	accessToken.set(loadedData.newAccessToken);
		// }

		// stories = loadedData['stories'];
		// orgName = loadedData['org_name'];
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
</script>

<div class="container">
	<div class="p-5">
		<OrgHeader
			org_name={orgName}
			description="This is a description of my organization"
			numProjects={projectsTotal}
			numStories={storiesTotal}
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
					<a href="/stories/new?org_id={encodeURIComponent(params.org_name)}" class="button">
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

	{#if stories.length === 0}
		<p class="has-text-centered">Loading Stories...</p>
	{:else if filteredItems.length === 0}
		<p class="has-text-centered">No {type} available. Widen search.</p>
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
	{/if}
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
