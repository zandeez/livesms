<template>
  <div>
    <nav>
      <span><router-link to="/">LiveSMS</router-link></span>
      <a @click="toggleNew" href="#">
        <font-awesome-icon icon="plus"></font-awesome-icon>
      </a>
      <router-link :to="{name: 'Settings'}">
        <font-awesome-icon icon="cog"></font-awesome-icon>
      </router-link>
      <a @click="logout" href="#">
        <font-awesome-icon icon="sign-out-alt"></font-awesome-icon>
      </a>
    </nav>
    <div class="newConversation" v-if="newOpen">
      <input type="text" placeholder="Number..." v-model="newNumber">
      <button :disabled="!valid" @click="newConversation">
        <font-awesome-icon icon="plus"></font-awesome-icon>
      </button>
    </div>
  </div>
</template>

<script>
import {clearAuthTokens} from "axios-jwt";

export default {
  name: "NavBar",
  data() {
    return {
      newOpen: false,
      newNumber: ""
    }
  },
  computed: {
    valid() {
      return this.newNumber && this.newNumber.length
    }
  },
  methods: {
    toggleNew() {
      this.newOpen = !this.newOpen
    },
    async newConversation() {
      this.newOpen = false
      const conversationReq = this.$http.post("sms/conversations", {party: this.newNumber})
      this.newNumber = ""
      const conversationResponse = await conversationReq
      await this.$router.push({name: 'Conversation', params: {conversationId: conversationResponse.data.id}})
    },
    logout() {
      clearAuthTokens()
      this.$store.commit("clearSession")
      this.$router.push({name: "Login"})
    }
  }
};
</script>

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
