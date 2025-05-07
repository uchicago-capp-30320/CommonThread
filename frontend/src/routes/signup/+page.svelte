<script>
	import background_texture from '$lib/assets/background_texture.png';

  // Font Awesome logos: https://www.npmjs.com/package/svelte-fa
  import Fa from 'svelte-fa'
  import { faFlag } from '@fortawesome/free-solid-svg-icons'
  import { faGithub } from '@fortawesome/free-brands-svg-icons';
</script>

<!-- Bulma Ref: https://bulma.io/documentation/form/general/#with-icons -->
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css">
</head>

<div id="container">
    <div class="container is-max-tablet">
        <div class="notification is-primary">
            <h1>SIGN UP</h1>

    <div class="field ">
        <label class="label">Name</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" type="text" placeholder="Your name">
        </div>
      </div>
      
      <div class="field">
        <label class="label">Username</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input is-success" type="text" placeholder="Your username">
          <span class="icon is-small is-left">
            <i class="fas fa-user"></i>
          </span>
          <span class="icon is-small is-right">
            <i class="fas fa-check"></i>
          </span>
        </div>
        <p class="help is-success">This username is available</p>
      </div>
      
      <div class="field">
        <label class="label">Email</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input is-danger" type="email" placeholder="your@email.org">
          <span class="icon is-small is-left">
            <i class="fas fa-envelope"></i>
          </span>
          <span class="icon is-small is-right">
            <i class="fas fa-exclamation-triangle"></i>
          </span>
        </div>
        <p class="help is-danger">This email is invalid</p>
      </div>
      
      <div class="field">
        <label class="label">Password</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input is-success" type="password" placeholder="*****" value="">
          <span class="icon is-small is-left">
            <i class="fas fa-user"></i>
          </span>
          <span class="icon is-small is-right">
            <i class="fas fa-check"></i>
          </span>
        </div>
      </div>

      <div class="field">
        <label class="label">Confirm password</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input is-success" type="password" placeholder="*****" value="">
          <span class="icon is-small is-left">
            <i class="fas fa-user"></i>
          </span>
          <span class="icon is-small is-right">
            <i class="fas fa-check"></i>
          </span>
        </div>
      </div>


      <div class="field">
        <div class="control">
          <label class="checkbox">
            <input type="checkbox">
            I agree to the <a href="#">terms and conditions</a>
          </label>
        </div>
      </div>
            
      <div class="field is-grouped">
        <div class="control">
          <button class="button is-link">Sign Up</button>
        </div>
        <div class="control">
          <button class="button is-link is-light">Cancel</button>
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
    @import "https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css";
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