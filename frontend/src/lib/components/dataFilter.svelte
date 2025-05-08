<script>
	let { currentGroupBy, uniqueTags, updateGroupBy } = $props();
</script>

<div class="sidebar">
	<h3>Group by</h3>
	<hr />

	<div class="filter-section">
		<div class="label mb-0">TAG</div>
		<div class="filter-options">
			<div class="select is-fullwidth">
				<select bind:value={currentGroupBy} onchange={() => updateGroupBy(currentGroupBy)}>
					<option value="storyteller">Storyteller</option>
					<option value="curator">Curator</option>
					<option value="date">Date</option>
					{#each uniqueTags as tag}
						<option value={tag.name}>{tag.name}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>
</div>

<style>
	.sidebar {
		background-color: #56bcb374;
		padding: 1rem;
		border-radius: 8px;
		height: 100%;
		height: fit-content;
	}

	h3 {
		font-weight: 400;
		margin-top: 0;
		margin-bottom: 0;
		font-size: 1.5rem;
		color: black !important;
	}

	.filter-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
</style>
