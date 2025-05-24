<!-- ./ mobile
    // change logo
    // change nav items
 -->
<script>
	// Imports
	import logo from '$lib/assets/logos/logo_main.png';
	import { accessToken, refreshToken, userExpirationTimestamp } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/state';

	// URL parameters
	const org_id = page.params.org_id;

	// Tasks while launch
	onMount(async () => {
		// Check authorization 
		let authorized = $state(false)
		const now = new Date();
		const expirationDate = new Date($userExpirationTimestamp);
		if (now > expirationDate) {
			console.log('User token expired');
			} else {
			console.log('User token is valid');
			authorized = true; 
			// API requests (only executed if user is authorized)
			const [orgResponse, userRequest] = await Promise.all([
				authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
				authRequest(`/user`, 'GET', $accessToken, $refreshToken)
			]);

			// Data
			orgs = userRequest.data.orgs.filter((org) => org.org_id !== org_id);
			if (storiesResponse.newAccessToken) {
				accessToken.set(storiesResponse.newAccessToken);
			}
		}
	}); 

	// Drop-down button state
	let dActive = $state(false)
</script>

<header class="header">
	<div class="logo">
		<a href="/">
			<img src={logo} alt="Common Thread Logo" />
		</a>
	</div>
	{#if !authorized}
		<div class="right-section">
			<nav class="navigation">
				<ul>
					<li><a href="/about">About</a></li>
					<li><a href="/impact">Impact</a></li>
					<li><a href="/careers">Careers</a></li>
				</ul>
			</nav>
			<div class="auth">
				<a href="/login">
					<button class="login-btn">Log In</button>
				</a>
				<!-- <a href="/signup">
					<button class="signup-btn">Sign Up</button>
				</a> -->
			</div>
		</div>
	{:else}
		<div class="right-section">
			<div class="dropdown {dActive ? 'is-active' : ''}">
				<div class="dropdown-trigger">
					<button
						class="button is-secondary is-small"
						aria-haspopup="true"
						aria-controls="dropdown-menu"
						onclick={() => {
							dActive = !dActive;
						}}
					>
						<span>Change Organization</span>
						<span class="icon is-small">
							<i class="fa fa-angle-down" aria-hidden="true"></i>
						</span>
					</button>
				</div>
				<div class="dropdown-menu" id="dropdown-menu" role="menu" hidden>
					<div class="dropdown-content">
						{#each orgs as org}
							<a target="_self" href="/org/{org.org_id}" class="dropdown-item">{org.org_name}</a
							>
						{/each}
					</div>
				</div>
			</div>
			<div class="auth">
				<a href="/login">
					<button class="logout-btn">Log In</button>
				</a>
			</div>
		</div>
	{/if}
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

	.logout-btn {
		background-color: #133335;
		color: white;
		font-weight: 700;
		border: none;
		border-radius: 4px;
		padding: 0.5rem 1rem;
		cursor: pointer;
	}
</style>
