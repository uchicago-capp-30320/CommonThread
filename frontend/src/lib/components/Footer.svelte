<script>
	import logo from '$lib/assets/logos/logo_main.png';
</script>

<footer class="footer">
	<div
		class="content has-text-centered is-flex is-justify-content-center is-align-items-center"
		style="height: 100%;"
	>
		<p class="is-align-self-center is-fullwidth">
			<strong>CommonThread</strong> is an
			<a href="https://github.com/uchicago-capp-30320/CommonThread">
				open source project
				<span class="icon">
					<b><i class="fa fa-code-fork"></i></b>
				</span>
			</a>
			part of
			<a href="https://github.com/uchicago-capp-30320">
				Software Engineering for Civic Tech at UChicago</a
			>
		</p>
	</div>
</footer>

<style>
	.footer {
		background-color: var(--gray);
		filter: alpha(opacity=60);
		width: 100%;
		padding: 10px;
		height: 8vh;
		max-height: 75px;
		min-height: 50px;
		margin: auto;
	}

	p {
		color: #133335;
	}
	a {
		color: #56bcb3;
	}

	a:hover {
		text-decoration: underline;
	}
</style>
