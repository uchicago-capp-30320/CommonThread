<script>
	import background_texture from '$lib/assets/background_texture.png';
	import { authRequest } from '$lib/authRequest.js';
	import { goto } from '$app/navigation';
	import { accessToken, refreshToken, ipAddress } from '$lib/store.js';

	let signupData = $state({
		first_name: '',
		last_name: '',
		username: '',
		email: '',
		password: '',
		confirmPassword: ''
	});
	let errorMessage = $state('');
	let successMessage = $state('');
	$inspect(errorMessage);

	$inspect(signupData);

	let termsAccepted = $state(false);

	$inspect(termsAccepted);

	async function signup() {
		if (!termsAccepted) {
			errorMessage = 'You must accept the terms and conditions.';
			return;
		}

		if (signupData.password !== signupData.confirmPassword) {
			errorMessage = 'Passwords do not match.';
			return;
		}

		try {
			const response = await authRequest(
				'/user/create',
				'POST',
				$accessToken,
				$refreshToken,
				signupData
			);
			console.log(response);
			if (response.data.success) {
				successMessage = 'Sign up successful! Redirecting to login...';
				// Redirect to login page after a short delay
				setTimeout(() => goto('/login'), 2000);
			} else {
				errorMessage = response.data.message || 'Sign up failed. Please try again.';
			}
		} catch (error) {
			console.error('Sign up error:', error);
			errorMessage = 'An error occurred during sign up. Please try again later.';
		}
	}
</script>

<svelte:head>
	<title>Sign Up</title>
</svelte:head>

<div id="container">
	<div class="container is-max-tablet">
		<div class="notification">
			<div class="title has-text-centered">SIGN UP</div>

			<div class="field">
				<label class="label" for="name">First Name</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input"
						type="text"
						id="first_name"
						bind:value={signupData.first_name}
						placeholder="Your first name"
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-user"></i>
					</span>
				</div>
			</div>
			<div class="field">
				<label class="label" for="name">Last Name</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input"
						type="text"
						id="last_name"
						bind:value={signupData.last_name}
						placeholder="Your first name"
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-user"></i>
					</span>
				</div>
			</div>

			<div class="field">
				<label class="label" for="username">Username</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-success"
						type="text"
						id="username"
						bind:value={signupData.username}
						placeholder="Your username"
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-user"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fa fa-check"></i>
					</span>
				</div>
				<p class="help is-success">This username is available</p>
			</div>

			<div class="field">
				<label class="label" for="email">Email</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-danger"
						type="email"
						id="email"
						bind:value={signupData.email}
						placeholder="your@email.org"
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-envelope"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fa fa-exclamation-triangle"></i>
					</span>
				</div>
				<p class="help is-danger">This email is invalid</p>
			</div>

			<div class="field">
				<label class="label" for="password">Password</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-success"
						type="password"
						id="password"
						placeholder="********"
						bind:value={signupData.password}
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-lock"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fa fa-check"></i>
					</span>
				</div>
			</div>

			<div class="field">
				<label class="label" for="confirm-password">Confirm password</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-success"
						type="password"
						id="confirm-password"
						placeholder="********"
						bind:value={signupData.confirmPassword}
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-lock"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fa fa-check"></i>
					</span>
				</div>
			</div>

			<div class="field">
				<div class="control">
					<label class="checkbox">
						<input type="checkbox" bind:checked={termsAccepted} />
						I agree to the <a href="#">terms and conditions</a>
					</label>
				</div>
			</div>

			<div class="field is-grouped">
				<div class="control">
					<button class="button is-link" id="signup-button" onclick={signup}>Sign Up</button>
				</div>
				<div class="control">
					<button class="button is-light">Cancel</button>
				</div>
			</div>

			<div class="field">
				<div class="control">
					Already have an account? <a href="/login">Login!</a>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.notification {
		background-color: var(--light-blue);
	}

	#signup-button {
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
</style>
