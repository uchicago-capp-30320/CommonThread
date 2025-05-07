<script>
	import background_texture from '$lib/assets/background_texture.png';
</script>

<div id="container">
	<div class="container is-max-tablet">
		<div class="notification is-primary" S>
			<div class="title has-text-centered">LOGIN</div>

			<div class="field">
				<label class="label" for="username">Username</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-success"
						type="text"
						id="username"
						placeholder="Your username"
						value=""
					/>
					<span class="icon is-small is-left">
						<i class="fa fa-user"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fa fa-check"></i>
					</span>
				</div>
			</div>

			<div class="field">
				<label class="label" for="password">Password</label>
				<div class="control has-icons-left has-icons-right">
					<input
						class="input is-success"
						type="password"
						id="password"
						placeholder="*****"
						value=""
					/>
					<span class="icon is-small is-left">
						<i class="fas fa-user"></i>
					</span>
					<span class="icon is-small is-right">
						<i class="fas fa-check"></i>
					</span>
				</div>
			</div>

			<div class="field is-grouped">
				<div class="control">
					<button class="button is-link">Login</button>
				</div>
				<div class="control">
					<button class="button is-link is-light">Cancel</button>
				</div>
			</div>

			<div class="field">
				<div class="control">
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
	.banner {
		height: 600px;
		z-index: -1;
		position: relative;
		overflow: hidden;
	}

	.banner img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	h1 {
		text-align: center;
		font-size: 2rem;
	}

	/* Ref: https://stackoverflow.com/questions/14402038/how-to-position-a-container-in-the-middle-of-the-screen */
	#container {
		margin-top: 50px;
		width: 400px;
		margin-left: auto;
		margin-right: auto;
	}
</style>
