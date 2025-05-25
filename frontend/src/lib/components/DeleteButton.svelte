<!-- General component to call Delete endpoints -->
<script>
    import Modal from "$lib/components/Modal.svelte"
    import { accessToken, refreshToken, ipAddress } from '$lib/store.js';
	import { authRequest } from '$lib/authRequest.js';
	import { redirect } from "@sveltejs/kit";
    
    // To be consistent with the API, the type prop must have the values: "story", "project", "org", "user"
    // Derive props and set initial state 
    let { type, id, redirectPath } = $props();
    let showModal = $state(false); 
    $inspect(showModal)

    // Check input 
    const validType = ['user', 'org', 'project', 'story'].includes(type)

    if (!validType) {
        console.error("Cannot delete object of type " + type); 
    }

    // Content to be deleted 
    let content = $state(""); 
    if (type === "user") {
        content = "all stories curated by the user"
    } else if (type === "org") {
        content = "all projects and stories"
    } else if (type === "project") {
        content = "all stories"
    } else if (type === "story") {
        content = "text, tags, and audivisual materials"
    }

    // Define delete request 
    const sendDeleteRequest = async () => {
        const deleteResponse = await authRequest(`/${type}/${id}/delete`, 'DELETE', $accessToken, $refreshToken)
        console.log(deleteResponse)
        
        if (deleteResponse.ok) {
            return redirect(204, redirectPath);
        }
    }

</script>

<!-- Trash button -->
<button class="button is-ghost"
    aria-label="delete"
    onclick={showModal=true}
>
    <span class="icon">
        <i class="fa fa-trash"></i>
    </span>
</button>

<!-- Bulma's modal with Pop up message  -->
<Modal bind:showModal>
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
        <button class="button" 
        id="cancel-delete"
        onclick={showModal=false}
        >No, go back.</button>
        <button class="button is-link" 
        id="confirm-delete"
        onclick={sendDeleteRequest}
        >
        <b>Yes, delete.</b></button>
    </div>
</Modal>

<style>
    button {
        color: #133335 !important
    }

    #confirm-delete {
        color:#f2f1f0 !important;
        background-color: #CE6664;
    }

    #cancel-delete {
        background-color: #ede8eb;
    }

    i:hover{
        color: #CE6664;
    }

</style>
 