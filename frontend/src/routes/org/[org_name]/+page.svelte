<script>

    let { data } = $props()
    const { tests } = data;

</script>


<h1>Org Name</h1>
<h2>Project List</h2>

{#each tests as item}
    <p>{item.name}</p>
    <p>{item.email}</p>
{/each}
