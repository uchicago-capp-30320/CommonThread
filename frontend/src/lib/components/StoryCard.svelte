<script>
	let { name, email, text } = $props();
</script>

<div class="column is-9">
	<!-- Takes up 3/4 of the page (9/12 columns) -->
	<div class="card">
		<header class="card-header">
			<p class="card-header-title">
				{name}
			</p>
			<p class="card-header-icon">
				<span class="icon mr-2">
					<i class="fas fa-envelope" aria-hidden="true"></i>
				</span>
				<span class="is-size-6">{email}</span>
			</p>
		</header>

		<div class="card-content">
			<div class="content">
				{text}
			</div>
		</div>

		<footer class="card-footer">
			<div class="tags are-medium m-2">
				<span class="tag is-info">Tag 1</span>
				<span class="tag is-success">Tag 2</span>
				<span class="tag is-warning">Tag 3</span>
			</div>
		</footer>
	</div>
</div>
