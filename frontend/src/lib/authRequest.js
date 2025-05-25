import { ipAddress } from '$lib/store.js';

export async function authRequest(url, method, accessToken, refreshToken, postData) {
	let data;
	// Get the access token from cookies
	//console.log('ipAddress', ipAddress + url);

	const ogResponse = await fetch(ipAddress + url, {
		method: method,
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${accessToken}`
		},
		// if data is not null, send it as the body
		body: postData ? JSON.stringify(postData) : null
	});
	if (ogResponse.status === 200 || ogResponse.status === 201) {
		data = await ogResponse.json();
		return { data, newAccessToken: null };
	}

	if (ogResponse.status === 299) {
		console.log('need to refresh token');
		const newAccessToken = await getNewAccessToken(refreshToken);
		//console.log('newAccessToken', newAccessToken);

		if (!newAccessToken) {
			console.log('Failed to get new access token');
			return;
		}
		// retry original request with new access token
		const retryResponse = await fetch(ipAddress + url, {
			method: method,
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${newAccessToken}`
			}
		});

		if (retryResponse.status === 200) {
			console.log('Retry request successful');
			data = await retryResponse.json();

			return { data, newAccessToken: newAccessToken };
		} else {
			console.log('Retry request failed');
			return;
		}
	} else {
		console.log('Original request failed');
	}
}

async function getNewAccessToken(refreshToken) {
	const refreshResponse = await fetch(`${ipAddress}/create_access`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			refresh_token: refreshToken
		})
	});
	if (refreshResponse.status === 200) {
		const data = await refreshResponse.json();
		return data.access_token;
	} else {
		console.error('Failed to get new access token');
		return null;
	}
}
