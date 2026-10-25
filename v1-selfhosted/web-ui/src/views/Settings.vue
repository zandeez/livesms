<template>
  <div class="mainBlock">
    <div class="header">
      <div class="headerInner">
        <h3>Settings</h3>
        <a href="#" @click="saveSettings">
          <font-awesome-icon icon="save"></font-awesome-icon>
        </a>
      </div>
    </div>
    <div class="settings" v-if="user">
      <label for="number">Number</label>
      <input type="text" id="number" name="number" v-model="user.number">
      <label for="apiType">API Type</label>
      <select id="apiType" v-model="user.apiType">
        <option value="simwood">Simwood</option>
        <option value="sinch">Sinch</option>
      </select>
      <label for="apiAccount">API Account</label>
      <input type="text" id="apiAccount" v-model="user.apiAccount">
      <label for="apiUsername">API Username</label>
      <input type="text" id="apiUsername" v-model="user.apiUsername">
      <label for="apiPassword">API Password</label>
      <input type="text" id="apiPassword" v-model="user.apiPassword">
      <label for="apiWebhook">Incoming Webhook</label>
      <input type="text" id="apiWebhook" v-model="webhookUrl" disabled="disabled">
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  data() {
    return {
      user: null
    }
  },
  computed: {
    webhookUrl() {
      if (this.user && this.user.id && this.user.apiType && this.user.webhookToken) {
        return `${process.env.VUE_APP_API_ROOT}${this.user.apiType}/${this.user.id}/webhook?token=${this.user.webhookToken}`
      } else {
        return ""
      }
    }
  },
  methods: {
    async loadUser() {
      const userResponse = await this.$http.get('auth/user')
      this.user = userResponse.data
    },
    async saveSettings() {
      const saveResponse = await this.$http.post('auth/user', this.user)
      alert("Settings saved.")
    }
  },
  async mounted() {
    await this.loadUser()
  }
}
</script>

<style scoped>
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
