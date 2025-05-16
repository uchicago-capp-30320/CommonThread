import { writable, readable } from 'svelte/store';
import { browser } from '$app/environment';

export const ipAddress = 'http://127.0.0.1:8000';

export const accessToken = writable((browser && localStorage.getItem('accessToken')) || 'webjeda');
accessToken.subscribe((val) => {
	if (browser) return (localStorage.accessToken = val);
});

export const refreshToken = writable(
	(browser && localStorage.getItem('refreshToken')) || 'webjeda'
);
refreshToken.subscribe((val) => {
	if (browser) return (localStorage.refreshToken = val);
});
