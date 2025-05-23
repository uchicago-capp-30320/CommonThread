<script>
	let { story } = $props();
</script>

<div class="card">
	<header class="card-header">
		<h2>
			Curated by <span class="curator">{story.curator}</span> for
			<span class="project">{story.project_name}</span>
		</h2>
	</header>
	<div class="content">
		<h1>Story by <span class="storyteller"><b>{story.storyteller}</b></span></h1>
		{#each story.tags as tag}
			<div class="tags are-medium m-2">
				<span class="tag">{tag.name}</span>
			</div>
		{/each}

		<!-- Row of tags  -->
		<p>{story.text_content}</p>
	</div>
</div>

<style>
	.card-header {
		background-color: #ede8eb;
		padding: 10px;
	}

	.content {
		padding: 25px;
	}

	.tag {
		background-color: #d0fdb9;
	}

	/* 
    span.storyteller {
        color: #56bcb3;
    } */

	/* span.curator {

    }

    span.project {

    } */
</style>
