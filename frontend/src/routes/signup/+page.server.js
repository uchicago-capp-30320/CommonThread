import { fail, redirect } from '@sveltejs/kit';

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		console.log("Signup request sent")
		let data = await request.formData();
		console.log('Submited form data:' + data);

		// TODO: Figure out why data from form is emmpty 
		// Ref for form actions: https://svelte.dev/docs/kit/form-actions

		const response = await fetch('http://127.0.0.1:8000/user/create', {
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
			// TODO: replace harcoded org-austin with variable from db
			window.prompt('New user was sucessfully created! Now please login.');
			return redirect(303, '/login');
		} else {
			window.prompt('Invalid user or password, please try again.');
		}
	}
};

