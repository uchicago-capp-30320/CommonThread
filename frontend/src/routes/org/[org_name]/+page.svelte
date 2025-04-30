<script>
	import OrgHeader from '../../../components/OrgHeader.svelte';
	import ProjectCard from '../../../components/ProjectCard.svelte';

	let { data } = $props();
	const { tests, params } = data;

	let themeColor = $state('#133335');
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
						<button class="button active">Project View</button>
						<button class="button">Story View</button>
					</div>
				</div>
			</div>
			<div class="level-right">
				<div class="level-item">
					<p class="subtitle is-5"><strong>123</strong> Projects</p>
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
	<div class="columns mt-4">
		{#each tests as test}
			<div class="column is-one-third">
				<ProjectCard name={test.name} email={test.email} />
			</div>
		{/each}
	</div>
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
