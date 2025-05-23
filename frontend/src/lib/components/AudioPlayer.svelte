<script>
    // Ref: https://svelte.dev/playground/93652d40f09a416d9fc177a4ac89b32b?version=3.48.0
	let { audioFile } = $props();

    const playlist = [
		{
			artist: 'Chimalmat',
			name: 'Story Recording',
			audio: `https://www.chosic.com/wp-content/uploads/2022/01/Missing-You.mp3`
		}
	]
	
	let playingState = 'paused'
	let songPlayingIndex = 0
	let song = null

	function togglePlaying() {
		playingState === 'paused'? play() : pause()
	}
	
	function loadSong() {
		song = new Audio(playlist[songPlayingIndex].audio)
		song.volume = 0.2
		song.play()		
	}

	function play() {
		if (playingState === 'playing') {
			pause()
		}
		
		playingState = 'playing'
		loadSong()
	}
	
	function playSelectedSong(event) {		
		const songIndex = +event.target.dataset.index
		
		if (songIndex === songPlayingIndex) {
			songPlayingIndex = null
			return pause()
		}
		
		songPlayingIndex = songIndex
		play()
	}

	function pause() {
		playingState = 'paused'
		song.pause()
	}

	function previous() {
		if (songPlayingIndex <= 0) return
		songPlayingIndex -= 1
		play()
	}

	function next() {
		if (songPlayingIndex >= playlist.length - 1) return
		songPlayingIndex += 1
		play()
	}
</script>

<div class="player">
	<div class="playlist">	
		{#each playlist as song, index}
			<div class:playing={index === songPlayingIndex} class="song">
				<span>{index + 1}.</span> 
				<button data-index={index} on:click={playSelectedSong}>
					{playingState === 'playing' && index === songPlayingIndex ? '⏯️' : '▶️'}
				</button>
				<span>{song.name} - {song.artist}</span>
			</div>
		{/each}
	</div>

	<div class="controls">		
		<button on:click={previous}>⏪️</button>
		<button on:click={togglePlaying}>
			{playingState === 'paused' ? '▶️' : '⏯️'}
		</button>
		<button on:click={next}>⏩</button>
	</div>
</div>

<style>
	button {
		margin: 0;
		padding: 0;
		font-size: 1.4rem;
		font-weight: 700;
		background: none;
		border: none;
		cursor: pointer;
	}
	
	.player {
		color:  #f2f1f0;
		background-color: #133335;;
		border-radius: 8px;
		object-fit: contain;

	}

	.playlist {
		padding: 1rem;
	}
	
	.song {
		display: flex;
		align-items: center;
		padding: 1rem;
	}
	
	.song button {
		padding: 0 0.4rem;
	}
	
	.controls {
		display: flex;
		justify-content: center;
		gap: 24px;
		padding: 1rem 0;
		border-top: 1px solid hsl(220 20% 28%);
	}
	
	.controls button {
		font-size: 2rem;
	}
	
	.playing {
		color: #000000;
		background-color: #ede8eb;
		border-radius: 8px;
	}
</style>