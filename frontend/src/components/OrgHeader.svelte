<script>
	let {
		org_name,
		description,
		orgImage = 'https://bulma.io/assets/images/placeholders/96x96.png',
		background_color = 'blue'
	} = $props();
</script>

<div class="columns">
	<div class="card columns column is-half">
		<div class="card-image column is-one-fifth">
			<figure class="image is-4by3">
				<img src={orgImage} alt="Placeholder" />
			</figure>
		</div>
		<div class="card-content column">
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
							<p class="title is-4 mt-0">3,456</p>
						</div>
					</div>
					<div class="level-item has-text-centered ml-5">
						<div>
							<p class="heading mb-1">Projects</p>
							<p class="title is-4 mt-0">123</p>
						</div>
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
