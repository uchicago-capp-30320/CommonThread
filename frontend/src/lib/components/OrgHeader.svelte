<script>
	import { page } from '$app/stores';

	let {
		org_name,
		description,
		profile_pic_path = 'https://bulma.io/assets/images/placeholders/96x96.png',
		background_color = 'blue',
		numProjects = 0,
		numStories = 0,
		orgs = [
			{
				org_id: 1,
				org_name: 'Organization 1'
			},
			{
				org_id: 2,
				org_name: 'Organization 2'
			},
			{
				org_id: 3,
				org_name: 'Organization 3'
			}
		]
	} = $props();

	let dActive = $state(false);

	let notAdminPage = $state(!$page.url.pathname.includes('admin'));
</script>

<div class="columns">
	<div class="card columns column is-half">
		<div class="column is-one-quarter">
			<figure class="image is-128x128">
				<img class="box" src={profile_pic_path} alt="org profile pic" />
			</figure>
		</div>
		<div class="card-content column is-three-quarters pl-5">
			<div class="media">
				<div class="media-content">
					<p class="title is-4">{org_name}</p>
					<p class="subtitle is-6">{description}</p>
				</div>
			</div>

			<div class="content">
				<nav class="level-left">
					<div class="level-item has-text-centered mr-5">
						<div>
							<p class="heading mb-1">Projects</p>
							<p class="title is-4 mt-0">{numProjects}</p>
						</div>
					</div>
					<div class="level-item has-text-centered ml-5">
						<div>
							<p class="heading mb-1">Stories</p>
							<p class="title is-4 mt-0">{numStories}</p>
						</div>
					</div>
				</nav>
				{#if notAdminPage}
					<nav class="level-right">
						<div class="level-item">
							<a href="{$page.url.pathname}/admin" class="button is-secondary is-small mr-2">
								<span class="icon is-small">
									<i class="fa fa-edit"></i>
								</span>
								<span>Edit Organization</span>
							</a>
						</div>
					</nav>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	* {
		color: white;
	}

	.dropdown-item {
		color: black !important;
	}
	.card {
		background-color: var(--card-color);
	}
</style>
