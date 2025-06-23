<!-- General component to call Delete endpoints -->
<script>
	import Modal from '$lib/components/Modal.svelte';
	import WaitingModal from './WaitingModal.svelte';
	import SuccessModal from './SuccessModal.svelte';
	import { accessToken, refreshToken, ipAddress } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	// To be consistent with the API, the type prop must have the values: "story", "project", "org", "user"
	// Derive props and set initial state
	let { type, id, redirectPath = null } = $props();
	let showModal = $state(false);
	let showModalWait = $state(false);
	let showModalSuccess = $state(false);

	let url = '';

	const org_id = $page.params.org_id;

	$inspect(showModal);

	// Check input
	const validType = ['user', 'user-org', 'org', 'project', 'story'].includes(type);

	if (!validType) {
		console.error('Cannot delete object of type ' + type);
	}

	// Content to be deleted
	let content = $state('');
	if (type === 'user') {
		content = 'all stories curated by the user';
	} else if (type === 'org') {
		content = 'all projects and stories';
	} else if (type === 'project') {
		content = 'all stories';
	} else if (type === 'story') {
		content = 'text, tags, and audivisual materials';
	}

	const closeModal = (id) => {
		console.log('Try to close modal: ' + id);
		const dialog = document.getElementById(id);
		dialog.close();
	};

	// Define delete request
	const sendDeleteRequest = async () => {
		if (type === 'user-org') {
			url = `/org/${org_id}/delete-user/${id}`;
		} else {
			url = `/${type}/${id}/delete`;
		}

		showModalWait = true;
		showModal = false;
		closeModal('confirmRequest');

		const deleteResponse = await authRequest(url, 'DELETE', $accessToken, $refreshToken);

		/* Wait till response is done to close dialog. */
		if (deleteResponse.data.success) {
			if (type === 'user') {
				// delete user from store
				$accessToken = '';
				$refreshToken = '';
			}

			showModalWait = true;
			closeModal('waitingAPIResponse');

			if (redirectPath) {
				window.location.href = redirectPath;
			}
		}
	};
</script>

<!-- Trash button -->
<div class="level-right">
	<button class="button is-ghost" aria-label="delete" onclick={() => (showModal = true)}>
		<span class="icon">
			<i class="fa fa-trash"></i>
		</span>
	</button>
</div>

<!-- Bulma's modal with Pop up message  -->
<Modal bind:showModal modalId={'confirmRequest'}>
	{#snippet header()}
		<div class="content">
			<h4>
				Are you sure you want to delete this {type}?
			</h4>
			<p>
				All information associated with it—including {content}—will be deleted and not recoverable.
			</p>
		</div>
	{/snippet}

	<div id="modal-buttons" class="container level-right">
		<!-- <button class="button" 
        id="cancel-delete"
        onclick={showModal=false}
        >No, go back.</button> -->
		<button
			class="button is-link"
			id="confirm-delete"
			onclick={() => {
				sendDeleteRequest();
			}}
		>
			<b>Yes, delete.</b></button
		>
	</div>
</Modal>

<WaitingModal bind:showModalWait modalId={'waitingAPIResponse'}>
	<p>Waiting for your {type} to be deleted.</p>
</WaitingModal>

<!-- <SuccessModal bind:showModalSuccess modalId={"successfulResponse"}>
	<p>Your story has been succesfully deleted</p>
</SuccessModal> -->

<style>
	button {
		color: #133335 !important;
	}

	#confirm-delete {
		color: #f2f1f0 !important;
		background-color: var(--red);
	}

	#cancel-delete {
		background-color: #ede8eb;
	}

	i:hover {
		color: var(--red);
	}
</style>
