// look into httpOnly: true for cookies
// TODO figure out how to send promise for placeholder on page

export async function load({ params, cookies, fetch }) {
	// Return a promise that the page can handle
	const getDataPromise = async () => {
		// Use the provided fetch parameter which handles environment appropriately
		const response = await fetch(`http://127.0.0.1:8000/org/1/`);
		const data = await response.json();
		return data;
	};

	// Return the promise directly
	return {
		storiesPromise: getDataPromise(),
		params
	};

	// get cookies
	//const accessToken = cookies.get('ct_access_token');
	//const refreshToken = cookie.get('ct_refresh_token');

	// const response = await fetch(`http://127.0.0.1:8000/stories/`, {
	// 	method: 'GET',
	// 	headers: {
	// 		'Content-Type': 'application/json',
	// 		Authorization: `Bearer ${accessToken}`
	// 	}
	// });

	// if (!response.ok) {
	// 	const statusCode = response.status;
	// 	if (statusCode === 299) {
	// 		// need to refresh token
	// 		const refreshResponse = await fetch(`http://127.0.0.1:8000/login/create_access`, {
	// 			method: 'POST',
	// 			headers: {
	// 				'Content-Type': 'application/json'
	// 			},
	// 			body: JSON.stringify({
	// 				refresh_token: cookie.get('ct_refresh_token')
	// 			})
	// 		});
	// 		if (!refreshResponse.ok) {
	// 			const statusCode = refreshResponse.status;
	// 			if (statusCode === 401) {
	// 				// redirect to login page
	// 				return { status: 401, error: new Error('Unauthorized') };
	// 			} else {
	// 				// save new access token
	// 				const data = await refreshResponse.json();
	// 				cookie.set('ct_access_token', data.access_token, { path: '/' });

	// 				// retry the original request
	// 				const retryResponse = await fetch(`test`, {
	// 					method: 'GET',
	// 					headers: {
	// 						'Content-Type': 'application/json',
	// 						Authorization: `Bearer ${data.access_token}`
	// 					}
	// 				});
	// 				if (!retryResponse.ok) {
	// 					return { status: retryResponse.status, error: new Error('Failed to fetch stories') };
	// 				}
	// 				const retryData = await retryResponse.json();
	// 				const { stories } = retryData;
	// 				return { stories, params };
	// 			}
	// 		}
	// 	}
	// }
}
