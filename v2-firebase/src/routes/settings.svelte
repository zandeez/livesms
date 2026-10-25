<script>
	import { onAuthStateChanged } from 'firebase/auth';
	import { doc, getDoc, setDoc } from 'firebase/firestore';

	import { onDestroy } from 'svelte';
	import { auth, firestore, COLLECTION_USERS, FIREBASE_PROJECT_ID, FUNCTIONS_REGION } from '$lib/firebase';

	import { library } from '@fortawesome/fontawesome-svg-core';
	import { faSave } from '@fortawesome/free-solid-svg-icons';

	library.add(faSave);

	let user = null;
	let userSettingsRef = null;
	let userSettings = null;


	onDestroy(onAuthStateChanged(auth, async (value) => {
		if (value) {
			user = value;
			userSettingsRef = doc(firestore, COLLECTION_USERS, value.uid);
			const userSettingsDoc = await getDoc(userSettingsRef);
			userSettings = userSettingsDoc.data();
			if (!userSettings) {
				userSettings = {
					number: ''
				};
			}
			if (!userSettings.webhook_token) {
				// Secret for the inbound webhook URL; saved straight away so the URL shown is always valid
				userSettings.webhook_token = generateToken();
				await setDoc(userSettingsRef, { webhook_token: userSettings.webhook_token }, { merge: true });
			}
		}
	}));

	function generateToken() {
		const bytes = new Uint8Array(32);
		crypto.getRandomValues(bytes);
		return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
	}

	async function saveSettings() {
		await setDoc(userSettingsRef, { ...userSettings });
		alert('Settings saved.');
	}

	$: webhookUrl = user && userSettings ? `https://${FUNCTIONS_REGION}-${FIREBASE_PROJECT_ID}.cloudfunctions.net/sinchWebhook/${user.uid}?token=${userSettings.webhook_token}` : null;
</script>

<svelte:head>
	<title>LiveSMS - Settings</title>
</svelte:head>

<div class='mainBlock'>
	<div class='header'>
		<div class='headerInner'>
			<h3>Settings</h3>
			<a href='#' on:click={saveSettings}>
				<i class='fa fa-save'></i>
			</a>
		</div>
	</div>
	{#if userSettings}
		<div class='settings'>
			<label for='number'>Number</label>
			<input type='text' id='number' name='number' bind:value={userSettings.number}>
			<label for='apiAccount'>API Account</label>
			<input type='text' id='apiAccount' bind:value={userSettings.sinch_account}>
			<label for='apiPassword'>API Password</label>
			<input type='text' id='apiPassword' bind:value={userSettings.sinch_password}>
			<label for='apiWebhook'>Incoming Webhook</label>
			<input type='text' id='apiWebhook' value={webhookUrl} disabled='disabled'>
		</div>
	{/if}
</div>

<style>
    .mainBlock {
        @apply flex flex-col h-full;
    }

    .header {
        @apply p-4 bg-gray-100 flex-none;
    }

    .headerInner {
        @apply flex flex-row;
    }

    .headerInner h3 {
        @apply flex-grow;
    }

    .settings {
        @apply p-4 bg-white flex-grow;
    }
</style>

