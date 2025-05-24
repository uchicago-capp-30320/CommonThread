<script>
	import background_texture from '$lib/assets/background_texture.png';

	import { fail, redirect } from '@sveltejs/kit';
	let formData = {};

	export const actions = {
		default: async ({ cookies, request, fetch }) => {
			console.log('Signup request sent');
			let data = await request.formData();
			console.log('Submited form data:' + data);

			// TODO: Figure out why data from form is emmpty
			// Ref for form actions: https://svelte.dev/docs/kit/form-actions

			const response = await fetch('http://127.0.0.1:8000/user/create', {
				method: 'POST',
				body: JSON.stringify({ data }),
				headers: {
					'Content-Type': 'application/json'
				}
			});

			let response_data = {};

			await response.json().then((d) => {
				response_data = d;
			});

			console.log(response_data);

			await cookies.set('ct_access_token', response_data.access_token, { path: '/' });
			cookies.set('ct_refresh_token', response_data.refresh_token, { path: '/' });

			// handle redirect if need
			if (response.ok) {
				// TODO: replace harcoded org-austin with variable from db
				window.prompt('New user was sucessfully created! Now please login.');
				return redirect(303, '/login');
			} else {
				window.prompt('Invalid user or password, please try again.');
			}
		}
	};
</script>

<svelte:head>
	<title>Sign Up</title>
</svelte:head>

<div id="container">
	<div class="container is-max-tablet">
		<div class="notification">
			<div class="title has-text-centered">SIGN UP</div>

			<div class="field">
				<label class="label" for="name">Name</label>
				<div class="control has-icons-left has-icons-right">
					<input class="input" type="text" id="name" placeholder="Your name" />
					<span class="icon is-small is-left">
						<i class="fa fa-user"></i>
					</span>
				</div>
			</div>

			<div class="field">
				<label class="label" for="username">Username</label>
				<div class="control has-icons-left has-icons-right">
					<input class="input is-success" type="text" id="username" placeholder="Your username" />
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
					<input class="input is-danger" type="email" id="email" placeholder="your@email.org" />
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
						value=""
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
						value=""
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
						<input type="checkbox" />
						I agree to the <a href="#">terms and conditions</a>
					</label>
				</div>
			</div>

			<div class="field is-grouped">
				<div class="control">
					<button class="button is-link" id="signup-button">Sign Up</button>
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
