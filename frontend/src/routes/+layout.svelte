<script>
	import '../../node_modules/bulma/css/bulma.css';
	import '../app.css';
	import Header from '$lib/components/Header.svelte';

	let { children } = $props();
</script>

<Header />

{@render children()}
