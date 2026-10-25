<template>
  <div id="container">
    <div id="window">
      <h1>LiveSMS Login</h1>
      <div v-if="loginError" class="alert danger">
        {{ loginError }}
      </div>
      <form @submit="login($event)">
        <div class="mb-4">
          <label class="block mb-2" for="username">Username</label>
          <input
            id="username"
            name="username"
            placeholder="Username"
            v-model="username"
            :disabled="loginCancel"
          />
        </div>
        <div class="mb-4">
          <label class="block mb-2" for="password">Password</label>
          <input
            id="password"
            name="password"
            placeholder="Password"
            type="password"
            v-model="password"
            :disabled="loginCancel"
          />
        </div>
        <button type="submit" :disabled="!valid">Login</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { setAuthTokens } from "axios-jwt";

export default {
  name: "Login",
  data: function() {
    return {
      username: "",
      password: "",
      loginCancel: null,
      loginError: null
    };
  },
  computed: {
    valid() {
      return (
        this.username &&
        this.username.length &&
        this.password &&
        this.password.length &&
        !this.loginCancel
      );
    }
  },
  methods: {
    async login(event) {
      event.preventDefault();
      this.loginError = null;
      this.loginCancel = axios.CancelToken.source();

      try {
        const res = await this.$http.post(
          "auth/token",
          {
            username: this.username,
            password: this.password
          },
          { cancelToken: this.loginCancel.token }
        );

        setAuthTokens({
          accessToken: res.data.accessToken,
          refreshToken: res.data.refreshToken
        });

        if (this.$route.query.n) {
          await this.$router.push({ path: this.$route.query.n });
        } else {
          await this.$router.push({ name: "Home" });
        }
      } catch (err) {
        console.log(err);
        this.loginError = err.response.data.detail;
        this.$nextTick();
      } finally {
        this.loginCancel = null;
      }
    }
  }
};
</script>

<style scoped>
#container {
  @apply flex content-center justify-center mx-auto h-screen items-center flex-col;
}

#window {
  @apply border-2 border-gray-200 bg-white p-8 rounded shadow-lg;
}

#window h1 {
  @apply my-0 text-center;
}

form {
  @apply mt-4;
}
</style>
