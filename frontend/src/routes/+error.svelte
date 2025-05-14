<script>
	import { page } from '$app/state';
	import error403 from '$lib/assets/illustrations/error403.png';
	import error404 from '$lib/assets/illustrations/error404.png';
	import error500 from '$lib/assets/illustrations/error500.png';
	import inDevelopment from '$lib/assets/illustrations/error500.png';
</script>

<div id="container">
	<div class="banner">
		{#if page.status === 500 || page.error.message === 'Forbidden'}
			<img src={error500} alt="Customized illustration for HTTP error 500" />
		{:else if page.status === 404}
			<img src={error404} alt="Customized illustration for HTTP error 404" />
		{:else if page.status === 403}
			<img src={error403} alt="Customized illustration for HTTP error 403" />
		{:else}
			<h1>{page.status}: {page.error.message}</h1>
		{/if}
	</div>
</div>
