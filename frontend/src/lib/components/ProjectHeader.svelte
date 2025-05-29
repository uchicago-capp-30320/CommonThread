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
	<div class="card columns column">
		<div class="card-content column">
			<div class="media">
				<div class="media-content">
					<p class="title is-4">{project_name}</p>

					<p class="subtitle is-5 mt-2 mb-0">
						<span class="icon">
							<i class="fa fa-lightbulb-o"></i>
							<!-- <i class="fa fa-user-robot"></i> -->
						</span>
						<i>AI Insight</i>
					</p>
					{#if typeof insight === 'object' && insight !== null}
						<div class="content">
							<ul class="fa-ul">
								{#each Object.entries(insight) as [key, value]}
									<li>
										<span class="fa-li"><i class="fas fa-circle-notch"></i></span>
										{value}
									</li>
								{/each}
							</ul>
						</div>
					{:else}
						{insight || 'No AI Insight'}
					{/if}
				</div>
			</div>

			<div class="content">
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
