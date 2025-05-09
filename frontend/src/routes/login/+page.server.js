import { fail, redirect } from '@sveltejs/kit';

// Look for credentials to decide if login is needed
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

// Praveen's solution
// // Send user's info for login
// const loginData = {

// }

// export async function attemptLogin(loginData) {
// 	console.log("Hello")
// }

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		// Request and wait form form data
		let data = await request.formData();
		console.log('LOGIN ➤ Received Login form data from user');
		console.log(data);

		// Parse information as expected by backend
		// When using several input html components (as bulma's form do),
		// Svelte renders the form data as an array of name-value pairs
		// for every element in the form. It can be unpacked with:
		// Ref: https://stackoverflow.com/questions/71769084/sveltekit-unable-to-read-data-from-post-formdata
		let post_data = Object.fromEntries(data);

		console.log('LOGIN ➤ Reformatted data from login form');
		console.log(post_data);

		// Check that user has token to register in DB
		data['token'] = cookies.get('token');

		// Send POST request to login endpoint
		console.log('LOGIN ➤ Send POST request to login endpoint');
		console.log(data);

		const response = await fetch('http://127.0.0.1:8000/login', {
			method: 'POST',
			body: JSON.stringify({ post_data }),
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

		const ok = response_data.success;

		// Handle redirect if login is successful
		if (ok) {
			// TODO: replace harcoded org-austin with variable from db
			// Get user org and handle redirect
			const org = 'org-austin';

			return redirect(303, ['/org/', org].join(''));
		} else {
			return redirect(303, '/signup');
		}
	}
};
