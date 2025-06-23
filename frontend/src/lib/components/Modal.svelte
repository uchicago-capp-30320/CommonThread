<!-- 
    Modal component to display pop up messages
    Ref: https://svelte.dev/playground/modal?version=5.33.2
-->

<script>
	let { showModal = $bindable(), header, children, modalId } = $props();

	let dialog = $state(); // HTMLDialogElement

	$effect(() => {
		if (showModal) {
			dialog.showModal();
		} else {
			dialog.close();
		}
	});
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
	id={modalId}
	bind:this={dialog}
	onclose={() => (showModal = false)}
	onclick={(e) => {
		if (e.target === dialog) dialog.close();
	}}
>
	<!-- svelte-ignore a11y_autofocus -->
	<div class="container">
		<!-- X mark to close dialog -->
		<div class="modal">
			<div class="modal-background"></div>
		</div>

		<div class="level-right">
			<button
				class="button is-ghost level-right"
				id="close"
				autofocus
				onclick={() => dialog.close()}
				aria-label="Close"
			>
				<span class="icon">
					<i class="fa fa-window-close"></i>
				</span>
			</button>
		</div>

		<!-- The actual content of the modal is defined in the parent component -->
		{@render header?.()}
		<hr />
		{@render children?.()}
	</div>
</dialog>

<style>
	dialog {
		max-width: 32em;
		border-radius: 0.2em;
		border: none;
		padding: 0;
	}
	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}
	dialog > div {
		padding: 1em;
	}
	dialog[open] {
		animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	@keyframes zoom {
		from {
			transform: scale(0.95);
		}
		to {
			transform: scale(1);
		}
	}
	dialog[open]::backdrop {
		animation: fade 0.2s ease-out;
	}
	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	button {
		display: block;
	}

	.icon {
		color: #ede8eb !important;
	}

	.icon:hover {
		color: #ce6664 !important;
	}
</style>
