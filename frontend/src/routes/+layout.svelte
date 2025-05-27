<script>
	import '../../node_modules/bulma/css/bulma.css';
	import '../app.css';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import ErrorModal from '$lib/components/errorModal.svelte';

	let { children } = $props();
</script>

<!-- 
Add full page wrapper and article element to enable sticky footer
Ref: https://stackoverflow.com/questions/12239166/footer-at-bottom-of-page-or-content-whichever-is-lower
  -->

<div id="main-wrapper">
	<Header />
	<article>
		{@render children()}
	</article>
	<Footer />
</div>

<ErrorModal />

<style>
	:global(html),
	:global(body) {
		height: 100%;
		margin: 0;
		padding: 0;
	}

	#main-wrapper {
		display: -webkit-box;
		display: -ms-flexbox;
		display: flex;
		-webkit-box-orient: vertical;
		-webkit-box-direction: normal;
		-ms-flex-direction: column;
		flex-direction: column;
		min-height: 100%;
		height: auto;
		height: 100%;
		margin: 0 auto -142px; /* the bottom margin is the negative value of the footer's height */
	}

	article {
		-webkit-box-flex: 1;
		-ms-flex: 1;
		flex: 1;
	}
</style>
