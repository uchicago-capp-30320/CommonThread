import { ipAddress } from '$lib/store.js';
import { showError, resolveErrorCode } from '$lib/errorStore.js';

export async function authRequest(url, method, accessToken, refreshToken, postData) {
	let data;
	// Get the access token from cookies
	//console.log('ipAddress', ipAddress + url);

	try {
		const ogResponse = await fetch(ipAddress + url, {
			method: method,
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${accessToken}`
			},
			// if data is not null, send it as the body
			body: postData ? JSON.stringify(postData) : null
		});
		console.log('ogResponse', ogResponse);

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
				showError('REFRESH_TOKEN_EXPIRED');
				return null;
			}
			// retry original request with new access token
			const retryResponse = await fetch(ipAddress + url, {
				method: method,
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${newAccessToken}`
				},
				body: postData ? JSON.stringify(postData) : null
			});

			if (retryResponse.status === 200 || retryResponse.status === 201) {
				console.log('Retry request successful');
				data = await retryResponse.json();
				return { data, newAccessToken: newAccessToken };
			} else {
				console.log('Retry request failed');
				const retryErrorData = await retryResponse.json().catch(() => ({}));
				console.error('Retry error data:', retryErrorData);
				showError(retryErrorData.error || { code: 'INTERNAL_ERROR', message: 'Retry failed' });
				return null;
			}
		} else {
			console.log('Original request failed');

			const errorResponseBody = await ogResponse.json().catch(() => ({}));

			console.error('Error response body:', errorResponseBody);

			const NOT_FOUND_NOT_AUTHORIZED_ERRORS = [
				'PROJECT_NOT_FOUND',
				'STORY_NOT_FOUND',
				'ORG_NOT_FOUND',
				'USER_NOT_FOUND',
				'INVALID_CREDENTIALS',
				'INSUFFICIENT_PERMISSIONS',
				'USER_NOT_IN_ORG'
			];

			if (NOT_FOUND_NOT_AUTHORIZED_ERRORS.includes(errorResponseBody.error.code)) {
				return errorResponseBody;
			}
			if (errorResponseBody.error.code === 'REFRESH_TOKEN_EXPIRED') {
				showError(errorResponseBody.error);
				return null;
			}
			return null;
		}
	} catch (networkError) {
		console.error('Network error:', networkError);
		const retryFunction = () => authRequest(url, method, accessToken, refreshToken, postData);
		showError('NETWORK_ERROR', retryFunction);
		return null;
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
		const errorData = await refreshResponse.json().catch(() => ({}));
		showError(errorData.error);
		return null;
	}
}
