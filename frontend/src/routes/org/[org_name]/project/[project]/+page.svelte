<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import DataDashboard from '$lib/components/DataDashboard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';

	//import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	//import { accessToken, refreshToken } from '$lib/store.js';

	let projectData = $state({
		projectName: 'Test Project',
		description: 'This is a test description',
		storiesTotal: 1000
	});
	let type = $state('dash');
	let stories = $state([
		{
			id: 1,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'John Doe',
			storyteller: 'Fatima',
			date: '2023-01-01',
			content: 'This is a test story'
		},
		{
			id: 2,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'Jane Doe',
			storyteller: 'Austin',
			date: '2023-01-02',
			content: 'This is a test story'
		},
		{
			id: 2,
			tags: { topic: 'health', location: 'chicago' },
			curator: 'Jane Doe',
			storyteller: 'Austin',
			date: '2023-01-02',
			content: 'This is a test story'
		}
	]);
	let storiesTotal = $derived(stories.length);

	let params = $state(page.params);

	$inspect(stories);

	onMount(async () => {
		// first make a request to get list of orgs that user is a part of
		//const project = await authRequest(`/projects`, 'GET', $accessToken, $refreshToken);
		//projectData = await project.json();
		console.log('project fetched:', projectData);
	});

	let themeColor = $state('#133335');
</script>

<div class="container">
	<div class="p-5">
		<OrgHeader
			org_name={projectData.projectName}
			description={projectData.description}
			numProjects="1"
			numStories={projectData.storiesTotal}
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
						<strong>{storiesTotal}</strong> Stories
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
		<p class="has-text-centered">Loading Stories...</p>
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
