import { fail, redirect } from '@sveltejs/kit';

export const load = async ({ cookies }) => {
	// Check if the user is already logged in
	const ct_access_token = cookies.get('ct_access_token');

	console.log('ct_access_token from cookie', ct_access_token);
	// if (ct_access_token) {
	//     // If logged in, redirect to the dashboard or home page
	//     throw redirect(302, '/org/org-austin');
	// }

	return {};
};

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		let test = await request.formData();
		console.log(test);
		let data = {
			username: 'alice',
			password: 'pass123'
		};

		//data['token'] = cookies.get('token')

		const response = await fetch('http://127.0.0.1:8000/login', {
			method: 'POST',
			body: JSON.stringify({ data }),
			headers: {
				'Content-Type': 'application/json'
			}
		});
		let response_data = {};
		await response.json().then((d) => {
			response_data = d;
		});
		console.log(response_data);

		await cookies.set('ct_access_token', response_data.access_token, { path: '/' });
		cookies.set('ct_refresh_token', response_data.refresh_token, { path: '/' });

		// handle redirect if need
		if (response.ok) {
			return redirect(303, '/org/org-austin');
		}
	}
};
