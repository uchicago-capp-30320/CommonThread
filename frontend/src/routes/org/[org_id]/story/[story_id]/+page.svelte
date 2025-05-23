<script>
	import OrgHeader from '$lib/components/OrgHeader.svelte';
	import AudioPlayer from '$lib/components/AudioPlayer.svelte';
	// import AudioPlayer from '$lib/components/audio/AudioPlayer.svelte'
	import { accessToken, refreshToken } from '$lib/store.js';
	import { onMount } from 'svelte';
	import { authRequest } from '$lib/authRequest.js';
	import { page } from '$app/stores';

	import StoryFullView from '$lib/components/StoryFullView.svelte';
	import thread3 from '$lib/assets/illustrations/thread3.png';
	// import sampleImage from '$lib/assets/sample/popol-vuh.jpg'
	import sampleImage from '$lib/assets/sample/Popol-Vuh.webp';

	let themeColor = $state('#133335');
	let saveResponse = $state('...');
	let orgData = $state({
		orgName: 'Loading...',
		description: 'Loading...',
		projectsTotal: 0,
		storiesTotal: 0
	});

	let story = $state({
		story_id: 1,
		storyteller: 'Chimalmat',
		project_id: 1,
		project_name: 'Popol Vuh',
		curator: 'Francisco Ximénez',
		text_content:
			'Over a universe wrapped in the gloom of a dense and primeval night passed the god Hurakan, the mighty wind. He called out “earth,” and the solid land appeared. The chief gods took counsel; they were Hurakan, Gucumatz, the serpent covered with green feathers, and Xpiyacoc and Xmucane, the mother and father gods. As a result of their deliberations animals were created. But as yet man was not. To supply the deficiency the divine beings resolved to create mannequins carved out of wood. But these soon incurred the displeasure of the gods, who, irritated by their lack of reverence, resolved to destroy them. Then by the will of Hurakan, the Heart of Heaven, the waters were swollen, and a great flood came upon the mannequins of wood. They were drowned and a thick resin fell from heaven. The bird Xecotcovach tore out their eyes; the bird Camulatz cut off their heads; the bird Cotzbalam devoured their flesh; the bird Tecumbalam broke their bones and sinews and ground them into powder. Because they had not thought on Hurakan, therefore the face of the earth grew dark, and a pouring rain commenced, raining by day and by night. Then all sorts of beings, great and small, gathered together to abuse the men to their faces. The very household utensils and animals jeered at them, their mill-stones, their plates, their cups, their dogs, their hens. Said the dogs and hens, “Very badly have you treated us, and you have bitten us. Now we bite you in turn.” Said the mill-stones (metates, large hollowed stones used for grinding maize), ” Very much were we tormented by you, and daily, daily, night and day, it was squeak, screech, screech, for your sake. Now you shall feel our strength, and we will grind your flesh and make a meal of your bodies.” And the dogs upbraided the mannequins because they had not been fed, and tore the unhappy images with their teeth. And the cups and dishes said, “Pain and misery you gave us, smoking our tops and sides, cooking us over the fire burning and hurting us as if we had no feeling. Now it is your turn, and you shall burn.” Then ran the mannequins hither and thither in despair. They climbed to the roofs of the houses, but the houses crumbled under their feet; they tried to mount to the tops of the trees, but the trees hurled them from them; they sought refuge in the caverns, but the caverns closed before them. Thus was accomplished the ruin of this race, destined to be overthrown. And it is said that their posterity are the little monkeys who live in the woods.',
		audio_path: '',
		image_path: '',
		summary: "The Popol Vuh is a foundational sacred narrative of the Kich'e people ",
		tags: [
			{ name: 'Nation', value: 'Mayan' },
			{ name: 'Regions', value: 'Quintana Roo, Guatemala, El Salvador' }
		]
	});

	let projectResponses = $state([]);

	$inspect(orgData);

	const org_id = $page.params.org_id;
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
			<div class="column is-1"></div>
			<div class="column is-6">
				<StoryFullView {story}></StoryFullView>
			</div>

			<div class="column">
				<!-- Are we displaying a single image or multiple? -->
				<div class="row">
					<div class="media">
						<div class="media-right" id="audio">
							<div class="audio">
								<AudioPlayer></AudioPlayer>
							</div>
						</div>
					</div>
					<div class="media-right" id="images">
						<figure>
							<img src={sampleImage} alt="Thread illustration 3" />
							<figcaption>Figure 1</figcaption>
						</figure>
					</div>
				</div>
			</div>

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
