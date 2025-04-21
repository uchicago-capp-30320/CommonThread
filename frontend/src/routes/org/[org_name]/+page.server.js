export async function load({ params }) {
	//const post = await getPostFromDatabase(params.slug);

	const tests = [
		{
			name: 'Test',
			email: 'test@gmail.com'
		},
		{
			name: 'Test2',
			email: 'test2@gmail.com'
		}
	];

	return { tests, params };
}
