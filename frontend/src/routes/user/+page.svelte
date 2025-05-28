<script>
	// assets
	import thread from '$lib/assets/illustrations/thread1.png';

	import UserProfile from '$lib/components/UserProfile.svelte';

	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { accessToken, refreshToken } from '$lib/store.js';
	import CreateButton from '$lib/components/CreateButton.svelte';
	import DeleteButton from '$lib/components/DeleteButton.svelte';

	let userData = $state({
		first_name: 'Loading...',
		last_name: '',
		email: 'Loading...',
		data_added: 'Loading...'
	});
	let orgData = $state([
		{
			name: 'Loading...',
			description: 'Loading...',
			project_count: 0,
			story_count: 0,
			date: 'Loading...'
		}
	]);
	let orgLoaded = $state(false);
	let themeColor = $state('#133335');
	let initialLoad = $state(true); // To handle initial loading state
	$inspect(userData);
	$inspect(orgData);

	onMount(async () => {
		try {
			// first get user data
			const userResponse = await authRequest(`/user`, 'GET', $accessToken, $refreshToken);

			// Check for user errors
			if (userResponse?.error) {
				showError('USER_NOT_FOUND');
				return;
			} else {
				userData = userResponse.data;
				initialLoad = false;
			}

			if (userResponse.newAccessToken) {
				console.log('New access token received:', userResponse.newAccessToken);
				accessToken.set(userResponse.newAccessToken);
			}

			// then get org data
			const org_ids = userData.orgs.map((org) => org.org_id);

			// get project info from all projects concurrently
			const orgPromises = org_ids.map((org_ids) =>
				authRequest(`/org/${org_ids}`, 'GET', $accessToken, $refreshToken)
			);

			const orgResponses = await Promise.all(orgPromises);

			// Check for org errors in responses
			for (const response of orgResponses) {
				if (response?.error) {
					showError('ORG_NOT_FOUND');
					return;
				}
			}

			// Extract project data from the responses
			orgData = orgResponses.map((response) => {
				const org = response.data;
				return {
					...org,
					isOpen: false
				};
			});
			orgLoaded = true;
		} catch (error) {
			console.error('Unexpected error loading user page:', error);
			showError('INTERNAL_ERROR');
			orgLoaded = false;
		}
	});

	const addOrg = (org) => {
		orgData = [{ ...org }, ...orgData];
	};
</script>

<svelte:head>
	<title>User Profile</title>
</svelte:head>

{#if initialLoad}
	<div class="section">
		<div class="container">
			<div class="columns is-centered">
				<div class="column is-half has-text-centered">
					<img
						src={thread}
						alt="Loading thread illustration"
						style="width: 50px; height: auto;"
						class="spinning-thread mb-3"
					/>
					<p class="is-size-5 has-text-weight-bold">Loading...</p>
				</div>
			</div>
		</div>
	</div>
	<style>
		.spinning-thread {
			animation: spinY 2s linear infinite;
		}
		@keyframes spinY {
			0% {
				transform: rotateY(0deg);
			}
			100% {
				transform: rotateY(360deg);
			}
		}
	</style>
{:else}
	<div class="container">
		<div class="breadcrumb-nav mb-5 mt-3">
			<nav class="breadcrumb nav-color" aria-label="breadcrumbs">
				<ul>
					<li><a href="/">Home</a></li>
					<li class="is-active">
						<a href="/user" aria-current="page">Profile Page</a>
					</li>
				</ul>
			</nav>
		</div>
		<div class="p-5">
			<UserProfile user={userData} />
		</div>
		<hr />
		<div class="container mt-5">
			<h2 class="title is-4">Organizations</h2>

			<div class="mb-5">
				<button
					class="button is-primary is-medium"
					style="background-color: #56BDB3;"
					onclick={() => {
						orgData = [
							{
								name: '',
								description: '',
								isOpen: true,
								isNew: true
							},
							...orgData
						];
					}}
				>
					<span class="icon">
						<i class="fa fa-plus"></i>
					</span>
					<span>Add New Organization</span>
				</button>
			</div>

			{#if !orgLoaded}
				<div class="skeleton-block mb-6"></div>
			{:else}
				{#each orgData as org, i}
					<div class="card mb-4">
						<header class="card-header">
							<div class="card-header-title is-justify-content-space-between is-flex-wrap-wrap">
								<div class="is-flex is-flex-direction-column is-align-items-flex-start">
									<p class="mb-1 is-size-4">{org.name}</p>
									<p class="is-size-6 has-text-grey">{org.description}</p>
								</div>
								<div class="is-flex is-flex-direction-column is-align-items-flex-end">
									<p class="mb-1 is-size-5"><strong>{org.project_count}</strong> Projects</p>
									<p class="mb-1 is-size-5"><strong>{org.story_count}</strong> Stories</p>
									<p class="is-size-6 has-text-grey">Created: {org.date}</p>
								</div>
							</div>
							<button
								class="card-header-icon is-size-5"
								aria-label="more options"
								onclick={() => (org.isOpen = !org.isOpen)}
								style="background-color: {themeColor}; color: white; border-radius: 5px;"
							>
								Edit
								<span class="icon">
									<i class="fa fa-angle-down" aria-hidden="true" class:is-rotated={org.isOpen}></i>
								</span>
							</button>
						</header>

						{#if org.isOpen}
							<div class="card-content">
								<div class="field">
									<label class="label">Organization Name</label>
									<div class="control">
										<input
											class="input"
											type="text"
											bind:value={org.name}
											required
											placeholder="Organization name"
										/>
									</div>
								</div>

								<div class="field">
									<label class="label">Description</label>
									<div class="control">
										<textarea
											class="textarea"
											bind:value={org.description}
											placeholder="Organization description"
										></textarea>
									</div>
								</div>
								<div class="field is-grouped mt-4">
									<div class="control mr-2">
										<CreateButton type="org" bind:data={orgData[i]} redirectPath="/user" />
									</div>
									<div class="control mr-2">
										<button
											class="button is-light"
											onclick={() => {
												if (org.isNew) {
													orgData = orgData.filter((_, index) => index !== i);
												} else {
													org.isOpen = false;
												}
											}}
										>
											Cancel
										</button>
									</div>
									<div class="control">
										<DeleteButton type="org" id={org.org_id} redirectPath="/user" />
									</div>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>
	</div>
{/if}

<style>
	.is-rotated {
		transform: rotate(180deg);
	}

	.breadcrumb a {
		color: black;
	}

	.breadcrumb a.is-active {
		color: var(--dark_blue) !important;
	}
</style>
