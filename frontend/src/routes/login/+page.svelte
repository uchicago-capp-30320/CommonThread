<script>
	// Load design assets
	import background_texture from '$lib/assets/background_texture.png';
	import { authRequest } from '$lib/authRequest';

	import { accessToken, refreshToken, ipAddress, userExpirationTimestamp } from '$lib/store.js';

	import { redirect } from '@sveltejs/kit';
	import { utcFormat } from 'd3-time-format';

	let username = $state('');
	let password = $state('');

	async function login(data) {
		data = { post_data: data };
		console.log('login data', data);
		// Send POST request to login endpoint
		const response = await fetch(`${ipAddress}/login`, {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		let response_data = {};

		await response.json().then((d) => {
			response_data = d;
		});

		console.log('response_data', response_data);
		console.log('accessToken', $accessToken);

		accessToken.set(response_data.access_token);
		console.log('accessToken', $accessToken);

		refreshToken.set(response_data.refresh_token);
		console.log('refreshToken', $refreshToken);

		// Set expiration timestamp for 7 days from now
		userExpirationTimestamp.set(
			utcFormat(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000))('%Y-%m-%dT%H:%M:%S')
		);

		const ok = response_data.success;

		// Handle redirect if login is successful
		if (ok) {
			const user = await authRequest(`/user`, 'GET', $accessToken, $refreshToken);
			console.log('user', user);

			const org_id = user.data.orgs[0].org_id;

			// TODO find org_id from response data?
			//const org_id = response_data.org_id;

			// Use window.location for client-side navigation
			window.location.href = `/org/${org_id}`;
		} else {
			redirect(303, '/signup');
		}
	}
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<div id="container">
	<div class="container is-max-tablet">
		<div class="notification">
			<div class="title has-text-centered">LOGIN</div>
			<form onsubmit={() => login({ username, password })}>
				<div class="field">
					<label class="label" for="username" bind>Username</label>
					<div class="control has-icons-left has-icons-right">
						<input
							class="input is-success"
							type="text"
							id="username"
							name="username"
							placeholder="Your username"
							bind:value={username}
							required
						/>
						<span class="icon is-small is-left">
							<i class="fa fa-user"></i>
						</span>
						<!-- <span class="icon is-small is-right">
							<i class="fa fa-check"></i>
						</span> -->
					</div>
				</div>

				<div class="field">
					<label class="label" for="password">Password</label>
					<div class="control has-icons-left has-icons-right">
						<input
							class="input is-success"
							type="password"
							id="password"
							name="password"
							placeholder="*****"
							bind:value={password}
							required
						/>
						<span class="icon is-small is-left">
							<i class="fa fa-lock"></i>
						</span>
					</div>
				</div>

				<div class="field is-grouped">
					<div class="control">
						<button type="submit" class="button is-link" id="login-btn">Login</button>
					</div>
					<div class="control">
						<button type="reset" class="button is-light">Cancel</button>
					</div>
				</div>
			</form>

			<div class="field">
				<div class="control" id="forgot">
					<a href="/">Did you forget your password?</a>
				</div>
			</div>

			<div class="field">
				<div class="control">
					Is this your first time visiting? <a href="/signup">Sign up!</a>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.notification {
		background-color: var(--light-blue);
	}

	#login-btn {
		background-color: var(--dark-blue);
		color: white;
	}

	/* Ref: https://stackoverflow.com/questions/14402038/how-to-position-a-container-in-the-middle-of-the-screen */
	#container {
		margin-top: 50px;
		width: 400px;
		margin-left: auto;
		margin-right: auto;
	}

	#forgot {
		padding-top: 15px;
	}
</style>
