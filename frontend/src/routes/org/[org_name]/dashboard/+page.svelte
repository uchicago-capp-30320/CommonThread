<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	let themeColor = $state('blue');
</script>

<div class="content">
	<div class="header"></div>
</div>

<style>
	.header {
		position: relative;
	}
	.content {
		margin: auto;
		margin-top: 30px;
		height: 90vh;
		width: calc(100% - 40px); /* full width minus left and right margin */

		background-color: var(--light-blue);
		opacity: 0.25;
		border-radius: 10px;
	}
</style>
