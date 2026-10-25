<script>
	import { onAuthStateChanged, signOut } from 'firebase/auth';
	import { library } from '@fortawesome/fontawesome-svg-core';
	import { faPlus, faCog, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
	import { auth, COLLECTION_CONVERSATIONS, COLLECTION_USERS, firestore } from '$lib/firebase';
	import { collection, query, where, getDocs, addDoc } from 'firebase/firestore';
	import { onDestroy } from 'svelte';
	import { goto } from '$app/navigation';

	library.add(faPlus, faCog, faSignOutAlt);

	let newOpen = false;
	let newNumber = '';
	let user = null;

	onDestroy(onAuthStateChanged(auth, (value) => {
		user = value;
	}));

	$: valid = !(newOpen && newNumber);

	function toggleNew() {
		newOpen = !newOpen;
	}

	async function logout() {
		await signOut(auth);
	}

	async function newConversation() {
		newOpen = false;

		const conversationCollection = collection(firestore, COLLECTION_USERS, user.uid, COLLECTION_CONVERSATIONS);
		const existingQuery = query(conversationCollection, where('party', '==', newNumber));
		const queryResult = await getDocs(existingQuery);
		if (queryResult.docs.length) {
			const conversationDoc = await queryResult.docs[0].id;
			await goto(`/conversation/${conversationDoc}`);
		} else {
			const newDoc = await addDoc(conversationCollection, { party: newNumber, timestamp: new Date(), read: true });
			await goto(`/conversation/${newDoc.id}`);
		}
	}
</script>

<div>
	<nav>
		<span><a href='/'>LiveSMS</a></span>
		<a on:click={toggleNew} href='#'>
			<i class='fa fa-plus'></i>
		</a>
		<a href='/settings'>
			<i class='fa fa-cog'></i>
		</a>
		<a on:click={logout} href='#'>
			<i class='fa fa-sign-out-alt'></i>
		</a>
	</nav>
	{#if newOpen}
		<div class='newConversation'>
			<input type='text' placeholder='Number...' bind:value={newNumber}>
			<button disabled={valid} on:click={newConversation}>
				<i class='fa fa-plus'></i>
			</button>
		</div>
	{/if}
</div>


<style scoped>
    nav {
        @apply p-4 bg-gray-100 flex;
    }

    nav span {
        @apply flex-grow;
    }

    img {
        @apply rounded-full h-5;
    }

    .flex * {
        @apply mx-1;
    }

    .fix-margins {
        margin-bottom: -10px;
        margin-top: -10px;
    }

    svg {
        @apply mx-1;
    }

    input {
        @apply flex-grow;
    }

    button {
        @apply rounded-full text-sm ml-1 flex-none w-12;
    }

    .newConversation {
        @apply flex flex-row p-4 bg-gray-100;
    }
</style>
