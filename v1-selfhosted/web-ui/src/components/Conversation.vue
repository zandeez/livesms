<template>
  <div class="mainBlock">
    <h3>{{ conversation.party }}</h3>
    <div>
      <span class="lastMessage">{{ conversation.lastMessage }}</span>
      <span class="unread" v-if="conversation.unreadCount">{{conversation.unreadCount}}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "Conversation",
  props: ['conversation']

}
</script>

<style scoped>
h3{
  font-weight: bold;
}

.mainBlock {
  @apply p-3 border border-gray-200;
}
.mainBlock div {
  @apply flex flex-row
}

.lastMessage {
  @apply flex-grow truncate;
}

.unread {
  @apply inline-block bg-purple-500 text-white rounded-full p-1 text-sm w-8 text-center;
}
</style>