import { writable } from 'svelte/store';
import { goto } from '$app/navigation';

export const errorStore = writable(null);

// THIS MIGHT BE AN OVEKILL BUT THE IDEA IS TO HAVE A CENTRALIZED PLACE TO HANDLE ALL ERRORS
// A LOT OF THESE MIGHT NOT BE NEEDED OR MIGHT BE REDUNDANT

export const ERROR_ACTIONS = {
	NO_TOKEN: {
		message: 'No token provided',
		actions: [{ label: 'Login', handler: () => goto('/login') }]
	},
	INVALID_TOKEN: {
		message: 'Invalid token',
		actions: [{ label: 'Login', handler: () => goto('/login') }]
	},
	ACCESS_TOKEN_EXPIRED: {
		message: 'Access token has expired',
		actions: [{ label: 'Refresh Page', handler: () => window.location.reload() }]
	},
	REFRESH_TOKEN_EXPIRED: {
		message: 'Your login session has expired. Please log in again.',
		actions: [{ label: 'Login Again', handler: () => goto('/login') }]
	},
	INSUFFICIENT_PERMISSIONS: {
		message: 'You do not have permission to perform this action.',
		actions: [{ label: 'Go Back', handler: () => history.back() }]
	},
	USER_NOT_IN_ORG: {
		message: 'You are not a member of this organization.',
		actions: [{ label: 'Go Back', handler: () => history.back() }]
	},
	INVALID_CREDENTIALS: {
		message: 'Invalid username or password',
		actions: [
			{ label: 'Try Again', handler: () => {} },
			{ label: 'Sign up', handler: () => goto('/signup') }
		]
	},

	NOT_FOUND: {
		message: 'The requested resource was not found.',
		actions: [{ label: 'Go Back', handler: () => history.back() }]
	},
	STORY_NOT_FOUND: {
		message: "The story you're looking for doesn't exist",
		actions: [
			{
				label: 'Go to Projects',
				handler: (context) => goto(`/org/${context.org_id}`)
			},
			{
				label: 'Go Home',
				handler: () => goto('/')
			}
		]
	},
	PROJECT_NOT_FOUND: {
		message: 'The requested project was not found.',
		actions: [
			{
				label: 'Go Home',
				handler: () => goto('/')
			}
		]
	},
	ORG_NOT_FOUND: {
		message: "The organization you're looking for doesn't exist",
		actions: [
			{
				label: 'Go Home',
				handler: () => goto('/')
			}
		]
	},
	USER_NOT_FOUND: {
		message: 'The requested user was not found.',
		actions: [{ label: 'Go Back', handler: () => history.back() }]
	},

	INVALID_JSON: {
		message: 'The request body is not valid.',
		actions: [{ label: 'Try Again', handler: 'retry' }]
	},
	MISSING_REQUIRED_FIELDS: {
		message: 'Missing required fields',
		actions: [{ label: 'OK', handler: () => {} }]
	},
	INVALID_FIELD_FORMAT: {
		message: 'Invalid field format',
		actions: [{ label: 'OK', handler: () => {} }]
	},

	DUPLICATE_USERNAME: {
		message: 'Username already exists',
		actions: [{ label: 'Try Different Username', handler: () => {} }]
	},
	DUPLICATE_ORG_NAME: {
		message: 'Organization name already exists',
		actions: [{ label: 'Try Different Name', handler: () => {} }]
	},

	INTERNAL_ERROR: {
		message: 'The issue is on our end. Please try again later or contact support.',
		actions: [
			{ label: 'Try Again', handler: 'retry' },
			{ label: 'Contact Support', handler: () => goto('/home') }
		]
	},
	DATABASE_ERROR: {
		message: 'The database operation failed. Please try again later or contact support.',
		actions: [{ label: 'Try Again', handler: 'retry' }]
	},
	S3_ERROR: {
		message: 'The file operation failed. Please try again later or contact support.',
		actions: [{ label: 'Try Again', handler: 'retry' }]
	},

	NETWORK_ERROR: {
		message: 'Unable to connect to server. Check your internet connection.',
		actions: [{ label: 'Try Again', handler: 'retry' }]
	},

	STORY_NOT_IN_ORG: {
		message: "This story doesn't belong to this organization",
		actions: [
			{
				label: 'Go Back',
				handler: () => history.back()
			},
			{
				label: 'Go Home',
				handler: () => goto('/')
			}
		]
	}
};

// Fallback system: HTTP status codes when descriptive codes aren't available
export const STATUS_CODE_FALLBACKS = {
	400: 'INVALID_JSON',
	401: 'INVALID_TOKEN',
	403: 'INSUFFICIENT_PERMISSIONS',
	404: 'NOT_FOUND',
	409: 'ALREADY_EXISTS',
	422: 'INVALID_STATE_TRANSITION',
	500: 'INTERNAL_ERROR',
	503: 'DATABASE_ERROR'
};

// Smart error resolution function
export function resolveErrorCode(errorResponse) {
	console.log('Resolving error code for:', errorResponse);
	// Try to get descriptive code from backend first
	if (errorResponse?.code && ERROR_ACTIONS[errorResponse.code]) {
		return errorResponse.code;
	}

	// Fall back to HTTP status code mapping
	if (errorResponse?.status && STATUS_CODE_FALLBACKS[errorResponse.status]) {
		return STATUS_CODE_FALLBACKS[errorResponse.status];
	}

	// Ultimate fallback
	return 'INTERNAL_ERROR';
}

export function showError(errorCodeOrResponse, retryFunction = null, context = {}) {
	let errorCode;

	if (typeof errorCodeOrResponse === 'string') {
		errorCode = errorCodeOrResponse;
	} else {
		errorCode = resolveErrorCode(errorCodeOrResponse);
	}

	errorStore.set({
		code: errorCode,
		retryFunction: retryFunction,
		context: context
	});
}
