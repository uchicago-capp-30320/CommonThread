<script>
	import MyStory from '$lib/components/StoryPreview.svelte';
	// Refs: https://stackoverflow.com/questions/43370534/css-cutting-text-to-the-size-of-parent-div
	// Refs: https://www.w3schools.com/css/css3_borders.asp
	// Refs: https://dev.to/drews256/ridiculously-easy-row-and-column-layouts-with-flexbox-1k01
	const story = {
		story_id: 123,
		proj_id: 321,
		org_id: 213,
		storyteller: 'Rebecca Sugar',
		curator: 'Arthur Steiner',
		date: 'May 5th, 2025',
		content:
			' Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra commodo rutrum. Curabitur vel odio in elit fringilla tincidunt. Nulla nisl sem, mattis at nisl quis, tempor porttitor neque. Integer dignissim mauris quis tellus efficitur bibendum. Donec odio leo, finibus quis ornare vel, ultricies sit amet erat. Nulla a porttitor risus, vitae faucibus elit. Nam venenatis ac tellus sit amet vestibulum. Cras ullamcorper diam lorem, et dictum augue fringilla non. Donec ac metus augue. Nunc tincidunt massa vel est maximus, quis efficitur risus tincidunt. Curabitur ac eros venenatis, consequat purus eu, facilisis tortor. Quisque mattis volutpat justo eu accumsan. Donec vel velit at erat semper iaculis nec nec lectus.\nVestibulum eu mi vel diam fermentum maximus in vitae lorem. Sed pulvinar tortor sapien, vitae fermentum leo condimentum sit amet. Duis vestibulum lectus ut tellus luctus accumsan. Quisque at ipsum maximus, venenatis ipsum vel, hendrerit ante. Aliquam bibendum interdum porttitor. Maecenas molestie augue et semper tempor. Aenean aliquam, libero iaculis ullamcorper sollicitudin, felis est interdum enim, vel interdum lorem sapien id felis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Suspendisse potenti. Etiam eu mi consectetur, vulputate enim ut, ornare justo. Praesent accumsan erat sed vulputate congue. Nulla iaculis, nisi sed hendrerit volutpat, arcu augue bibendum nunc, vehicula gravida enim ex eget tellus. Sed porta luctus hendrerit. Nam nec bibendum elit, eu scelerisque elit. Nulla tristique aliquam vulputate. Aenean et pulvinar velit, in fringilla nulla. '
	};
</script>

<MyStory {...story} />

<!-- <Test { ...story }/>  -->
