<script>
	import StoryHolder from '$lib/components/story/StoryHolder.svelte';
	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { accessToken, refreshToken } from '$lib/store.js';

	const org_id = $page.params.org_id;

	let projects = $state([
		{
			project_name: 'Loading...',
			description: 'Loading...',
			stories: 0,
			required_tags: [],
			optional_tags: []
		}
	]);

	$inspect(projects);

	// get all projects that a user is part of
	onMount(async () => {
		try {
			const orgResponse = await authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken);

			// Check for org errors
			if (orgResponse?.error) {
				showError(orgResponse.error.code === 'ORG_NOT_FOUND' ? 'ORG_NOT_FOUND' : orgResponse.error);
				return;
			}

			const orgData = orgResponse.data;
			const project_ids = orgData.project_ids;

			// get project info from all projects concurrently
			const projectPromises = project_ids.map((project_id) =>
				authRequest(`/project/${project_id}`, 'GET', $accessToken, $refreshToken)
			);

			const projectResponses = await Promise.all(projectPromises);

			// Check for project errors in responses
			for (const response of projectResponses) {
				if (response?.error) {
					showError('PROJECT_NOT_FOUND');
					return;
				}
			}

			// Extract project data from the responses
			projects = projectResponses.map((response) => {
				return response.data;
			});
		} catch (error) {
			console.error('Unexpected error loading new story page:', error);
			showError('INTERNAL_ERROR');
		}
	});
</script>

<svelte:head>
	<title>Add Story</title>
</svelte:head>

<div class="page-container is-flex is-flex-direction-column is-align-items-center p-5 is-fullwidth">
	<StoryHolder {projects} />
</div>

<style>
	.page-container {
		background-image: url('$lib/assets/background_texture.png');
		min-height: 100vh; /* so that container takes up the full height */
	}
</style>
