<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import DataFilter from '$lib/components/DataFilter.svelte';
	import BarChart from '$lib/layer-cake/BarChart.svelte';
	import LineAreaChart from '$lib/layer-cake/LineAreaChart.svelte';
	import { timeParse } from 'd3-time-format';

	const parseDate = timeParse('%Y-%m-%d');

	let { stories } = $props();

	let uniqueTags = new Set();
	stories.forEach((story) => {
		if (story.tags) {
			story.tags.forEach((tag) => uniqueTags.add(tag));
		}
	});

	// Function to group stories by a specified field
	function groupStoriesByField(stories, field) {
		return Object.entries(
			stories.reduce((acc, story) => {
				const value = story[field] || 'Unknown';
				if (!acc[value]) {
					acc[value] = 0;
				}
				acc[value]++;
				return acc;
			}, {})
		).map(([key, count]) => ({
			[field]: key,
			count
		}));
	}

	let currentGroupBy = $state('storyteller');

	let barData = $derived(groupStoriesByField(stories, currentGroupBy));

	// Function to create running totals data for stories by date
	function createRunningTotalByDate(stories) {
		// Sort stories by date
		const sortedStories = [...stories].sort((a, b) => {
			// Handle ISO date format (YYYY-MM-DDTHH:MM:SSZ)
			return new Date(a.date) - new Date(b.date);
		});

		const runningTotals = [];
		let total = 0;

		// Group by date and calculate running total
		sortedStories.forEach((story) => {
			// Extract date part and convert to timestamp for numerical representation
			const dateString = story.date.split('T')[0];
			const timestamp = new Date(dateString).getTime();
			const existingEntry = runningTotals.find((entry) => entry.date === timestamp);

			if (existingEntry) {
				existingEntry.count++;
				existingEntry.total = ++total;
			} else {
				runningTotals.push({
					date: timestamp,
					count: 1,
					total: ++total
				});
			}
		});

		return runningTotals;
	}

	let storiesRunningTotal = $derived(createRunningTotalByDate(stories));

	$inspect(storiesRunningTotal);

	let themeColor = $state('#133335');

	function updateGroupBy(value) {
		currentGroupBy = value;
		//applyFilters(currentFilters);
	}
</script>

<div class="dashboard p-5">
	<div class="sidebar-container">
		<DataFilter {currentGroupBy} {uniqueTags} {updateGroupBy} />
	</div>

	<div class="charts-container">
		<div class="response-count">{stories.length} Stories</div>
		<div class="chart-column">
			<BarChart data={barData} xKey={'count'} yKey={currentGroupBy} />
			<LineAreaChart data={storiesRunningTotal} xKey={'date'} yKey={'total'} stroke={themeColor} />
		</div>
	</div>
</div>

<style>
	.dashboard {
		display: grid;
		grid-template-columns: 200px 1fr;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	.sidebar-container {
		grid-column: 1;
	}

	.response-count {
		position: absolute;
		top: 0.8rem;
		left: 2rem;
		font-size: 0.9rem;
		font-weight: 500;
		color: #555;
		background-color: rgba(255, 255, 255, 0.7);
		padding: 0.3rem 0.7rem;
		border-radius: 4px;
		z-index: 1;
	}

	.charts-container {
		position: relative;
		background-color: #56bcb374;
		grid-column: 2;
		padding: 2rem;
		padding-top: 3rem;
		border-radius: 8px;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}

	.chart-column,
	.text-column {
		padding-top: 0.5rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	@media (max-width: 900px) {
		.dashboard {
			grid-template-columns: 1fr;
		}

		.sidebar-container,
		.charts-container {
			grid-column: 1;
		}

		.charts-container {
			grid-template-columns: 1fr;
		}

		.chart-column,
		.text-column {
			gap: 1rem;
		}

		.response-count {
			top: 0.8rem;
			left: 2rem;
		}
	}
</style>
