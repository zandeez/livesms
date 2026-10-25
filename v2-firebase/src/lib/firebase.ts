import { initializeApp } from "firebase/app";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFunctions, connectFunctionsEmulator } from "firebase/functions";
import { dev } from "$app/env";

export const FIREBASE_PROJECT_ID = import.meta.env.VITE_FIREBASE_PROJECT_ID as string;
export const FUNCTIONS_REGION = "europe-west2";

const firebaseApp = initializeApp({
	apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string,
	authDomain: `${FIREBASE_PROJECT_ID}.firebaseapp.com`,
	projectId: FIREBASE_PROJECT_ID,
	storageBucket: `${FIREBASE_PROJECT_ID}.appspot.com`,
	messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string,
	appId: import.meta.env.VITE_FIREBASE_APP_ID as string
});

export const auth = getAuth(firebaseApp);
export const firestore = getFirestore(firebaseApp);
export const functions = getFunctions(firebaseApp, FUNCTIONS_REGION);

export const COLLECTION_USERS = "users";
export const COLLECTION_CONVERSATIONS = "conversations";
export const COLLECTION_MESSAGES = "messages";

if (dev) {
	connectAuthEmulator(auth, "http://localhost:9099");
	connectFirestoreEmulator(firestore, "localhost", 8080);
	connectFunctionsEmulator(functions, "localhost", 5001);
}


