# LiveSMS v2: Firebase

SvelteKit frontend, Firestore, and Cloud Functions (`functions/src/index.ts`) in `europe-west2`.
See the [top-level README](../README.md) for the architecture and how it compares with v1.

```sh
cp .env.example .env            # Firebase web app config
npm install && (cd functions && npm install)
firebase emulators:start
npm run dev
```
