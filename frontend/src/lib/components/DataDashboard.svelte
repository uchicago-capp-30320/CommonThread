<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import BarChart from '$lib/layer-cake/BarChart.svelte';
	import LineAreaChart from '$lib/layer-cake/LineAreaChart.svelte';
	import { timeParse } from 'd3-time-format';
	import { is } from 'immutable';

	const parseDate = timeParse('%Y-%m-%d');

	let { stories } = $props();

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

	// Function to group stories by a specified tag
	function groupStoriesByTag(stories, tagName) {
		return Object.entries(
			stories.reduce((acc, story) => {
				if (story.tags && Array.isArray(story.tags)) {
					const tag = story.tags.find((t) => t && t.name === tagName);
					const value = tag ? tag.value : 'Unknown';
					if (!acc[value]) {
						acc[value] = 0;
					}
					acc[value]++;
				}
				return acc;
			}, {})
		).map(([key, count]) => ({
			[tagName]: key,
			count
		}));
	}

	let currentGroupBy = $state('storyteller');

	let uniqueTags = new Set();

	// Extract unique tags from stories
	stories.forEach((story) => {
		if (story.tags) {
			// Handle tags in format { name: string, value: string }
			if (Array.isArray(story.tags)) {
				story.tags.forEach((tag) => {
					if (tag && tag.name) {
						uniqueTags.add(tag.name);
					}
				});
			} else if (typeof story.tags === 'object') {
				// Fallback for old format { topic: 'health', location: 'chicago' }
				Object.keys(story.tags).forEach((key) => uniqueTags.add(key));
			}
		}
	});
	console.log('Unique tags:', uniqueTags);
	let groupTag = $state(uniqueTags.size > 0 ? [...uniqueTags][0] : null);

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

	// Get topline stats
	let uniqueStorytellers = $derived(new Set(stories.map((s) => s.storyteller)).size);
	let latestStory = $derived.by(() => {
		if (stories.length === 0) return 'None';
		// Safely handle string dates by ensuring proper Date objects are created first
		const validDates = stories
			.map((s) => (s.date ? new Date(s.date) : null))
			.filter((date) => date && !isNaN(date.getTime()));
		if (validDates.length === 0) return 'None';
		return new Date(Math.max(...validDates.map((d) => d.getTime()))).toLocaleDateString();
	});

	let storiesByTag = $derived.by(() => {
		if (!groupTag || !uniqueTags.has(groupTag)) return null;
		return groupStoriesByTag(stories, groupTag);
	});

	let storiesByStoryteller = $derived(groupStoriesByField(stories, 'storyteller'));
	let storiesByCurator = $derived(groupStoriesByField(stories, 'curator'));
	let themeColor = $state('#133335');
</script>

<div class="container is-fluid p-4">
	<div class="box mb-5">
		<div class="columns is-multiline">
			<div class="column is-4-desktop is-12-tablet">
				<div class="notification is-primary is-light has-text-centered">
					<p class="heading">Total Stories</p>
					<p class="title">{stories.length}</p>
				</div>
			</div>
			<div class="column is-4-desktop is-12-tablet">
				<div class="notification is-primary is-light has-text-centered">
					<p class="heading">Storytellers</p>
					<p class="title">{uniqueStorytellers}</p>
				</div>
			</div>
			<div class="column is-4-desktop is-12-tablet">
				<div class="notification is-primary is-light has-text-centered">
					<p class="heading">Latest Story</p>
					<p class="title">{latestStory}</p>
				</div>
			</div>
		</div>
	</div>

	<div class="box has-background-primary-light p-5 position-relative">
		<div class="columns is-multiline">
			<div class="column is-6-desktop is-12-tablet">
				<div class="box">
					<h3 class="title is-5">Cumulative Stories Over Time</h3>
					<LineAreaChart
						data={storiesRunningTotal}
						xKey={'date'}
						yKey={'total'}
						stroke={themeColor}
						fill={themeColor + '25'}
					/>
				</div>
			</div>
			<div class="column is-6-desktop is-12-tablet">
				<div class="box">
					<div
						style="display: flex; justify-content: space-between; align-items: center"
						class="mb-4"
					>
						<h3 class="title is-5">
							Stories by Tag:
							<span class="select is-small is-primary ml-2" style="vertical-align: middle;">
								<select bind:value={groupTag}>
									{#each [...uniqueTags] as tag, i}
										<option value={tag} selected={i === 0}>{tag}</option>
									{/each}
								</select>
							</span>
						</h3>
					</div>

					{#if groupTag && storiesByTag}
						<BarChart data={storiesByTag} xKey={'count'} yKey={groupTag} />
					{:else}
						<p class="has-text-centered mt-4">Select a tag to view data</p>
					{/if}
				</div>
			</div>
			<div class="column is-6-desktop is-12-tablet">
				<div class="box">
					<h3 class="title is-5">Stories by Storyteller</h3>
					<BarChart data={storiesByStoryteller} xKey={'count'} yKey="storyteller" />
				</div>
			</div>
			<div class="column is-6-desktop is-12-tablet">
				<div class="box">
					<h3 class="title is-5">Stories by Curator</h3>
					<BarChart data={storiesByCurator} xKey={'count'} yKey="curator" />
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* Add custom styling to complement Bulma if needed */
	.position-relative {
		position: relative;
	}
</style>
