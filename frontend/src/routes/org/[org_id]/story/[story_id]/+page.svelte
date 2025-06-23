<script>
	// assests
	import thread from '$lib/assets/illustrations/thread1.png';

	// Imports
	import StoryFullView from '$lib/components/StoryFullView.svelte';
	import AudioPlayer from '$lib/components/audio/AudioPlayer.svelte';
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import Chatbox from '$lib/components/Chatbox.svelte'; // Added Chatbox import
	import { accessToken, refreshToken } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { showError } from '$lib/errorStore.js';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	// Page state
	let themeColor = $state('#133335');
	let loading = $state(true);

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
		storyteller: '...',
		project_name: '...',
		curator: '...',
		text_content: 'Loading...',
		summary: 'Loading...'
	});

	$inspect(orgData);
	$inspect(storyData);

feat/project-chat-perplexity
	// Construct chat API endpoint
	console.log('Story Page - $page.params.story_id:', $page.params.story_id);
	const story_id_for_endpoint = $page.params.story_id; // Ensure story_id is explicitly defined for clarity
	const chatApiEndpoint = `/story/${story_id_for_endpoint}/chat`;
	console.log('Story Page - constructed chatApiEndpoint:', chatApiEndpoint);

	onMount(async () => {
		try {
			console.log('Making requests for org:', org_id, 'story:', story_id);

			const [orgResponse, storyResponse] = await Promise.all([
				authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
				authRequest(`/story/${story_id}`, 'GET', $accessToken, $refreshToken)
			]);

			console.log('orgResponse:', orgResponse);
			console.log('storyResponse:', storyResponse);

			// Check for org errors
			if (orgResponse?.error) {
				showError(orgResponse.error.code === 'ORG_NOT_FOUND' ? 'ORG_NOT_FOUND' : orgResponse.error);
				loading = false;
				return;
			}

			// Check for story errors
			if (storyResponse?.error) {
				console.log('Story error detected:', storyResponse.error);
				console.log('Calling showError with:', 'STORY_NOT_FOUND', { org_id });

				if (storyResponse.error.code === 'STORY_NOT_FOUND') {
					showError('STORY_NOT_FOUND', null, { org_id });
				} else {
					showError(storyResponse.error.code);
				}
				loading = false;
				return;
			}

			// Check if responses are null (handled by authRequest)
			if (!orgResponse || !storyResponse) {
				loading = false;
				return;
			}

			// Success - update data
			if (orgResponse.newAccessToken) {
				accessToken.set(orgResponse.newAccessToken);
			}

			orgData = orgResponse.data;
			storyData = storyResponse.data;

			includesAudio = storyData.audio_path != '';
			includesImage = storyData.image_path != '';
			if (includesAudio || includesImage) media = true;

			loading = false;
		} catch (error) {
			console.error('Unexpected error loading story:', error);
			showError('INTERNAL_ERROR');
			loading = false;
		}
	});
</script>

<!-- Just show loading or content - modal handles errors -->
{#if loading}
	<div class="loading-container">
		<div class="has-text-centered">
			<img
				src={thread}
				alt="Loading thread illustration"
				style="width: 50px; height: auto;"
				class="spinning-thread"
			/>
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
			<p><b>Loading...</b></p>
		</div>
	</div>
{:else}
	<!-- Show normal content -->
	<div id="container" class="mb-6">
		<!-- NAVIGATION BAR  -->
		<div class="has-text-left mb-3">
			<a href="/org/{orgData.org_id}" class="button is-light">
				<span class="icon">
					<i class="fa fa-arrow-left"></i>
				</span>
				<span>Back to Organization</span>
			</a>
		</div>
		<div class="breadcrumb-nav mb-5 mt-3">
			<nav class="breadcrumb nav-color" aria-label="breadcrumbs">
				<ul>
					<li><a href="/">Home</a></li>
					<li>
						<a href="/org/{orgData.org_id}"><b>Organization</b>: {orgData.name || 'Organization'}</a
						>
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
				<!-- STORY TEXT -->
				{#if media}
					<div class="column is-three-quarters" id="text">
						<StoryFullView story={storyData}></StoryFullView>
					</div>
				{:else}
					<div class="column is-full">
						<StoryFullView story={storyData}></StoryFullView>
					</div>
				{/if}

				<!-- AUDIOVISUAL MEDIA -->
				{#if media}
					<div class="column is-one-quarter" id="media">
						<!-- Are we displaying a single image or multiple? -->
						<div class="row">
							{#if includesAudio}
								<div class="media-right" id="audio">
									<AudioPlayer src={storyData.audio_path} storyteller={storyData.storyteller}
									></AudioPlayer>
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
			</div>
		</div>
	</div>
{/if}

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

	.story-chat-container {
		margin-top: 30px; /* Increased margin-top */
		padding: 20px;    /* Increased padding */
		border: 1px solid #ddd; /* Slightly darker border */
		border-radius: 8px; /* Added border-radius for rounded corners */
		background-color: #f9f9f9; /* Light background color for the container */
		max-width: 700px; /* Max width for the chat container */
		margin-left: auto; /* Center the chat container */
		margin-right: auto; /* Center the chat container */
	}

	.story-chat-container h3 {
		font-size: 1.5em;
		color: #333;
		margin-bottom: 15px;
		text-align: center;
	}

	#images {
		/* max-height: 300px; */
		max-width: 100%;
		/* margin: 0 10px; */
		object-fit: contain;
	}

	/* #media {
		display: flex; 
		} */

	.row {
		width: 100%;
		padding-bottom: 20%;
	}

	#audio {
		/* display:flex; */
		/* object-fit: contain; */
		width: 100%;
	}

	li a {
		color: black;
	}

	li a:hover {
		color: #56bcb3;
	}

	li.is-active a {
		color: #56bcb3 !important;
	}

	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 50vh;
		padding: 2rem;
	}
</style>

<!-- Chatbox Integration -->
<div class="story-chat-container">
	<h3>Chat about this Story</h3>
	<Chatbox {chatApiEndpoint} />
</div>
