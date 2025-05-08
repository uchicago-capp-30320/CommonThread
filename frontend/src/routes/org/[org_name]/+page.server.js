export async function load({ params }) {
	const response = await fetch(`http://127.0.0.1:8000/stories/`);

	if (!response.ok) {
		throw new Error('Failed to fetch stories');
	}
	const data = await response.json();

	const { stories } = data;

	// const stories = [
	// 	{
	// 		story_id: 1,
	// 		proj_id: 321,
	// 		org_id: 213,
	// 		storyteller: 'Rebecca Sugar',
	// 		curator: 'Arthur Steiner',
	// 		date: 'May 5th, 2025',
	// 		content:
	// 			'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra commodo rutrum. Curabitur vel odio in elit fringilla tincidunt. Nulla nisl sem, mattis at nisl quis, tempor porttitor neque. Integer dignissim mauris quis tellus efficitur bibendum. Donec odio leo,'
	// 	},
	// 	{
	// 		story_id: 2,
	// 		proj_id: 321,
	// 		org_id: 213,
	// 		storyteller: 'test2',
	// 		curator: 'Arthur Steiner',
	// 		date: 'May 10th, 2025',
	// 		content:
	// 			'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra commodo rutrum. Curabitur vel odio in elit fringilla tincidunt. Nulla nisl sem, mattis at nisl quis, tempor porttitor neque. Integer dignissim mauris quis tellus efficitur bibendum. Donec odio leo,'
	// 	}
	// ];

	return { stories, params };
}
