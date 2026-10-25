import Vue from 'vue'
import App from './App.vue'
import store from "./store";
import router from './router'
import axios from 'axios';
import { clearAuthTokens, useAuthTokenInterceptor } from 'axios-jwt'
import VueAxios from "vue-axios";

import {library} from "@fortawesome/fontawesome-svg-core";
import {faSignOutAlt, faPaperPlane, faCog, faPlus, faTrash, faSave} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";

library.add(faSignOutAlt, faPaperPlane, faCog, faPlus, faTrash, faSave);
Vue.component("font-awesome-icon", FontAwesomeIcon);

import "./assets/styles/index.css";

Vue.config.productionTip = false

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app')

const api = axios.create({
    baseURL: process.env.VUE_APP_API_ROOT
})

async function requestRefresh (refreshToken: string): Promise<string> {
    try {
        return (
            await axios.post(`${process.env.VUE_APP_API_ROOT}auth/token/refresh`, {
                token: refreshToken
            })
        ).data.accessToken
    } catch (err) {
        clearAuthTokens()
        store.commit('clearProfile')
        await router.push({ name: 'Login' })
        return ''
    }
}

useAuthTokenInterceptor(api, { requestRefresh })

Vue.use(VueAxios, api)