<script>
	export let conversation;

	$: data = conversation.data();
</script>

<div class='mainBlock'>
	<h3>{ data.party }</h3>
	<div>
		<span class='lastMessage'>{ data.lastMessage || "" }&nbsp;</span>
		{#if data.unreadCount}<span class='unread'>{ data.unreadCount }</span>{/if}
	</div>
</div>

<style>
    h3 {
        font-weight: bold;
    }

    .mainBlock {
        @apply p-3 border border-gray-200;
    }

    .mainBlock div {
        @apply flex flex-row;
    }

    .lastMessage {
        @apply flex-grow truncate;
    }

    .unread {
        @apply inline-block bg-purple-500 text-white rounded-full p-1 text-sm w-8 text-center;
    }
</style>
