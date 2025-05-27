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

	// Initialize state
	let loading = $state(true);
	let authorized = $state(false);
	let dActive = $state(false);
	let orgs = $state([]);
	let org_id = $state(null);
	let isHome = $state(page.url.pathname === '/');
	let first_name = $state(null);

	// URL parameters
	if (page.url.pathname.includes('org/')) {
		org_id = page.params.org_id;
	}

	// Define functions
	const getOrgs = async () => {
		const userRequest = await authRequest(`/user`, 'GET', $accessToken, $refreshToken);
		console.log('userRequest', userRequest);
		if (org_id) {
			orgs = userRequest.data.orgs.filter((org) => org.org_id !== org_id);
		} else {
			orgs = userRequest.data.orgs;
		}
		first_name = userRequest.data.first_name;
		authorized = true;
	};

	const logOut = () => {
		console.log('Print log out');
		accessToken.set('');
		refreshToken.set('');
		authorized = false;
		// redirect to login page
		window.location.href = '/login';
	};

	// Mount
	onMount(async () => {
		// Tasks to be executed right when the page is rendered
		// Check authorization
		const now = new Date();
		const expirationDate = new Date($userExpirationTimestamp);

		if (now > expirationDate || $accessToken == '') {
			console.log('User token expired');
		} else {
			console.log('User token is valid');
			getOrgs();
		}

		loading = false;
	});
</script>

<header class="header">
	<div class="logo">
		<a href="/">
			<img src={logo} alt="Common Thread Logo" />
		</a>
	</div>
	{#if !loading}
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
					<a href="/signup">
						<button class="signup-btn">Sign Up</button>
					</a>
				</div>
			</div>
		{:else}
			<div class="right-section">
				<div class="dropdown {dActive ? 'is-active' : ''}">
					<div class="dropdown-trigger">
						<button
							class="login-btn"
							aria-haspopup="true"
							aria-controls="dropdown-menu"
							onclick={() => {
								dActive = !dActive;
							}}
						>
							<span>{isHome ? 'Choose Organization' : 'Change Organization'}</span>
							<span class="icon">
								<i class="fa fa-angle-down" aria-hidden="true"></i>
							</span>
						</button>
					</div>
					<div class="dropdown-menu" id="dropdown-menu" role="menu" hidden>
						<div class="dropdown-content">
							{#each orgs as org}
								<div class="m-2">
									<a href="/org/{org.org_id}" target="_self" class="dropdown-item">
										<div class="org-item">
											<span class="org-name">{org.org_name}</span>
											<span class="icon is-small">
												<i class="fa fa-arrow-right" aria-hidden="true"></i>
											</span>
										</div>
									</a>
								</div>
							{/each}
						</div>
					</div>
				</div>

				<div class="auth">
					<button onclick={logOut} class="logout-btn">Log Out</button>
				</div>
				<div class="user-greeting">
					<a href="/user" class="is-flex is-align-items-center">
						<span class="icon mr-2">
							<i class="fa fa-user-circle"></i>
						</span>
						<span>Hi, {first_name}</span>
					</a>
				</div>
			</div>
		{/if}
	{/if}
</header>

<style>
	a {
		text-decoration: none;
		color: inherit;
		margin: 0;
		padding: 0;
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
		height: 10vh;
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

	.signup-btn {
		background-color: #133335;
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
