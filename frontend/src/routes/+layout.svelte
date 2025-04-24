<script>
	import '../../node_modules/bulma/css/bulma.css';

	let { children } = $props();

</script>

<nav>
	<a href="/">Home</a>
	<a href="/about">About</a>
	<a href="/settings">Settings</a>
</nav>

{@render children()}
