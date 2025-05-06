export async function load({ params }) {
	//const post = await getPostFromDatabase(params.slug);

	const tests = [
		{
			name: 'Organization1',
			email: 'test@gmail.com',
			text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ac ligula nec felis facilisis aliquet. Integer a nunc ut est efficitur fringilla. Sed at erat in nulla accumsan convallis. Donec id leo sed enim auctor aliquet. Nulla facilisi. Sed at nunc et nisi tincidunt sodales. Sed ac ligula ac enim efficitur commodo.'
		},
		{
			name: 'Organization2',
			email: 'test2@gmail.com',
			text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ac ligula nec felis facilisis aliquet. Integer a nunc ut est efficitur fringilla. Sed at erat in nulla accumsan convallis. Donec id leo sed enim auctor aliquet. Nulla facilisi. Sed at nunc et nisi tincidunt sodales. Sed ac ligula ac enim efficitur commodo.'
		}
	];

	return { tests, params };
}
