<script>
    // Imports 
    import StoryFullView from '$lib/components/StoryFullView.svelte'
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
    const story_id = $page.params.story_id
    let media = $state(false);

    // Org state 
    let orgData = $state({
		orgName: 'Loading...',
		description: 'Loading...',
		projectsTotal: 0,
		storiesTotal: 0
	});

    // Story page 
    let storyData = $state({
        "storyteller": "Loading...", 
        "project_name": "Loading...", 
        "curator": "Loading...", 
        "text_content": "Loading...", 
        "summary": "Loading..."
    });


    $inspect(orgData);
	$inspect(storyData);

    // API call
    onMount(async () => {
		// Make both requests concurrently using Promise.all
		const [orgResponse, storyResponse] = await Promise.all([
            authRequest(`/org/${org_id}`, 'GET', $accessToken, $refreshToken),
			authRequest(`/story/${story_id}`, 'GET', $accessToken, $refreshToken),
		]);

		if (orgResponse.newAccessToken) {
			accessToken.set(orgResponse.newAccessToken);
		}

		orgData = orgResponse.data;
        storyData = storyResponse.data;

        let includesAudio = (storyData.audio_path != "")
        let includesImage = (storyData.image_path != "")
        if (includesAudio || includesImage) media = true; 

	});

</script>

<div class="breadcrumb-nav mb-5 mt-3">
    <nav class="breadcrumb nav-color" aria-label="breadcrumbs">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/org/{orgData.org_id}">{orgData.name || 'Organization'}</a></li>
            <li class="is-active">
                <a href="/org/{orgData.org_id}/admin" aria-current="page">Admin Page</a>
            </li>
        </ul>
    </nav>
</div>

<div id="container">
    <div class="container-is-fullhd">
        <div class="columns">
            <div class="column is-1">
            </div>
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
                                <div class = "media-right" id = "audio">
                                    <div class="audio">
                                        <AudioPlayer></AudioPlayer>
                                    </div>
                                </div>
                            </div>
                        {/if}
                        {#if includesAudio}
                            <div class="media">
                                <div class = "media-right" id="images">
                                    <figure>
                                        <img src={sampleImage} alt="Thread illustration 3" />
                                        <figcaption>Figure 1</figcaption>
                                    </figure>
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>  
            {/if}

            <div class="column is-1">
            </div>
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

    img {
        /* max-height: 300px; */
        /* width: auto; */
        width: 80%;

        /* margin: 0 10px; */
        object-fit: contain;
    }
    .audio {
        object-fit: contain;
    }


</style>