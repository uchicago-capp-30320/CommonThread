<script>
	// TODO update with project data
	// project.name, project.description, project.total_stories
	import { page } from '$app/stores';

	let { project } = $props();
</script>

<div class="card">
	<div class="card-content">
		<div class="media">
			<div class="media-content">
				<p class="is-size-6 has-text-grey mb-1">Project</p>
				<p class="title is-4">{project.project_name}</p>
			</div>
			<div class="media-right">
				<div class="has-text-right">
					<p class="is-size-6 has-text-grey mb-0">Stories</p>
					<p class="is-size-5 has-text-weight-bold mt-0">{project.stories}</p>
				</div>
			</div>
		</div>
		<hr />

		<div class="content">
			<p class="is-size-6 has-text-grey mb-1">Project Description</p>
			{#if project.insight}
				{project.insight[Object.keys(project.insight)[0]]}
			{:else}
				<em>No insight available</em>
			{/if}
		</div>
		<div class="has-text-right mt-4">
			<a href="{$page.url.pathname}/project/{project.project_id}" class="button is-primary">
				<span>Explore Project</span>
				<span class="icon">
					<i class="fa fa-arrow-right"></i>
				</span>
			</a>
		</div>
	</div>
</div>
