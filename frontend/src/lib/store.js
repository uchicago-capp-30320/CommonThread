import { writable, readable } from 'svelte/store';
import { browser } from '$app/environment';

export const ipAddress = import.meta.env.VITE_API_BASE;

export const accessToken = writable((browser && localStorage.getItem('accessToken')) || '');
accessToken.subscribe((val) => {
	if (browser) return (localStorage.accessToken = val);
});

export const refreshToken = writable((browser && localStorage.getItem('refreshToken')) || '');
refreshToken.subscribe((val) => {
	if (browser) return (localStorage.refreshToken = val);
});

export const userExpirationTimestamp = writable(
	(browser && localStorage.getItem('userExpirationTimestamp')) || ''
);
userExpirationTimestamp.subscribe((val) => {
	if (browser) return (localStorage.userExpirationTimestamp = val);
});
