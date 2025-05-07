<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import StoryCard from '$lib/components/StoryCard.svelte';
	import StoryPreview from '$lib/components/StoryPreview.svelte';

	let { data } = $props();
	const { tests, params } = data;

	let themeColor = $state('#133335');
	let type = $state('project'); // or 'story', depending on your logic

	let projectsTotal = $state(tests.length);
	let storiesTotal = $state(tests.length);
</script>

<div class="content">
	<div class="p-5">
		<OrgHeader
			org_name={params.org_name}
			description="This is a description of my organization"
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
						<strong>{type === 'story' ? storiesTotal : projectsTotal}</strong> Projects
					</p>
				</div>

				<div class="level-item">
					<div class="field has-addons">
						<p class="control">
							<input class="input" type="text" placeholder="Search for project" />
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
	{#if type === 'project'}
		<div class="columns mt-4">
			{#each tests as test}
				<div class="column is-one-third">
					<ProjectCard name={test.name} email={test.email} />
				</div>
			{/each}
		</div>
	{:else}
		{#each tests as test}
			<div class="">
				<StoryPreview name={test.name} email={test.email} text={test.text} />
			</div>
		{/each}
	{/if}
</div>

<style>
	.content {
		margin: 30px;
	}

	button.active {
		background-color: #133335;
		color: white;
	}
</style>
