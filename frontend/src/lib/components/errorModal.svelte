<script>
  import Modal from '$lib/components/Modal.svelte';
  import { errorStore, ERROR_ACTIONS } from '$lib/errorStore.js';
  
  // This component watches for errors automatically
  let showModal = $state(false);
  let currentError = $state(null);
  
  // Svelte 5 reactive effect - runs when errorStore changes
  $effect(() => {
    if ($errorStore) {
      currentError = $errorStore;
      showModal = true;
    } else {
      currentError = null;
      showModal = false;
    }
  });
  
  function handleAction(action) {
    closeModal();
    if (action === 'retry' && currentError.retryFunction) {
      // If it's a retry action and we have a retry function, call it
      currentError.retryFunction();
    } else if (typeof action === 'function') {
      // If it's a function, call it
      action(currentError.context || {});
    }
    
  }
  
  function closeModal() {
    errorStore.set(null); // Clear the error
  }
  
  // Get the error configuration
  function getErrorConfig(errorCode) {
    return ERROR_ACTIONS[errorCode] || {
      message: 'An unexpected error occurred',
      actions: [{ label: 'OK', handler: () => {} }]
    };
  }
</script>

<Modal bind:showModal>
  {#snippet header()}
    <h3 class="modal-card-title has-text-danger has-text-centered is-size-4 style=width:100%;" > Error</h3>
  {/snippet}
  
  {#if currentError}
    {@const errorConfig = getErrorConfig(currentError.code)}
    <div class="message is-danger">
    <div class="message-body">
      <p class="mb-4">{errorConfig.message}</p>
      
      <div class="field is-grouped is-grouped-right">
        {#each errorConfig.actions as actionConfig}
        <p class="control">
          <button 
            class="button {actionConfig.style || 'is-primary'}" 
            onclick={() => handleAction(actionConfig.handler)}
          >
            {actionConfig.label}
          </button>
          </p>
        {/each}
      </div>
    </div>
    </div>
  {/if}
</Modal>

<style>

  :global(dialog::backdrop) {
    background: rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(4px) !important;
    -webkit-backdrop-filter: blur(4px) !important;
  }
  
  /* Ensure the modal content has proper spacing */
  :global(dialog) {
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
  }
  

</style>