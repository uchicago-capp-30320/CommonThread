<script>
	// Refs: https://stackoverflow.com/questions/43370534/css-cutting-text-to-the-size-of-parent-div
	// Refs: https://www.w3schools.com/css/css3_borders.asp
	// Refs: https://dev.to/drews256/ridiculously-easy-row-and-column-layouts-with-flexbox-1k01
	let story = $props();

</script>

<div class="box" id="storySample">
	<div class="column">
		<div class="row" style="margin-right:0;margin-left:auto<float:right">
			<span class="tag is-info is-medium"> Storyteller: { story.storyteller } </span>
			<span class="tag is-info is-medium"> Curator: { story.curator } </span>
			<span class="tag is-primary is-medium" id="date"> { story.date } </span>	
		</div>

		<div class="text" id="storyContent">
			{ story.content }
		</div>

	</div>
</div>


<style>

	#storySample {
		display: flex;
		flex-direction: flex;
		border-radius: 15px 50px 30px;
		border: 1px solid #133335;
		padding: 1em;
		width: 75%;
		height: 300px;
		background-color: #f2f1f0;
		filter: alpha(opacity=40);
		justify-content: center;
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
