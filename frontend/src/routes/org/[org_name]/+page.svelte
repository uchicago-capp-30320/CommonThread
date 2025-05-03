<script>
	let { data } = $props();
	const { tests, params } = data;

</script>

<h1>Org Name {params.org_name} </h1>
<h2>Project List</h2>

{#each tests as item}
	<p>{item.name}</p>
	<p>{item.email}</p>
{/each}
