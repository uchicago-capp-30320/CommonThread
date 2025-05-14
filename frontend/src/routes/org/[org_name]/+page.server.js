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

const dataRequest = async (accessToken) => {
	let response = await fetch(`http://127.0.0.1:8000/org/1/1`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${accessToken}`
		}
	});

	return response;
};

export async function load({ params, cookies, fetch }) {
	const getDataPromise = async () => {
		let data;

		//get cookies
		const accessToken = cookies.get('ct_access_token');
		const refreshToken = cookies.get('ct_refresh_token');

		console.log('accessToken from cookie', accessToken);
		console.log('refreshToken from cookie', refreshToken);

		const ogResponse = await dataRequest(accessToken);
		console.log('making first ogResponse', ogResponse.status);

		if (!ogResponse.ok) {
			const statusCode = ogResponse.status;
			// check if error from refresh token expired
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

				console.log('refreshResponse status', refreshResponse.status);

				if (!refreshResponse.ok) {
					// error

					return { data, status: refreshResponse.status, statusText: refreshResponse.statusText };
				}
				// save new access token
				const refreshData = await refreshResponse.json();
				const newAccessToken = refreshData.access_token;
				console.log('refreshData', refreshData);

				// retry the original request
				const retryResponse = await dataRequest(newAccessToken);

				if (!retryResponse.ok) {
					// if retry fails, return the response
					return { data, status: retryResponse.status, statusText: retryResponse.statusText };
				} else if (retryResponse.ok) {
					// if retry succeeds, return the data
					data = await retryResponse.json();
					console.log('retryResponse data', data);
					//ookies.set('ct_access_token', newAccessToken, { path: '/' });
					return { data: data, status: retryResponse.status, statusText: retryResponse.statusText };
				}
			} else {
				// other issue
				return { data: data, status: ogResponse.status, statusText: ogResponse.statusText };
			}
		} else {
			// if response is ok, return the data
			data = await ogResponse.json();
			return { data: data, status: ogResponse.status, statusText: ogResponse.statusText };
		}
	};
	return {
		dataPromise: getDataPromise(),
		params
	};
}
