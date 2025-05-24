<script>
	// Refs: https://stackoverflow.com/questions/43370534/css-cutting-text-to-the-size-of-parent-div
	// Refs: https://www.w3schools.com/css/css3_borders.asp
	// Refs: https://dev.to/drews256/ridiculously-easy-row-and-column-layouts-with-flexbox-1k01
	import { page } from '$app/stores';

	const { org_id, story_id } = $page.params;

	let { story } = $props();
</script>

<div class="box" id="storySample">
	<div class="column">
		<div class="mb-1">
			<span class="has-text-left">PROJECT</span>
			<div class="title is-4 has-text-left">
				{story.project_name}
			</div>
		</div>

		<div class="column">
			<div class="row mb-2">
				<span class="tag is-info is-small"> Storyteller: {story.storyteller} </span>
				<span class="tag is-warning is-small"> Curator: {story.curator} </span>
				<span class="tag is-primary is-small" id="date"> {story.date} </span>
			</div>

			<div class="row">
				{story.text_content
					? story.text_content.length > 500
						? story.text_content.slice(0, 500) + '...'
						: story.text_content
					: ''}
				{#if story.audio}
					<audio controls>
						<source src={story.audio} type="audio/mpeg" />
						Your browser does not support the audio element.
					</audio>
				{/if}
			</div>
			<div class="mt-4 has-text-right">
				<a
					href="{$page.url.origin}/org/{org_id}/story/{story.story_id}"
					class="button is-primary is-rounded"
				>
					<span>Read More</span>
					<span class="icon">
						<i class="fa fa-arrow-right"></i>
					</span>
				</a>
			</div>
		</div>
	</div>
</div>

<style>
	#storySample {
		display: flex;
		flex-direction: column;
		border-radius: 15px 50px 30px;
		border: 2px solid var(--dark-blue); /* Using Bulma's info color instead of #133335 */
		padding: 1.5em;
		width: 100%;
		max-width: 900px;
		margin: 1rem auto;
		height: auto;
		min-height: 300px;
		background-color: #fff;
		box-shadow: 0 2px 5px rgba(10, 10, 10, 0.1);
		transition:
			transform 0.3s ease,
			box-shadow 0.3s ease;
	}

	#storySample:hover {
		transform: translateY(-5px);
		box-shadow: 0 5px 15px rgba(10, 10, 10, 0.2);
	}

	.row {
		display: flex;
		flex-direction: row;
	}

	.column {
		display: flex;
		flex-direction: column;
	}

	.text {
		flex: 1;
		overflow: hidden;
	}

	span + span {
		margin-left: 2%;
	}

	#date {
		display: flex;
		float: right;
	}

	#storyContent {
		margin-top: 15px;
	}

	/*
	Alternative for overflow
	Ref: https://css-tricks.com/almanac/properties/t/text-overflow/
	 .ellipsis {
		text-overflow: ellipsis;
		white-space: nowrap;
		overflow: hidden;
	} */
</style>
