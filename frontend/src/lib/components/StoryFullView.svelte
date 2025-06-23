<!-- Highlight text Ref: https://svelte.dev/playground/09058408863b46b7837e645a45c43ff3?version=5.32.1#H4sIAAAAAAAAE3VTwW7bMAz9FULowQHc5O7EKYphQA8bBhS9RQEqW4ytVpEMiW5ceP73QZHtpml3Skw-PpLvUT0z4ogsYw-qqrWqaoKjoLJGCYQdgTIgoLSG0BBKRaLQCFK9wUlRDf4NNSFL2UFp9Czb9Yzem0AXAiydyO-bZjljC-Hxu_jYxbOMbXzpVENbbgA0TiN5yGHHWSzgLAXO6mnq-OnfDYmOs_16qhxJIQfO7qVUpoIIgrkUyIIwoEzTnveN_ND6ABbTpyhJWcPZzBzUsG7NTQgcWnPOQ9tIQfgjdk0W0IcswGoFwkjw5FQDVCPUdNRAovIxrw6QRMLFxcgxsgxGjIzn7sNVz6Nwr-gS6igFh93c9BPgCd0xIXTHOX2eymGjRYluBk-5sKKSHeST-EtlJHZ_DpFkPeEcUusMPMMmdIFSC-9zzm76HWcOZfSl0C1ytt8p2e3h7g44s1Sj42zgbHvTB8ZhswoEW3geqYf4M_JTR8tx1sRhl8K4S7692m5xKRF2jXX0IcTseWKsxBR2TpweA1uQeP9VuGh6ciFZMCqAFxAYlsoYdA9Pv3-ddYo2YPDB4AkesfrZNcnUg7OKs8Xi83pTh_Wnbed28ZwSW7xczABXc0MOtnhZf6SvSAGGdGw6ibNZzS-Mm41Ub-enFv5E4NWLzzkjFyyM2dZjNkuZ97vpQl6sMglnfzlbpBPFfly0UEZmVCuf9_Gsx7g1WaFbl_efXs4Aq22YMk7GzcbTu8bzkFmlbSF0EuReOpSzMKXV1mXgUE5bXoHDFV6jQ-w_8POJfsWL8vX7ghlaiPK1crY18nasOtWKcHTjYA3dnjBIl0FhtbzwZFySpSwYy7Ig-rBPGQmlT8pIlh2E9jj8A24Pplq2BQAA -->

<script>
	import DeleteButton from '$lib/components/DeleteButton.svelte';
	import { fail, redirect } from '@sveltejs/kit';
	let { story } = $props();

	// Define redirect path
	const host = window.location.hostname;
	const path = window.location.pathname.split('/');
	const deleteRedirectPath = `org/${path[2]}`;

	// Highlight searched terms
	let searchTerm = $state('');
	let editor;

	function updateContent() {
		// and strip the html tags
		if (editor) content = editor.textContent;
	}

	function marker(txt, rex) {
		function markTerm(term) {
			// replacer function
			return ` <mark class="highlight" style="background-color:#56bcb3; color:#f2f1f0">${term}</mark> `;
		}
		return txt.replace(rex, (term) => markTerm(term));
	}

	export function highlight(node, [rawRex, text]) {
		function action() {
			if (text) node.innerHTML = marker(text, new RegExp(rawRex, 'g'));
		}
		action();

		return {
			update(obj) {
				[rawRex, text] = obj;
				action();
			}
		};
	}
</script>

<div class="card">
	<!-- HEADER  -->
	<header class="card-header">
		<div class="level-left">
			<h2>
				Curated by <span class="curator">{story.curator}</span> for
				<span class="project">{story.project_name}</span>
			</h2>
		</div>
		<div class="level-right" id="trash">
			<DeleteButton type={'story'} id={story.story_id} redirectPath={deleteRedirectPath}
			></DeleteButton>
		</div>
	</header>
	<div class="content">
		<!-- TITLE -->
		<h1>Story by <span class="storyteller"><b>{story.storyteller}</b></span></h1>

		<!-- TAGS -->
		<div class="tags is-justify-content-start">
			<div class="column" id="user-tags">
				<span class="icon">
					<i class="fa fa-pencil"></i>
				</span>
				<span class="has-text-left">HUMAN GENERATED TAGS</span>
				<br />
				{#if story.tags.filter((tag) => tag.created_by != 'computer').length > 0}
					{#each story.tags as tag}
						{#if tag.created_by != 'computer'}
							<span class="tag is-medium m-1">{tag.value}</span>
						{/if}
					{/each}
				{:else}
					<div class="p-1 is-small">No tags added</div>
				{/if}
			</div>
			<div class="column" id="ml-tags">
				<span class="icon">
					<i class="fa fa-lightbulb-o"></i>
					<!-- <i class="fa fa-user-robot"></i> -->
				</span>
				<span class="has-text-left">AI GENEARATED TAGS</span>
				<br />
				{#if story.tags.filter((tag) => tag.created_by == 'computer').length > 0}
					{#each story.tags as tag}
						{#if tag.created_by == 'computer'}
							<span class="tag is-medium m-1">{tag.value}</span>
						{/if}
					{/each}
				{:else}
					<div class="p-1 is-small">No AI generated tags added</div>
				{/if}
			</div>
		</div>

		<!-- SEARCH INPUT BOX -->
		<div class="columns is-multiline">
			<div class="column is-4 is-left" id="search-container">
				<div class="field is-left">
					<div class="control is-small is-left">
						<input
							class="input is-small"
							type="text"
							placeholder="Search a word"
							bind:value={searchTerm}
						/>
					</div>
				</div>
			</div>
			<div class="column is-7"></div>
		</div>

		<!-- TEXT CONTENT -->
		<!-- The highlighting function does not parse 
		 the paragraph correctly when there are no search terms.
		 The conditional enables rendering the text directly whitout 
		 going through the highlighting function when it is not needed. 
		  -->

		{#if searchTerm}
			<div
				contenteditable="true"
				use:highlight={[searchTerm, story.text_content]}
				bind:this={editor}
				onblur={updateContent}
			></div>
		{:else}
			<p>{story.text_content}</p>
		{/if}
	</div>
</div>

<style>
	.card-header {
		background-color: #ede8eb;
		padding: 10px;
	}

	.content {
		padding: 25px;
	}

	#user-tags > .tag {
		background-color: #56bcb3;
		color: #f2f1f0;
	}

	#ml-tags > .tag {
		background-color: #d0fdb9;
	}

	#trash {
		margin-left: auto;
		margin-right: 0;
	}
</style>
