<template>
  <div id="mainContainer">
    <div id="innerContainer">
      <div id="leftBar">
        <NavBar></NavBar>
        <div class="conversationList">
          <router-link :to="{name:'Conversation', params: {conversationId: conversation.id}}"
                       v-for="conversation in conversations" :key="conversation.id">
            <Conversation :conversation="conversation"></Conversation>
          </router-link>
        </div>
      </div>
      <div id="conversationView">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>

import NavBar from "@/components/NavBar";
import Conversation from "@/components/Conversation";
import {mapActions, mapGetters} from "vuex";

export default {
  name: "Base",
  components: {Conversation, NavBar},
  computed: {
    ...mapGetters(['conversations'])
  },
  methods: {
    ...mapActions(['loadConversations'])
  },
  mounted() {
    this.loadConversations()
  }
};
</script>

<style scoped>
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
  background-color: rgba(255,255,255,0.5);

}

.router-link-active div {
  @apply bg-gray-200;
}

.conversationList {
  @apply overflow-y-scroll flex-grow;
}
</style>
