<script>
	// TODO update with project data
	// project.name, project.description, project.total_stories

	let { story } = $props();
</script>

<div class="card">
	<div class="card-content">
		<div class="media">
			<div class="media-content">
				<p class="is-size-6 has-text-grey mb-1">Project</p>
				<p class="title is-4">{story.storyteller}</p>
			</div>
			<div class="media-right">
				<div class="has-text-right">
					<p class="is-size-6 has-text-grey mb-0">Stories</p>
					<p class="is-size-5 has-text-weight-bold mt-0">10</p>
				</div>
			</div>
		</div>
		<hr />

		<div class="content">
			<p class="is-size-6 has-text-grey mb-1">Project Description</p>
			{story.content}
		</div>
	</div>
</div>
