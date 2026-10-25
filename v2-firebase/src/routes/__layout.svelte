<script>
	import '../../app.postcss';

	import { page } from '$app/stores';
	import { onDestroy } from 'svelte';
	import { onAuthStateChanged } from 'firebase/auth';
	import { onSnapshot, collection, query, orderBy } from 'firebase/firestore';
	import { goto } from '$app/navigation';
	import { auth, COLLECTION_CONVERSATIONS, COLLECTION_USERS, firestore } from '$lib/firebase';
	import NavBar from '../components/NavBar.svelte';

	import { dom } from '@fortawesome/fontawesome-svg-core';
	import Conversation from '../components/Conversation.svelte';

	dom.watch();

	let unsubscribe = null;
	let conversations = [];

	onDestroy(onAuthStateChanged(auth, (user) => {
		if (!user) {
			goto(`/login?next=${encodeURIComponent($page.path)}`);
		}
		else {
			const conversationCollection = collection(firestore, COLLECTION_USERS, user.uid, COLLECTION_CONVERSATIONS);
			const sortedConversationCollection = query(conversationCollection, orderBy("timestamp", "desc"));
			unsubscribe = onSnapshot(sortedConversationCollection, (documents) => {
				conversations = documents.docs;
			});
		}
	}));

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});


</script>

<div id='mainContainer'>
	<div id='innerContainer'>
		<div id='leftBar'>
			<NavBar></NavBar>
			<div class='conversationList'>
				{#each conversations as conversation}
					<a href='/conversation/{conversation.id}'>
						<Conversation conversation={conversation}></Conversation>
					</a>
				{/each}
			</div>
		</div>
		<div id='conversationView'>
			<slot></slot>
		</div>
	</div>
</div>

<style>
    #mainContainer {
        @apply h-screen p-12;
    }

    #innerContainer {
        @apply border border-gray-200 rounded shadow-lg h-full flex flex-row;
    }

    #leftBar {
        @apply w-64 flex flex-col h-full bg-white;
    }

    #conversationView {
        @apply flex-grow border-gray-200 border;
        background-color: rgba(255, 255, 255, 0.5);

    }

    .router-link-active div {
        @apply bg-gray-200;
    }

    .conversationList {
        @apply overflow-y-scroll flex-grow;
    }
</style>
