export async function load({ params }) {
	//const post = await getPostFromDatabase(params.slug);

	const tests = [
		{
			name: 'Organization1',
			email: 'test@gmail.com'
		},
		{
			name: 'Organization2',
			email: 'test2@gmail.com'
		}
	];

	return { tests, params };
}
