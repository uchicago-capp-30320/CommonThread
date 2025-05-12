// look into httpOnly: true for cookies
// TODO figure out how to send promise for placeholder on page

// const getDataPromise = async () => {
// 	// Use the provided fetch parameter which handles environment appropriately
// 	const response = await fetch(`http://127.0.0.1:8000/org/1/1/`);
// 	const data = await response.json();
// 	return data;
// };
// // Return the promise directly
// return {
// 	storiesPromise: getDataPromise(),
// 	params
// };

const dataRequest = async (cookies) => {
	// get cookie
	const accessToken = cookies.get('ct_access_token');

	const response = await fetch(`http://127.0.0.1:8000/org/1/1`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${accessToken}`
		}
	});

	return response;
};

export async function load({ params, cookies, fetch }) {
	// Return a promise that the page can handle
	// const getDataPromise = async () => {
	// 	// Use the provided fetch parameter which handles environment appropriately
	// 	const response = await fetch(`http://127.0.0.1:8000/org/1/1/`);
	// 	const data = await response.json();
	// 	return data;
	// };
	// // Return the promise directly
	// return {
	// 	storiesPromise: getDataPromise(),
	// 	params
	// };
	const getDataPromise = async () => {
		let data;

		//get cookies
		const accessToken = cookies.get('ct_access_token');
		const refreshToken = cookies.get('ct_refresh_token');

		console.log('accessToken from cookie', accessToken);
		console.log('refreshToken from cookie', refreshToken);

		const response = await dataRequest(cookies);
		//console.log('response from dataRequest', response);

		if (response.ok) {
			const statusCode = response.status;
			if (statusCode === 299) {
				console.log('299 response, need to refresh token');
				// need to refresh token
				const refreshResponse = await fetch(`http://127.0.0.1:8000/login/create_access`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						refresh_token: cookies.get('ct_refresh_token')
					})
				});
				// save token

				const statusCode = refreshResponse.status;
				if (statusCode === 401) {
					// redirect to login page
					return { status: 401, error: new Error('Unauthorized') };
				} else if (statusCode === 403) {
					// redirect to login page
					return { status: 403, error: new Error('Forbidden') };
				} else if (statusCode === 404) {
					// redirect to login page
					return { status: 404, error: new Error('Not Found') };
				} else if (statusCode === 500) {
					// redirect to login page
					return { status: 500, error: new Error('Internal Server Error') };
				}
				// save new access token
				data = await refreshResponse.json();
				console.log('data from refreshResponse', data);
				cookies.set('ct_access_token', data.access_token, { path: '/' });

				// retry the original request
				const retryResponse = dataRequest(cookies);
				if (!retryResponse.ok) {
					return { status: retryResponse.status, error: new Error('Failed to fetch stories') };
				}
				const retryStatusCode = retryResponse.status;
				data = await response.json();
				// console.log(data);
				return data;
			} else {
				// you got data
				data = await response.json();
				// console.log(data);
				return data;
			}
		}
	};
	return {
		dataPromise: getDataPromise(),
		params
	};
}
