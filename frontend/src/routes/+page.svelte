<script>
    import background_texture from '$lib/background_texture.png';
    import thread1 from '$lib/illustrations/thread1.png';
    import thread2 from '$lib/illustrations/thread2.png';
    import thread3 from '$lib/illustrations/thread3.png';
    import { slide } from 'svelte/transition';
    import { onMount, onDestroy } from 'svelte';



    let greetings = ['Impact', 'Community', 'Stories', 'Connection', 'Growth'];
	let index = $state(0);
	let roller;

    onMount(() => {
		roller = setInterval(() => {
			if (index === greetings.length - 1) index = 0;
			else index++;
		}, 3000);
	});
    
    onDestroy(() => {
		clearInterval(roller);
	});
</script>

<div id = "container">
    <div class="banner">
        <img src="{background_texture}" alt="">
        <div class="content">
            <div class="welcome-text">
                
                    <p>Weaving Together <br>Your Stories for </p>
                    {#key index}
                    <p class = 'rotate' transition:slide>{greetings[index]}</p> 
                    {/key}
            </div>
            <div class="welcome-image">
                    <img src="{thread1}" alt="Thread illustration 1">
                    <img src="{thread3}" alt="Thread illustration 3">
                </div>

            </div>
        </div>
    </div>
    



<style>
    .banner {
        height: 600px;
        z-index: -1;
        position: relative;
        overflow: hidden;
    }

    .banner img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .content {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 5%;
    }
   
    .welcome-text {
        flex: 1;
        font-size: 4rem;
        color: #fff;
        width: 500px;
        line-height: normal;
    }

    .welcome-text p {
        margin: 0;

    }

    .rotate {
        transition: transform 0.5s ease-in-out;
        font-style: italic;
        color: var(--green);
        font-weight: bold;
    
    }
    .welcome-image {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .welcome-image img {
        height: 40%;
        max-height: 300px;
        width: auto;
        margin: 0 10px;
    }

</style>