import { text } from '@sveltejs/kit';

export async function load({ params }) {
	//const post = await getPostFromDatabase(params.slug);

	const stories = [
		{
			story_id: 1,
			proj_id: 321,
			org_id: 213,
			storyteller: 'Rebecca Sugar',
			curator: 'Arthur Steiner',
			date: 'May 5th, 2025',
			content:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra commodo rutrum. Curabitur vel odio in elit fringilla tincidunt. Nulla nisl sem, mattis at nisl quis, tempor porttitor neque. Integer dignissim mauris quis tellus efficitur bibendum. Donec odio leo,'
		},
		{
			story_id: 2,
			proj_id: 321,
			org_id: 213,
			storyteller: 'test2',
			curator: 'Arthur Steiner',
			date: 'May 10th, 2025',
			content:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra commodo rutrum. Curabitur vel odio in elit fringilla tincidunt. Nulla nisl sem, mattis at nisl quis, tempor porttitor neque. Integer dignissim mauris quis tellus efficitur bibendum. Donec odio leo,'
		}
	];

	return { stories, params };
}
