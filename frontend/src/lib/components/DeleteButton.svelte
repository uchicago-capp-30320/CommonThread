<!-- General component to call Delete endpoints -->
<script>
    import Modal from "$lib/components/Modal.svelte"
    // A type can be: "story"...
    // Derive props and set initial state 
    let { type, redirectPath } = $props();
    let showModal = $state(false); 
    $inspect(showModal)

    function askDeleteConfirmation() {
        showModal = true; 
    }


</script>

<!-- Trash button -->
<button class="button is-ghost"
    aria-label="delete"
    onclick={askDeleteConfirmation}
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
                All information associated with it—including text, tags, and 
                audiovisual materials—will be deleted and not recoverable. 
            </p>
        </div>

	{/snippet}

    <div id="modal-buttons" class="container level-right">
        <button class="button" id="cancel-delete">No, go back.</button>
        <button class="button is-link" id="confirm-delete"><b>Yes, delete.</b></button>
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
 