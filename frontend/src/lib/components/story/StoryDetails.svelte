<script>
	import { text } from '@sveltejs/kit';
	import AudioRecorder from '../audio/AudioRecorder.svelte';

	let { currentStep = $bindable(), storyData = $bindable(), projects } = $props();
	let wordCount = $derived(storyData.text_content.trim().split(/\s+/).length);
	let required;
	let optional;

	let project = $derived(
		projects.filter((project) => project.project_id === storyData.project_id)[0]
	);

	if (project.required_tags.length === 0) {
		required = [];
	} else {
		required = project.required_tags.map((tag) => ({
			id: tag,
			label: tag
		}));
	}

	if (project.optional_tags.length === 0) {
		optional = [];
	} else {
		optional = project.optional_tags.map((tag) => ({
			id: tag,
			label: tag
		}));
	}

	let tagCategories = $state({ required: required, optional: optional });
	let selectedOptionalCategory = $state(optional[0]?.id || '');
	let optionalTagValue = $state('');
	let textActive = $state(true);
	let audioActive = $state(false);

	// Add these new state variables to track audio source
	let hasUploadedAudio = $derived(storyData.audio && !storyData.audio.name?.startsWith('recording-'));
	let hasRecordedAudio = $derived(storyData.audio && storyData.audio.name?.startsWith('recording-'));

	$inspect(tagCategories, textActive, audioActive);

	function getTagMap() {
		return new Map((storyData.tags || []).map((tag) => [tag.category, tag]));
	}

	// Read a tag's value
	function getTagValue(categoryId) {
		return getTagMap().get(categoryId)?.value || '';
	}

	// Add or update a tag in one go
	function setTagValue(categoryId, value) {
		const cleanValue = value.trim();
		if (!cleanValue) return;

		const tagsMap = getTagMap();
		const meta = [...tagCategories.required, ...tagCategories.optional].find(
			(c) => c.id === categoryId
		);

		tagsMap.set(categoryId, {
			category: categoryId,
			categoryLabel: meta?.label ?? categoryId,
			value: cleanValue
		});

		storyData = {
			...storyData,
			tags: Array.from(tagsMap.values())
		};
	}

	// Remove by category (works for optional or required)
	function removeTag(categoryId) {
		storyData = {
			...storyData,
			tags: (storyData.tags || []).filter((t) => t.category !== categoryId)
		};
	}

	// Helpers for optional-tag UI
	function addOptionalTag() {
		if (optionalTagValue.trim()) {
			setTagValue(selectedOptionalCategory, optionalTagValue);
			optionalTagValue = '';
		}
	}

	// Validation: ensure all required categories exist and have non-empty values
	function hasAllRequiredTags() {
		const tagsMap = getTagMap();
		return tagCategories.required.every((cat) => tagsMap.has(cat.id) && tagsMap.get(cat.id).value);
	}

	function handleNext() {
		if ((storyData.text_content || storyData.audio) && hasAllRequiredTags()) {
			currentStep = 3;
		}
	}

	// Define callback functions
	function handleAudioRecorded(data) {
		storyData = {
			...storyData,
			audio: data.audioFile
		};
	}
	
	function handleAudioCleared() {
		storyData = {
			...storyData,
			audio: null
		};
	}
</script>

<div class="box">
	<h2 class="title is-4 mb-5">Story Details</h2>

	<div class="field">
		<label class="label" for="story-text">Your Story</label>
		<p class="help mb-2">Share your story in your own words. Share either text or an audio file.</p>

		<div class="tabs is-boxed">
			<ul>
				<li class={textActive ? 'is-active' : ''}>
					<a
						onclick={() => {
							if (!storyData.audio && storyData.text_content === '') {
								textActive = !textActive;
								audioActive = !audioActive;
							}
						}}
					>
						<span class="icon is-small"><i class="fa fa-font"></i></span>
						<span>Text</span>
					</a>
				</li>
				<li class={audioActive ? 'is-active' : ''}>
					<a
						onclick={() => {
							if (storyData.text_content === '' && !storyData.audio) {
								audioActive = !audioActive;
								textActive = !textActive;
							}
						}}
					>
						<span class="icon is-small"><i class="fa fa-microphone"></i></span>
						<span>Audio</span>
					</a>
				</li>
			</ul>
		</div>

		<div class="tab-content">
			<!-- Text Tab Content -->
			{#if textActive}
				<div class="control">
					<textarea
						class="textarea"
						id="story-text"
						bind:value={storyData.text_content}
						placeholder="Share your story here..."
						rows="6"
						required
					></textarea>
				</div>
			{:else}
				<!-- Audio Tab Content -->
				<div class="control">
					<div class="file has-name is-fullwidth" class:disabled={hasRecordedAudio}>
						{#if hasRecordedAudio}
							<p class="help has-text-grey mb-2">File upload disabled - audio recording exists</p>
						{/if}
						<label class="file-label">
							<input
								class="file-input"
								type="file"
								accept="audio/*"
								disabled={hasRecordedAudio}
								onchange={(e) => {
									if (e.target.files.length > 0) {
										storyData = {
											...storyData,
											audio: e.target.files[0]
										};
									}
								}}
							/>
							<span class="file-cta" class:disabled={hasRecordedAudio}>
								<span class="file-icon">
									<i class="fa fa-upload"></i>
								</span>
								<span class="file-label">Choose an audio file...</span>
							</span>
							<span class="file-name">
								{storyData.audio?.name || 'No file selected'}
							</span>
						</label>
						{#if hasUploadedAudio}
							<button 
								class="button is-warning is-small mt-2" 
								onclick={() => {
									storyData = { ...storyData, audio: null };
								}}
							>
								<span class="icon is-small">
									<i class="fa fa-trash"></i>
								</span>
								<span>Remove uploaded file</span>
							</button>
						{/if}
					</div>
					
					<!-- Live Recording Component -->
					<div class="mt-3">
						<div class="has-text-centered mb-2">
							<span class="tag is-light">OR</span>
						</div>
						<AudioRecorder 
							disabled={hasUploadedAudio}
							onAudioRecorded={handleAudioRecorded}
							onAudioCleared={handleAudioCleared}
						/>
					</div>
				</div>
			{/if}
		</div>
	</div>
	<div class="is-flex is-justify-content-flex-end mb-2">
		<div class="label mb-0">
			Word count:
			<span class="tag is-link word-count-tag">{wordCount}</span>
		</div>
	</div>

	<!-- Required Tags Section -->
	<div class="field mt-4">
		<div class="label">Required Tags</div>
		{#if Object.keys(tagCategories.required).length === 0}
			<p>No required tags for this project.</p>
		{:else}
			<div class="tags mb-3">
				{#each storyData.tags as tag, index}
					{#if tagCategories.required.some((cat) => cat.id === tag.category)}
						<span class="tag is-medium">
							<strong class="mr-1">{tag.categoryLabel}:</strong>
							{tag.value}
							<button class="delete is-small ml-2" onclick={() => removeTag(index)}></button>
						</span>
					{/if}
				{/each}
			</div>
			{#each tagCategories.required as cat}
				<div class="required-tag-row mb-2">
					<label class="label mb-0 required-tag-label"
						>{cat.label}
						<input
							class="input is-rounded is-small required-tag-input compact-input"
							type="text"
							placeholder={'Enter ' + cat.label}
							value={getTagValue(cat.id)}
							oninput={(e) => setTagValue(cat.id, e.target.value)}
							required
						/>
					</label>
				</div>
			{/each}
		{/if}
	</div>

	<!-- Optional Tags Section -->
	<div class="field mt-4">
		<label class="label">Optional Tags</label>
		<div class="tags mb-3">
			{#if Object.keys(tagCategories.optional).length === 0}
				<p>No optional tags for this project.</p>
			{:else}
				{#each storyData.tags as tag, index}
					{#if tagCategories.optional.some((cat) => cat.id === tag.category)}
						<span class="tag is-medium">
							<strong class="mr-1">{tag.categoryLabel}:</strong>
							{tag.value}
							<button class="delete is-small ml-2" onclick={() => removeTag(index)}></button>
						</span>
					{/if}
				{/each}
				<div class="field has-addons">
					<div class="control is-expanded">
						<div class="select is-fullwidth">
							<select bind:value={selectedOptionalCategory}>
								{#each tagCategories.optional as category}
									<option value={category.id}>{category.label}</option>
								{/each}
							</select>
						</div>
					</div>
					<div class="control is-expanded">
						<input
							class="input"
							type="text"
							placeholder="Enter tag value..."
							bind:value={optionalTagValue}
						/>
					</div>
					<div class="control">
						<button
							class="button add-tag-btn"
							onclick={addOptionalTag}
							disabled={!optionalTagValue.trim()}
						>
							Add
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<div class="field mt-5 is-flex is-justify-content-flex-end">
		<div class="control">
			<button
				class="button is-primary"
				onclick={handleNext}
				disabled={(!storyData.text_content && !storyData.audio) ||
					!tagCategories.required.every((cat) =>
						(storyData.tags || []).some((tag) => tag.category === cat.id && tag.value.trim())
					)}
			>
				Next
			</button>
		</div>
	</div>
</div>

<style>
	.word-count-tag {
		background-color: #56bcb3 !important;
		color: #222 !important;
	}
	.required-tag-row {
		display: flex;
		align-items: center;
		gap: 0.5em;
		margin-bottom: 0.5em;
	}
	.required-tag-label {
		font-size: 0.95rem;
		min-width: 55px;
		margin-bottom: 0;
		padding-top: 0.1em;
		padding-bottom: 0.1em;
		text-align: left;
	}
	.required-tag-input {
		border: 1.5px solid #56bcb3;
		background: #f8fefd;
		transition: box-shadow 0.2s;
	}
	.required-tag-input:focus {
		box-shadow: 0 0 0 2px #56bcb333;
		border-color: #56bcb3;
	}
	.compact-input {
		font-size: 0.85rem;
		padding: 0.25em 0.5em;
		height: 1.8em;
		min-width: 80px;
		max-width: 140px;
	}
	.disabled {
		opacity: 0.6;
		pointer-events: none;
	}
	
	.file-cta.disabled {
		background-color: #f5f5f5 !important;
		color: #999 !important;
		cursor: not-allowed !important;
	}
</style>
