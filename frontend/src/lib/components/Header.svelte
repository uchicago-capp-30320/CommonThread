<!-- ./ mobile
    // change logo
    // change nav items
 -->
<script>
	import logo from '$lib/logos/logo_main.png';
</script>

<header class="header">
	<div class="logo">
		<a href="/">
			<img src={logo} alt="Common Thread Logo" />
		</a>
	</div>
	<div class="right-section">
		<nav class="navigation">
			<ul>
				<li><a href="/about">About</a></li>
				<li><a href="/impact">Impact</a></li>
				<li><a href="/careers">Careers</a></li>
			</ul>
		</nav>
		<div class="auth">
			<button class="login-btn">Log In</button>
		</div>
	</div>
</header>

<style>
	a {
		text-decoration: none;
		color: inherit;
		margin: 0;
		padding: 0;
	}
	h1 {
		font-family: 'Unna', serif;
		font-weight: 700;
		margin: 0;
	}
	.logo {
		width: 150px;
		height: fit-content;
		margin-right: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.logo img {
		max-width: 100%;
		height: auto;
		display: block;
		margin: 0 auto;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 2rem;
		background-color: white;
		border-bottom: 1px solid #e0e0e0;
	}

	.right-section {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.navigation ul {
		display: flex;
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.navigation li {
		margin-left: 2rem;
	}

	.navigation li:first-child {
		margin-left: 0;
	}

	.navigation a {
		text-decoration: none;
		color: #333;
		font-size: 1rem;
	}

	.login-btn {
		background-color: #56bcb3;
		color: white;
		font-weight: 700;
		border: none;
		border-radius: 4px;
		padding: 0.5rem 1rem;
		cursor: pointer;
	}
</style>
