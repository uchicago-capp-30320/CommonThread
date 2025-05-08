// look into httpOnly: true for cookies

export async function load({ params, cookie, fetch }) {
	// get cookies
	const accessToken = cookie.get('ct_access_token');
	const refreshToken = cookie.get('ct_refresh_token');

	const response = await fetch(`http://127.0.0.1:8000/stories/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${accessToken}`
		},
		body: JSON.stringify({
			refresh_token: refreshToken
		})
	});

	if (!response.ok) {
		const statusCode = response.status;
		if (statusCode === 299) {
			// need to refresh token
			const refreshResponse = await fetch(`http://127.0.0.1:8000/login/create_access`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					refresh_token: cookie.get('ct_refresh_token')
				})
			});
			if (!refreshResponse.ok) {
				const statusCode = refreshResponse.status;
				if (statusCode === 401) {
					// redirect to login page
					return { status: 401, error: new Error('Unauthorized') };
				} else {
					// save new access token
					const data = await refreshResponse.json();
					cookie.set('ct_access_token', data.access_token, { path: '/' });

					// retry the original request
					const retryResponse = await fetch(`test`, {
						method: 'GET',
						headers: {
							'Content-Type': 'application/json',
							Authorization: `Bearer ${data.access_token}`
						}
					});
					if (!retryResponse.ok) {
						return { status: retryResponse.status, error: new Error('Failed to fetch stories') };
					}
					const retryData = await retryResponse.json();
					const { stories } = retryData;
					return { stories, params };
				}
			}
		}
	}
}

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
