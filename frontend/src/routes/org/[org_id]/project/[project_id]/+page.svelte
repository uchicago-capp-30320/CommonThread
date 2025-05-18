<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { accessToken, refreshToken } from '$lib/store.js';

	let stories = $state([]);
	let projectData = $state({ name: 'Loading...', insight: 'Loading...', story_count: 0 });
	let projectsTotal = $state('...');
	let storiesTotal = $state('...');
	let themeColor = $state('#133335');
	let type = $state('dash');
	$inspect(projectData);
	$inspect(stories);

	onMount(async () => {
		// Fetch the data when the component mounts
		const project_id = page.params.project_id;

		// Make both requests concurrently using Promise.all
		const [storiesResponse, projectResponse] = await Promise.all([
			authRequest(`/stories?project_id=${project_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/project/${project_id}`, 'GET', $accessToken, $refreshToken)
		]);

		if (storiesResponse.newAccessToken) {
			accessToken.set(storiesResponse.newAccessToken);
		}

		projectData = projectResponse.data;

		const loadedData = storiesResponse.data;
		stories = loadedData['stories'];
	});
</script>

<div class="container">
	<div class="p-5">
		<OrgHeader
			org_name={projectData.project_name}
			description={projectData.insight}
			numProjects={projectData.story_count}
			numStories={projectData.story_count}
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
					<a href="/stories/" class="button">
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
						<strong>{projectData.story_count}</strong> Stories
					</p>
				</div>
				{#if type === 'story'}
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
				{/if}
			</div>
		</div>
	</div>

	<hr />

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
	{:else if type === 'dash'}
		<DataDashboard {stories} />
	{:else if type === 'story'}
		{#each stories as story}
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
