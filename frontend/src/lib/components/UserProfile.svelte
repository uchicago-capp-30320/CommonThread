<script>
	const { user } = $props();
	import DeleteButton from './DeleteButton.svelte';

	// Use mutable state for editing mode
	let editing = $state(false);

	// Create mutable state from user properties
	let first_name = $state(user.first_name);
	let last_name = $state(user.last_name);
	let email = $state(user.email);
	let profile_pic_path = $state(user.profile_pic_path);
	let bio = $state(user.bio);
	let city = $state(user.city);
	let position = $state(user.position);

	// Create a backup of original values to restore on cancel
	let originalValues = $state({});

	function toggleEdit() {
		if (!editing) {
			// Save original values before entering edit mode
			originalValues = {
				first_name: first_name,
				last_name: last_name,
				email: email,
				bio: bio,
				city: city,
				position: position,
				profile_pic_path: profile_pic_path
			};
		} else {
			// Save functionality would go here
			// (e.g., API call to update user profile)
		}
		editing = !editing;
	}

	function cancelEdit() {
		// Restore original values
		first_name = originalValues.first_name;
		last_name = originalValues.first_name;
		email = originalValues.email;
		bio = originalValues.bio;
		city = originalValues.city;
		position = originalValues.position;
		profile_pic_path = originalValues.profile_pic_path;
		editing = false;
	}
</script>

<section class="section">
	<div class="container">
		<div class="box">
			<div class="columns">
				<div class="column is-one-quarter">
					<figure class="image is-1by1">
						<img
							src={user.profile_pic_path || 'https://bulma.io/images/placeholders/256x256.png'}
							alt="Profile picture"
							class="is-rounded"
						/>
					</figure>
					{#if editing}
						<div class="field mt-3">
							<div class="control">
								<input
									class="input"
									type="text"
									placeholder="Image URL"
									bind:value={user.profile_pic_path}
								/>
							</div>
						</div>
					{/if}
				</div>

				<div class="column">
					<div class="content">
						{#if editing}
							<div class="field">
								<label class="label">First Name</label>
								<div class="control">
									<input class="input" type="text" bind:value={user.first_name} />
								</div>
							</div>
							<div class="field">
								<label class="label">Last Name</label>
								<div class="control">
									<input class="input" type="text" bind:value={user.last_name} />
								</div>
							</div>
							<div class="field">
								<label class="label">Email</label>
								<div class="control">
									<input class="input" type="email" bind:value={user.email} />
								</div>
							</div>
							<div class="field">
								<label class="label">Position</label>
								<div class="control">
									<input class="input" type="text" bind:value={position} />
								</div>
							</div>
							<div class="field">
								<label class="label">City</label>
								<div class="control">
									<input class="input" type="text" bind:value={city} />
								</div>
							</div>
							<div class="field">
								<label class="label">Bio</label>
								<div class="control">
									<textarea class="textarea" bind:value={bio}></textarea>
								</div>
							</div>
						{:else}
							<h1 class="title is-3">{user.first_name} {user.last_name}</h1>
							<p class="subtitle is-5">{user.position || 'No Position'}</p>
							<p><strong>Email:</strong> {user.email}</p>
							<p><strong>Location:</strong> {user.city || 'No City'}</p>
							<div class="block">
								<strong>Bio:</strong>
								{user.bio || 'No bio provided yet.'}
							</div>
						{/if}
						<div class="field">
							<div class="control">
								<button class="button is-primary" onclick={toggleEdit}>
									{editing ? 'Save Profile' : 'Edit Profile'}
								</button>
								{#if editing}
									<button class="button is-light ml-2" onclick={cancelEdit}> Cancel </button>
								{/if}
								<DeleteButton type="user" id={user.user_id} redirectPath="/" />
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>
