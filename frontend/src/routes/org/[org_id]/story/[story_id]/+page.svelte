<script>
	// Imports
	import StoryFullView from '$lib/components/StoryFullView.svelte';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import { accessToken, refreshToken } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	// Page state
	let themeColor = $state('#133335');

	// Fetch the data when the component mounts
	const org_id = $page.params.org_id;
	const story_id = $page.params.story_id;
	let media = $state(false);
	let includesAudio = $state(false);
	let includesImage = $state(false);
	$inspect(includesImage);

	// Org state
	let orgData = $state({
		orgName: 'Loading...',
		description: 'Loading...',
		projectsTotal: 0,
		storiesTotal: 0
	});

	// Story page
	let storyData = $state({
		storyteller: 'Loading...',
		project_name: 'Loading...',
		curator: 'Loading...',
		text_content: 'Loading...',
		summary: 'Loading...'
	});

	$inspect(orgData);
	$inspect(storyData);

	// API call
	onMount(async () => {
		// Make both requests concurrently using Promise.all
		const [orgResponse, storyResponse] = await Promise.all([
			authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/story/${story_id}`, 'GET', $accessToken, $refreshToken)
		]);

		if (orgResponse.newAccessToken) {
			accessToken.set(orgResponse.newAccessToken);
		}

		orgData = orgResponse.data;
		storyData = storyResponse.data;

		includesAudio = storyData.audio_path != '';
		includesImage = storyData.image_path != '';
		if (includesAudio || includesImage) media = true;
	});
</script>

<div id="container" class="mb-6">
	<div class="breadcrumb-nav mb-5 mt-3">
		<nav class="breadcrumb nav-color" aria-label="breadcrumbs">
			<ul>
				<li><a href="/">Home</a></li>
				<li>
					<a href="/org/{orgData.org_id}"><b>Organization</b>: {orgData.name || 'Organization'}</a>
				</li>
				<li class="">
					<a href="/org/{orgData.org_id}/project/{storyData.project_id}" aria-current="page"
						><b>Project</b>: {storyData.project_name}</a
					>
				</li>
				<li class="is-active">
					<a href="/org/{orgData.org_id}/story/{story_id}" aria-current="page"
						><b>Story</b>: {story_id}</a
					>
				</li>
			</ul>
		</nav>
	</div>
	<div class="container-is-fullhd">
		<div class="columns">
			<div class="column is-1"></div>
			{#if media}
				<div class="column is-6">
					<StoryFullView story={storyData}></StoryFullView>
				</div>
			{:else}
				<div class="column is-10">
					<StoryFullView story={storyData}></StoryFullView>
				</div>
			{/if}

			{#if media}
				<div class="column">
					<!-- Are we displaying a single image or multiple? -->
					<div class="row">
						{#if includesAudio}
							<div class="media">
								<div class="media-right" id="audio">
									<div class="audio">
										<AudioPlayer src={storyData.audio_path}></AudioPlayer>
									</div>
								</div>
							</div>
						{/if}
						{#if includesImage}
							<div class="media">
								<div class="media-right" id="images">
									<img src={storyData.image_path} alt="Story image" />
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}
			<div class="column is-1"></div>
		</div>
	</div>
</div>

<style>
	p {
		padding: 10%;
	}

	#container {
		margin-top: 50px;
		width: 90%;
		height: 90%;
		margin-left: auto;
		margin-right: auto;
		justify-content: center;
	}

	#images {
		/* max-height: 300px; */
		max-width: 100%;
		/* margin: 0 10px; */
		object-fit: contain;
	}

	.audio {
		object-fit: contain;
	}

	li a {
		color: black;
	}

	li.is-active {
		color: #133335 !important;
	}
</style>
