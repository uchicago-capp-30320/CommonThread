<script>
	let { currentStep = $bindable(), storyData = $bindable() } = $props();
	let wordCount = $derived(() => storyData.content.trim().split(/\s+/).length);

	// --- Hardcoded tag categories to be removed---
	const defaultTagCategories = {
		required: [
			{ id: 'city', label: 'City' },
			{ id: 'area', label: 'Area' }
		],
		optional: [
			{ id: 'mood', label: 'Mood' },
			{ id: 'season', label: 'Season' },
			{ id: 'topic', label: 'Topic' }
		]
	};

	let tagCategories = defaultTagCategories;
	let selectedOptionalCategory = $state(tagCategories.optional[0].id);
	let optionalTagValue = $state('');

	/* for future
	$onMount(async () => {
		const res = await fetch('/api/sdasda/dsadsa');
		const data = await res.json();
		tagCategories = {
			required: data.required_tags,
			optional: data.optional_tags
		};
	});
	*/

	function getTagMap() {
		return new Map((storyData.tags || []).map((tag) => [tag.category, tag]));
	}

	// Read a tag’s value
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

	// Helpers for optional‑tag UI
	function addOptionalTag() {
		if (optionalTagValue.trim()) {
			setTagValue(selectedOptionalCategory, optionalTagValue);
			optionalTagValue = '';
		}
	}

	// Validation: ensure all required categories exist and have non‑empty values
	function hasAllRequiredTags() {
		const tagsMap = getTagMap();
		return tagCategories.required.every((cat) => tagsMap.has(cat.id) && tagsMap.get(cat.id).value);
	}

	function handleNext() {
		if (storyData.content && hasAllRequiredTags()) {
			currentStep = 3;
		}
	}
</script>

<div class="box">
	<h2 class="title is-4 mb-5">Story Details</h2>

	<div class="field">
		<label class="label" for="story-text">Your Story</label>
		<div class="control">
			<textarea
				class="textarea"
				id="story-text"
				bind:value={storyData.content}
				placeholder="Share your story here..."
				rows="6"
				required
			></textarea>
		</div>
	</div>
	<div class="is-flex is-justify-content-flex-end mb-2">
		<label class="label mb-0">
			Word count:
			<span class="tag is-link word-count-tag">{wordCount()}</span>
		</label>
	</div>

	<!-- Required Tags Section -->
	<div class="field mt-4">
		<label class="label">Required Tags</label>
		{#each tagCategories.required as cat}
			<div class="required-tag-row mb-2">
				<label class="label mb-0 required-tag-label">{cat.label}</label>
				<input
					class="input is-rounded is-small required-tag-input compact-input"
					type="text"
					placeholder={'Enter ' + cat.label}
					value={getTagValue(cat.id)}
					oninput={(e) => setTagValue(cat.id, e.target.value)}
					required
				/>
			</div>
		{/each}
	</div>

	<!-- Optional Tags Section -->
	<div class="field mt-4">
		<label class="label">Optional Tags</label>
		<div class="tags mb-3">
			{#each storyData.tags as tag, index}
				{#if tagCategories.optional.some((cat) => cat.id === tag.category)}
					<span class="tag is-medium">
						<strong class="mr-1">{tag.categoryLabel}:</strong>
						{tag.value}
						<button class="delete is-small ml-2" onclick={() => removeTag(index)}></button>
					</span>
				{/if}
			{/each}
		</div>
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
	</div>

	<div class="field mt-5 is-flex is-justify-content-flex-end">
		<div class="control">
			<button
				class="button is-primary"
				onclick={handleNext}
				disabled={!storyData.content ||
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
</style>
