<script>
	import StoryInput from '$lib/components/story/StoryHolder.svelte';
</script>

<div class="page-container is-flex is-flex-direction-column is-align-items-center p-5 is-fullwidth">
	<StoryInput />
</div>

<style>
	.page-container {
		background-image: url('$lib/assets/background_texture.png');
		min-height: 100vh; /* so that container takes up the full height */
	}
</style>
