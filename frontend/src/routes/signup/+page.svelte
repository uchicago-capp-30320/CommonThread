<script>
	import background_texture from '$lib/assets/background_texture.png';
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
