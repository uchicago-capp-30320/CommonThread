<script>
	import { page } from '$app/stores';

	let {
		project_name,
		insight = 'No AI Insight',
		project_pic = 'https://bulma.io/assets/images/placeholders/96x96.png',
		stories = 0,
		org_id
	} = $props();

	let dActive = $state(false);
</script>

<div class="columns">
	<div class="card columns column is-half">
		<div class="card-image column is-one-fifth">
			<figure class="image is-4by3">
				<img src={project_pic} alt="Placeholder" />
			</figure>
		</div>
		<div class="card-content column">
			<div class="media">
				<div class="media-content">
					<p class="title is-4">{project_name}</p>
					<p class="subtitle is-6">{insight || 'No AI Insight'}</p>
				</div>
			</div>

			<div class="content">
				<nav class="level-left">
					<div class="level-item has-text-centered ml-5">
						<div>
							<p class="heading mb-1">Stories</p>
							<p class="title is-4 mt-0">{stories}</p>
						</div>
					</div>
				</nav>
				<nav class="level-right">
					<div class="level-item">
						<a href="/org/{org_id}/admin" class="button is-secondary is-small mr-2">
							<span class="icon is-small">
								<i class="fa fa-edit"></i>
							</span>
							<span>Edit Project</span>
						</a>
					</div>
				</nav>
			</div>
		</div>
	</div>
</div>

<style>
	* {
		color: white;
	}

	.card {
		background-color: var(--card-color);
	}
</style>
