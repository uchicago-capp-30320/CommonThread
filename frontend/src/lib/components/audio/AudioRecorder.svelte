<script>
	import { onMount, tick } from 'svelte';
	
	let { 
		disabled = false,
		onAudioRecorded = () => {},
		onAudioCleared = () => {}
	} = $props();
	
	let media = [];
	let mediaRecorder = null;
	let isRecording = $state(false);
	let recordedAudioURL = $state(null);
	let recordingDuration = $state(0);
	let recordingInterval = null;
	let audioElement = null;
	let stream = null;
	
	async function setupMediaRecorder() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			mediaRecorder = new MediaRecorder(stream);
			
			mediaRecorder.ondataavailable = (e) => media.push(e.data);
			
			mediaRecorder.onstop = async function() {
				const blob = new Blob(media, { 'type': 'audio/ogg; codecs=opus' });
				recordedAudioURL = window.URL.createObjectURL(blob);
				
				const audioFile = new File([blob], `recording-${Date.now()}.ogg`, {
					type: 'audio/ogg'
				});
				
				await tick();
				
				if (audioElement) {
					audioElement.src = recordedAudioURL;
					audioElement.load();
				}
				
				onAudioRecorded({ audioFile, audioURL: recordedAudioURL });
				media = [];
			};
			
			return true;
		} catch (error) {
			console.error('Error accessing microphone:', error);
			alert('Unable to access microphone. Please ensure microphone permissions are granted.');
			return false;
		}
	}
	
	async function startRecording() {
		if (disabled) return;
		
		if (!mediaRecorder) {
			const success = await setupMediaRecorder();
			if (!success) return;
		}
		
		if (mediaRecorder && !isRecording) {
			mediaRecorder.start();
			isRecording = true;
			recordingDuration = 0;
			
			recordingInterval = setInterval(() => {
				recordingDuration++;
			}, 1000);
		}
	}
	
	function stopRecording() {
		if (mediaRecorder && isRecording) {
			mediaRecorder.stop();
			isRecording = false;
			
			if (recordingInterval) {
				clearInterval(recordingInterval);
				recordingInterval = null;
			}
		}
	}
	
	function clearRecording() {
		recordedAudioURL = null;
		recordingDuration = 0;
		onAudioCleared();
	}
	
	onMount(() => {
		return () => {
			if (stream) {
				stream.getTracks().forEach(track => track.stop());
			}
		};
	});
	
	function formatTime(seconds) {
		const minutes = Math.floor(seconds / 60);
		const remainingSeconds = seconds % 60;
		return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
	}
</script>

<div class="recorder-container" class:disabled>
	{#if disabled}
		<p class="help has-text-grey">Recording disabled - audio file already uploaded</p>
	{/if}
	
	<div class="recorder-controls">
		{#if !isRecording && !recordedAudioURL}
			<button 
				class="button is-primary is-small" 
				onclick={startRecording}
				disabled={disabled}
			>
				<span class="icon is-small">
					<i class="fa fa-microphone"></i>
				</span>
				<span>Start Recording</span>
			</button>
		{:else if isRecording}
			<div class="recording-status">
				<button 
					class="button is-danger is-small" 
					onclick={stopRecording}
				>
					<span class="icon is-small">
						<i class="fa fa-stop"></i>
					</span>
					<span>Stop Recording</span>
				</button>
				<div class="recording-indicator">
					<span class="recording-dot"></span>
					<span class="recording-time">{formatTime(recordingDuration)}</span>
				</div>
			</div>
		{:else if recordedAudioURL}
			<div class="recorded-audio">
				<audio controls bind:this={audioElement}></audio>
				<button 
					class="button is-warning is-small ml-2" 
					onclick={clearRecording}
				>
					<span class="icon is-small">
						<i class="fa fa-trash"></i>
					</span>
				</button>
				<button 
					class="button is-primary is-small ml-2" 
					onclick={startRecording}
				>
					<span class="icon is-small">
						<i class="fa fa-microphone"></i>
					</span>
					<span>Record Again</span>
				</button>
			</div>
		{/if}
	</div>
</div>

<style>
	.recorder-container {
		margin-top: 0.75rem;
	}
	
	.recorder-container.disabled {
		opacity: 0.6;
	}

	.recording-status {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.recording-indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #e74c3c;
		font-weight: 600;
	}

	.recording-dot {
		width: 8px;
		height: 8px;
		background-color: #e74c3c;
		border-radius: 50%;
		animation: pulse 1.5s infinite;
	}

	@keyframes pulse {
		0% {
			transform: scale(1);
			opacity: 1;
		}
		50% {
			transform: scale(1.2);
			opacity: 0.7;
		}
		100% {
			transform: scale(1);
			opacity: 1;
		}
	}

	.recorded-audio {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.recorded-audio audio {
		flex: 1;
		min-width: 200px;
	}

	.recording-time {
		font-family: 'Courier New', monospace;
		font-size: 0.9rem;
	}
</style>