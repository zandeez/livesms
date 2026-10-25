import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import Login from '../views/Login.vue'
import { isLoggedIn } from 'axios-jwt'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '',
        component: () => import('../views/Base.vue'),
        children: [
            {
                path: '/',
                name: 'Home',
                component: () => import('../views/Home.vue')
            },
            {
                path: '/settings',
                name: 'Settings',
                component: () => import('../views/Settings.vue')
            },
            {
                path: '/conversation/:conversationId',
                name: 'Conversation',
                component: () => import('../views/Conversation.vue')
            }
        ]
    }
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

router.beforeEach((to, from, next) => {
    if (!isLoggedIn() && to.name !== 'Login')
        next({ name: 'Login', query: { n: to.fullPath } })
    else if (isLoggedIn() && to.name === 'Login') next({ name: 'Home' })
    else next()
})

export default router
