<script>
	let { currentGroupBy, uniqueTags, updateGroupBy } = $props();
</script>

<div class="sidebar">
	<h3>Filter by</h3>
	<hr />

	<div class="filter-section">
		<h4>TAG</h4>
		<div class="filter-options">
			<select
				bind:value={currentGroupBy}
				class="filter-dropdown"
				onchange={() => updateGroupBy(currentGroupBy)}
			>
				<option value="all">All</option>
				{#each { uniqueTags } as tag}
					<option value={tag.name}>{tag}</option>
				{/each}
				<option value="storyteller">Storyteller</option>
				<option value="curator">Curator</option>
				<option value="date">Date</option>
			</select>
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

	h4 {
		margin: 1rem 0 0.5rem;
		font-size: 0.8rem;
		color: black !important;
	}

	.filter-options {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.filter-btn {
		background-color: #e0e0e0;
		border: none;
		padding: 0.5rem;
		border-radius: 4px;
		cursor: pointer;
		text-align: left;
		font-size: 0.9rem;
	}

	.filter-btn.active {
		background-color: var(--dark-blue);
		color: white;
	}
</style>
