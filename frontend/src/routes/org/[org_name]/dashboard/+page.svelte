<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import SidebarFilter from '$lib/components/dataFilter.svelte';
	import BarChart from '$lib/layer-cake/BarChart.svelte';
	import LineAreaChart from '$lib/layer-cake/LineAreaChart.svelte';
	import { timeParse } from 'd3-time-format';

	const parseDate = timeParse('%Y-%m-%d');

	let { data } = $props();
	const { stories, params } = data;

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

	let barLocation = $derived(groupStoriesByField(stories, 'location'));
	let barTopic = $derived(groupStoriesByField(stories, 'topic'));

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

	let currentFilters = $state({
		age: 'all',
		state: 'all',
		gender: 'all',
		education: 'all'
	});

	function onFilterChange(type, value) {
		currentFilters[type] = value;
		//applyFilters(currentFilters);
	}
</script>

<div class="content">
	<div class="header p-6">
		<OrgHeader org_name="My Organization" --card-color={themeColor} />
	</div>
	<hr />
	<div class="dashboard p-5">
		<div class="sidebar-container">
			<SidebarFilter
				ageFilter={currentFilters.age}
				genderFilter={currentFilters.gender}
				stateFilter={currentFilters.state}
				educationFilter={currentFilters.education}
				{onFilterChange}
			/>
		</div>

		<div class="charts-container">
			<div class="response-count">100 Stories</div>
			<div class="chart-column"></div>
			<BarChart data={barLocation} xKey={'count'} yKey={'location'} />
			<BarChart data={barTopic} xKey={'count'} yKey={'topic'} />
			<div class="text-column">
				<LineAreaChart
					data={storiesRunningTotal}
					xKey={'date'}
					yKey={'total'}
					stroke={themeColor}
				/>
			</div>
		</div>
	</div>
</div>

<style>
	.header {
		position: relative;
	}
	.content {
		margin: auto;
		margin-top: 30px;
		height: 90vh;
		border-radius: 10px;
	}
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
</style>
