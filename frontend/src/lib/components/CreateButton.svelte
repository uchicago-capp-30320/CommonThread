<!-- General component to call Delete endpoints -->
<script>
	import Modal from '$lib/components/Modal.svelte';
	import WaitingModal from './WaitingModal.svelte';

	import { accessToken, refreshToken, ipAddress } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { goto } from '$app/navigation';

	// To be consistent with the API, the type prop must have the values: "story", "project", "org", "user"
	// Derive props and set initial state
	let { type, data = $bindable(), redirectPath = null } = $props();
	let showModal = $state(false);
	let showModalWait = $state(false);

	let url = '';

	$inspect(showModal);
	$inspect('type', type);
	$inspect('data in create', data);
	$inspect('redirectPath', redirectPath);

	// Check input
	const validType = ['user', 'org', 'project', 'story', 'user-org'].includes(type);

	if (!validType) {
		console.error('Cannot create object of type ' + type);
	}

	// parse type to readable
	const typeClean = {
		user: 'User',
		org: 'Organization',
		project: 'Project',
		story: 'Story',
		'user-org': 'User'
	}[type];

	const closeModal = (id) => {
		console.log('Try to close modal: ' + id);
		const dialog = document.getElementById(id);
		dialog.close();
	};

	// Define create request
	async function sendCreateRequest() {
		if (type === 'user-org') {
			url = `/org/${data.org_id}/add-user`;
		} else {
			url = `/${type}/create`;
		}

		showModalWait = true;
		showModal = false;
		closeModal('confirmRequest');

		const createResponse = await authRequest(url, 'POST', $accessToken, $refreshToken, data);
		console.log(createResponse);
		if (!createResponse) {
			console.error('No response from create request');
			showModalWait = false;
			closeModal('waitingAPIResponse');
			return;
		}

		if (createResponse.data.success) {
			showModalWait = false;
			data.isOpen = false; // Close the modal after successful creation
			closeModal('waitingAPIResponse');
			if (redirectPath) {
				// If a redirect path is provided, use it
				goto(redirectPath);
			}
		}
	}
</script>

<!-- Create button -->
<button class="button is-success" onclick={() => (showModal = true)}>
	{data.isNew ? `Add New ${typeClean}` : `Save Changes`}
</button>

<!-- Bulma's modal with Pop up message  -->
<Modal bind:showModal modalId={'confirmRequest'}>
	{#snippet header()}
		<div class="content">
			<h4>
				Are you sure you want to create this {typeClean}?
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

<WaitingModal bind:showModalWait modalId={'waitingAPIResponse'}>
	<p>Waiting for your {typeClean} to be created.</p>
</WaitingModal>

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
