<!-- General component to call Delete endpoints -->
<script>
	import Modal from '$lib/components/Modal.svelte';
	import { accessToken, refreshToken, ipAddress } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { goto } from '$app/navigation';

	// To be consistent with the API, the type prop must have the values: "story", "project", "org", "user"
	// Derive props and set initial state
	let { type, data, redirectPath = null } = $props();
	let showModal = $state(false);
	let url = '';

	$inspect(showModal);
	$inspect('type', type);
	$inspect('data in create', data);
	$inspect('redirectPath', redirectPath);

	// Check input
	const validType = ['user', 'org', 'project', 'story'].includes(type);

	if (!validType) {
		console.error('Cannot create object of type ' + type);
	}

	// Define create request
	async function sendCreateRequest() {
		if (type === 'user-org') {
			url = `/org/${data.org_id}/add-user`;
		} else {
			url = `/${type}/create`;
		}
		const createResponse = await authRequest(url, 'POST', $accessToken, $refreshToken, data);
		console.log(createResponse);
		if (!createResponse) {
			console.error('No response from create request');
			showModal = false;
			return;
		}

		if (createResponse.data.success) {
			if (redirectPath) {
				// If a redirect path is provided, use it
				goto(redirectPath);
			}
			showModal = false;
		}
	}
</script>

<!-- Create button -->
<button class="button is-success" onclick={() => (showModal = true)}>
	{data.isNew ? `Add New ${type}` : `Save Changes`}
</button>

<!-- Bulma's modal with Pop up message  -->
<Modal bind:showModal>
	{#snippet header()}
		<div class="content">
			<h4>
				Are you sure you want to create this {type}?
			</h4>
		</div>
	{/snippet}

	<div id="modal-buttons" class="container level-right">
		<!-- <button class="button" 
        id="cancel-delete"
        onclick={showModal=false}
        >No, go back.</button> -->
		<button class="button is-success" onclick={() => sendCreateRequest()}>
			<b>Yes, create.</b></button
		>
	</div>
</Modal>

<style>
	button {
		color: #133335 !important;
	}

	#cancel {
		background-color: #ede8eb;
	}

	i:hover {
		color: var(--green);
	}
</style>
