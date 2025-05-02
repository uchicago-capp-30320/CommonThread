# setup

## Developing

Download npm if you have not already [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

To set up a local development environment, follow these steps:

1. **Install Dependencies**: If you haven't already, install the project dependencies by running:

```bash
npm install
```

2. **Start the Development Server**: After installing the dependencies, you can start the development server. This will allow you to view your app in a web browser and see changes in real-time. Run the following command:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Linting

```bash
npm run format
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
