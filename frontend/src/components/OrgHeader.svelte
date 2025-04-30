<script>
    let {org_name,other} = $props();
</script>


<div class="columns">
<div class="card columns column is-half">
    <div class="card-image column is-one-fifth">
      <figure class="image is-96x96">
        <img
          src="https://bulma.io/assets/images/placeholders/96x96.png"
          alt="Placeholder image"
        />
      </figure>
    </div>
    <div class="card-content column">
      <div class="media">
        
        <div class="media-content">
          <p class="title is-4">{org_name}</p>
          <p class="subtitle is-6">{other}</p>
        </div>
      </div>
  
      <div class="content">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec
        iaculis mauris. <a>@bulmaio</a>. <a href="#">#css</a>
        <a href="#">#responsive</a>
        <br />
        <time datetime="2016-1-1">11:09 PM - 1 Jan 2016</time>
      </div>
    </div>
  </div>
</div>