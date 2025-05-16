<script>
	// TODO update with project data
	// project.name, project.description, project.total_stories

	let { project } = $props();
</script>

<div class="card">
	<div class="card-content">
		<div class="media">
			<div class="media-content">
				<p class="is-size-6 has-text-grey mb-1">Project</p>
				<p class="title is-4">{project.name}</p>
			</div>
			<div class="media-right">
				<div class="has-text-right">
					<p class="is-size-6 has-text-grey mb-0">Stories</p>
					<p class="is-size-5 has-text-weight-bold mt-0">{project.total_stories}</p>
				</div>
			</div>
		</div>
		<hr />

		<div class="content">
			<p class="is-size-6 has-text-grey mb-1">Project Description</p>
			This is a description placeholder of the project. It can be a bit longer to give more context about
			the project and its goals.
		</div>
		<div class="has-text-right mt-4">
			<a href="/projects/{project.id}/dashboard" class="button is-primary">
				<span>Explore Project</span>
				<span class="icon">
					<i class="fa fa-arrow-right"></i>
				</span>
			</a>
		</div>
	</div>
</div>
