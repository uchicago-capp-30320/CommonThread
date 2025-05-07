<script lang="ts">
	// Refs: https://stackoverflow.com/questions/43370534/css-cutting-text-to-the-size-of-parent-div
	// Refs: https://www.w3schools.com/css/css3_borders.asp
	// Refs: https://dev.to/drews256/ridiculously-easy-row-and-column-layouts-with-flexbox-1k01
	let { name, email, text, author = '', date = '' } = $props();
</script>

<div class="myStory" id="myStory">
	<div class="row">
		<div class="column">
			<div class="title">
				{name}
			</div>
		</div>
		<div class="column">
			<div class="row" style="margin-right:0;margin-left:auto<float:right">
				<button style="background-color:#56BCB3">Story by {author}</button>
				<button style="background-color:#D0FDB9">Label 1</button>
				<button style="background-color:white">Label 2</button>
			</div>
		</div>
	</div>
	<p>{date}</p>
	<div class="row">
		<div class="text">
			{text}
		</div>
	</div>
</div>

<!-- <div class="container" id="myStory">
	"
	<div class="title">
		{name}
	</div>
	<p>{date}</p>
	<div class="text">
		{text}
	</div>
</div>

<button style="background-color:#56BCB3">Story by {author}</button><button
	style="background-color:#D0FDB9">Label 1</button
><button style="background-color:white">Label 2</button> -->

<style>
	#myStory {
		border-radius: 15px 50px 30px;
		border: 1px solid #133335;
		padding: 20px;
		width: 80%;
		height: 150px;
		background-color: #f2f1f0;
		filter: alpha(opacity=40);
	}

	.title {
		font-family: 'Arial';
		font-size: 1.5vw;
	}

	.container {
		flex-direction: column;
		display: flex;
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
		font-family: 'Arial';
	}

	button {
		color: #000000;
		border: 2px solid;
		border-radius: 25px;
	}
</style>
