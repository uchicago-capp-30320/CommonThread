<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import StoryCard from '$lib/components/StoryCard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';

	let { data } = $props();
	const { storiesPromise: getDataPromise, params } = data;

	let stories = $state([]);
	let projectsTotal = $state('...');
	let storiesTotal = $state('...');
	let projects = $state([]);
	let orgName = $state('Loading...');

	$inspect(getDataPromise);
	$inspect(params);
	$inspect(stories);
	$inspect(projects);

	$effect(() => {
		getDataPromise
			.then((loadedData) => {
				stories = loadedData['stories'];
				orgName = loadedData['org_name'];
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
			})
			.catch((error) => {
				console.error('Error loading stories:', error);
			});
	});

	let themeColor = $state('#133335');
	let type = $state('project'); // or 'story', depending on your logic

	$inspect(projects);
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
						<button class="button {type === 'dash' ? 'active' : ''}" onclick={() => (type = 'dash')}
							>Dashboard</button
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
							<input class="input" type="text" placeholder={`Search for ${type}`} />
						</p>
						<p class="control">
							<button class="button">Search</button>
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>

	<hr />

	{#if stories.length === 0}
		<p class="has-text-centered">Loading Stories...</p>
	{:else if type === 'project'}
		<div class="columns mt-4 is-multiline">
			{#each projects as project}
				<div class="column is-one-third">
					<ProjectCard {project} />
				</div>
			{/each}
		</div>
	{:else if type === 'story'}
		{#each stories as story}
			<div class="">
				<StoryPreview {story} />
			</div>
		{/each}
	{:else if type === 'dash'}
		<DataDashboard {stories} />
	{:else}
		<p class="has-text-centered">No stories available</p>
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
