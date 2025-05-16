import { ipAddress } from '$lib/store.js';

export async function authRequest(url, method, accessToken, refreshToken) {
	// Get the access token from cookies
	console.log('accessToken', accessToken);
	console.log('ipAddress', ipAddress + url);

	const ogResponse = await fetch(ipAddress + url, {
		method: method,
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${accessToken}`
		}
	});

	if (ogResponse.status === 299) {
		const newAccessToken = getNewAccessToken(refreshToken);

		if (newAccessToken) {
			// update access token
			accessToken.value = newAccessToken;
		} else {
			console.log('Failed to get new access token');
			return;
		}
		// retry original request with new access token
		const retryResponse = await fetch(ipAddress + url, {
			method: method,
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${accessToken}`
			}
		});
		if (retryResponse.status === 200) {
			data = await retryResponse.json();
			return data;
		} else {
			console.log('Retry request failed');
			return;
		}
	} else {
		console.log('Original request failed');
	}
}

async function getNewAccessToken(refreshToken) {
	const refreshResponse = await fetch(`${ipAddress}/login/create_access`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		credentials: 'include'
	});
	if (refreshResponse.status === 200) {
		const data = await refreshResponse.json();
		return data.access_token;
	} else {
		console.error('Failed to get new access token');
		return null;
	}
}
