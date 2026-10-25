<template>
  <div class="mainBlock">
    <div class="header">
      <div class="headerInner">
        <h3 v-if="conversation">{{ conversation.party }}</h3>
        <a href="#" @click="deleteConversation">
          <font-awesome-icon icon="trash"></font-awesome-icon>
        </a>
      </div>
    </div>
    <div class="messages" ref="messageContainer">
      <template v-if="conversation">
        <div class="flex-grow"></div>
        <div class="message" :class="{ party: message.inbound }" v-for="message in conversation.messages"
             :key="message.id">
          <div>{{ message.message }}</div>
        </div>
      </template>
    </div>
    <div class="compose">
      <div class="compose-inner">
        <input type="text" placeholder="Type message..." @focus="setRead" v-model="message">
        <button :disabled="!valid" @click="sendMessage">
          <font-awesome-icon icon="paper-plane"></font-awesome-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import {mapGetters} from "vuex";

export default {
  name: "Conversation",
  data() {
    return {
      conversation: null,
      messages: [],
      message: ""
    }
  },
  computed: {
    ...mapGetters(['conversations']),
    valid() {
      return this.message && this.message.length;
    }
  },
  methods: {
    async getConversation() {
      this.conversation = this.conversations.find(x => x.id === this.$route.params.conversationId)
      if (this.conversation && !this.conversation.messages) {
        const messagesResponse = await this.$http.get(`sms/conversations/${this.$route.params.conversationId}`)
        Vue.set(this.conversation, "messages", messagesResponse.data.messages)
        await this.$nextTick()
      }
      await this.setRead()
      const container = this.$refs.messageContainer;
      container.scrollTop = container.scrollHeight;
    },
    async setRead() {
      if (this.conversation && this.conversation.unreadCount > 0) {
        await this.$http.post(`sms/conversations/${this.$route.params.conversationId}/read`)
      }
    },
    async sendMessage() {
      const sendProc = this.$http.post(`sms/conversations/${this.$route.params.conversationId}`, {message: this.message});
      this.message = "";
      await sendProc;
    },
    async deleteConversation() {
      if (confirm("Are you sure you want to delete this conversation and all messages?")) {
        await this.$http.delete(`sms/conversations/${this.$route.params.conversationId}`)
        this.$router.push({name: 'Home'})
      }
    }
  },
  mounted() {
    this.getConversation()
  },
  watch: {
    $route(to, from) {
      this.getConversation()

    },
    conversations() {
      this.getConversation()
    }
  }
}
</script>

<style scoped>
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