<script>
	import background_texture from '$lib/assets/background_texture.png';
</script>

<div id="container">
	<div class="container is-max-tablet">
		<div class="notification" S>
			<div class="title has-text-centered">LOGIN</div>

			<form method="post">
				<div class="field">
					<label class="label" for="username">Username</label>
					<div class="control has-icons-left has-icons-right">
						<input
							class="input is-success"
							type="text"
							d
							id="username"
							name="username"
							placeholder="Your username"
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
							required
						/>
						<span class="icon is-small is-left">
							<i class="fa fa-lock"></i>
						</span>
					</div>
				</div>

				<div class="field is-grouped">
					<div class="control">
						<button type="submit" class="button is-link" id="login-button">Login</button>
					</div>
					<div class="control">
						<button type="reset" class="button is-light">Cancel</button>
					</div>
				</div>
			</form>

			<div class="field">
				<div class="control" id="forgot">
					<a href="#">Did you forget your password?</a>
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

	#login-button {
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
