<script>
	import { onDestroy } from 'svelte';
	import { page } from '$app/stores';

	import { library } from '@fortawesome/fontawesome-svg-core';
	import { faPaperPlane, faTrash } from '@fortawesome/free-solid-svg-icons';
	import {
		collection,
		doc,
		query,
		orderBy,
		onSnapshot,
		getDoc,
		deleteDoc,
		updateDoc,
		addDoc
	} from 'firebase/firestore';
	import { COLLECTION_USERS, firestore, auth, COLLECTION_CONVERSATIONS, COLLECTION_MESSAGES } from '$lib/firebase';
	import { onAuthStateChanged } from 'firebase/auth';
	import { goto } from '$app/navigation';

	library.add(faTrash, faPaperPlane);

	let conversationRef = null;
	let conversation = null;
	let messagesRef = null;
	let messages = [];
	let message = '';
	let unsubscribe = null;
	let user = null;

	async function loadConversation() {
		if (unsubscribe) {
			unsubscribe();
		}

		if (user && $page.params.conversationId) {
			conversationRef = doc(firestore, COLLECTION_USERS,
				user.uid, COLLECTION_CONVERSATIONS,
				$page.params.conversationId);
			conversation = await getDoc(conversationRef);
			messagesRef = collection(conversationRef, COLLECTION_MESSAGES);
			unsubscribe = onSnapshot(query(messagesRef, orderBy('timestamp', 'asc')), (documents) => {
				messages = documents.docs.map((d) => d.data());
			});
		}
	}

	onDestroy(onAuthStateChanged(auth, (value) => {
		user = value;
		loadConversation();
	}));

	onDestroy(page.subscribe(loadConversation));

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});

	async function deleteConversation() {
		if (conversationRef && confirm('Are you sure you want to delete this conversation and all messages?')) {
			console.log(conversationRef);
			await deleteDoc(conversationRef);
			await goto('/');
		}
	}

	async function setRead() {
		if (conversationRef) {
			await updateDoc(conversationRef, { read: true, unreadCount: 0 });
		}
	}

	async function sendMessage() {
		if (messagesRef) {
			await addDoc(messagesRef, {
				inbound: false,
				timestamp: new Date(),
				message
			});
		}
		message = '';
	}

	$: valid = message.length === 0;
	$: conversationData = conversation ? conversation.data() : null;
	$: title = conversationData ? conversationData.party : 'Conversation';

</script>

<svelte:head>
	<title>LiveSMS - {title}</title>
</svelte:head>

<div class='mainBlock'>
	<div class='header'>
		<div class='headerInner'>
			{#if conversationData}<h3>{conversationData.party}</h3>{/if}
			<a href='#' on:click={deleteConversation}>
				<i class='fa fa-trash'></i>
			</a>
		</div>
	</div>
	<div class='messages' ref='messageContainer'>
		{#if messages}
			<div class='flex-grow'></div>
			{#each messages as message}
				<div class='message' class:party={message.inbound}>
					<div>{message.message}</div>
				</div>
			{/each}
		{/if}
	</div>
	<div class='compose'>
		<div class='compose-inner'>
			<input type='text' placeholder='Type message...' on:focus={setRead} bind:value={message}>
			<button disabled={valid} on:click={sendMessage}>
				<i class='fa fa-paper-plane'></i>
			</button>
		</div>
	</div>
</div>

<style>
    .mainBlock {
        @apply flex flex-col h-full;
    }

    .messages {
        @apply flex-grow p-4 overflow-y-scroll;
    }

    .header {
        @apply p-4 bg-gray-100 flex-none;
    }

    .compose {
        @apply bg-gray-100 flex-none p-4;
    }

    .compose-inner {
        @apply flex flex-row;
    }

    .compose-inner input {
        @apply flex-grow;
    }

    .compose-inner button {
        @apply flex-none w-16 h-16 rounded-full ml-4;
    }

    .headerInner {
        @apply flex flex-row;
    }

    .headerInner h3 {
        @apply flex-grow;
    }

    .message {
        @apply flex flex-row-reverse;
    }

    .message div {
        @apply rounded border-purple-400 border shadow p-2 text-sm my-2 bg-purple-200 flex-none;
    }

    .message.party {
        @apply flex-row;
    }

    .message.party div {
        @apply bg-white border-gray-200;
    }
</style>
