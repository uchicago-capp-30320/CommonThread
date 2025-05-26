import adapter from '@sveltejs/adapter-node';

import { sveltePreprocess } from 'svelte-preprocess';

// eslint-disable-next-line no-unused-vars
/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: sveltePreprocess({
		// scss: {
		// 	prependData: "@import 'node_modules/bulma/bulma.scss';"
		// }
	}),
	// Remove vite-plugin-svelte warnings about unused CSS selectors
	onwarn: (warning, handler) => {
		const { code, frame } = warning;
		if (code === 'css-unused-selector') return;
		handler(warning);
	},
	kit: {
		adapter: adapter()
	}
};

export default config;
