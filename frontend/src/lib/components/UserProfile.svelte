<script>
	const { user } = $props();

	// Use mutable state for editing mode
	let editing = $state(false);

	// Create mutable state from user properties
	let first_name = $state(user.First_name);
	let last_name = $state(user.Last_name);
	let email = $state(user.Email);
	let profile_pic_path = $state(user.Profile_pic_path);
	let bio = $state(user.Bio);
	let city = $state(user.City);
	let position = $state(user.Position);

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
							src={profile_pic_path || 'https://bulma.io/images/placeholders/256x256.png'}
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
									bind:value={profile_pic_path}
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
									<input class="input" type="text" bind:value={user.First_name} />
								</div>
							</div>
							<div class="field">
								<label class="label">Last Name</label>
								<div class="control">
									<input class="input" type="text" bind:value={user.Last_name} />
								</div>
							</div>
							<div class="field">
								<label class="label">Email</label>
								<div class="control">
									<input class="input" type="email" bind:value={user.Email} />
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
							<h1 class="title is-3">{user.First_name} {user.Last_name}</h1>
							<p class="subtitle is-5">{user.Position || 'No Position'}</p>
							<p><strong>Email:</strong> {user.Email}</p>
							<p><strong>Location:</strong> {user.City || 'No City'}</p>
							<div class="block">
								<strong>Bio:</strong>
								{user.Bio || 'No bio provided yet.'}
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
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>
