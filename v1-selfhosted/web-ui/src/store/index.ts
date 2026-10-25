import Vue from 'vue'
import Vuex from 'vuex'
import { Conversation, EventType, MessageEvent, ObjectType, SMSMessage } from '@/interfaces'
import router from '@/router'

Vue.use(Vuex)

export interface StoreState {
    conversations: Conversation[];
}

export default new Vuex.Store({
    state: {
        conversations: []
    } as StoreState,
    getters: {
        conversations: state => {
            return state.conversations
        }
    },
    mutations: {
        clearSession (state) {
            state.conversations = []
        },
        setConversations (state, conversations: Conversation[]) {
            state.conversations = conversations
        },
        messageEvent (state, event: MessageEvent) {
            console.log(event)
            if (event.objectType == ObjectType.CON) {
                if (event.event == EventType.NEW) {
                    const instance = event.instance as Conversation
                    state.conversations.unshift(instance)
                } else if (event.event == EventType.UPD) {
                    const thisInstance = state.conversations.find(x => x.id == event.objectId) as Conversation
                    Object.assign(thisInstance, event.instance)
                } else if (event.event == EventType.DEL) {
                    const conversationIndex = state.conversations.findIndex(x => x.id == event.objectId)
                    state.conversations.splice(conversationIndex, 1)
                    if (event.objectId === router.currentRoute.params.conversationId) {
                        router.push({ name: 'Home' })
                    }
                }
            } else if (event.objectType == ObjectType.MES) {
                if (event.event == EventType.NEW) {
                    const instance = event.instance as SMSMessage
                    const conversationIndex = state.conversations.findIndex(x => x.id == instance.conversationId)
                    const conversation = state.conversations.splice(conversationIndex, 1)[0] as Conversation
                    state.conversations.unshift(conversation)
                    conversation.lastMessage = instance.message
                    if (conversation.messages) {
                        conversation.messages.push(instance)
                    }
                    conversation.unreadCount += 1
                } else if (event.event == EventType.DEL) {
                    const instance = event.instance as SMSMessage
                    const conversation = state.conversations.find(x => x.id == instance.conversationId)
                    if (conversation && conversation.messages) {
                        const messageIndex = conversation.messages.findIndex(x => x.id == instance.id)
                        conversation.messages.splice(messageIndex, 1)
                    }
                }
            }
            Vue.nextTick()
        }
    },
    actions: {
        async loadConversations (context) {
            const messagesResponse = await Vue.axios.get('sms/conversations')
            context.commit('setConversations', messagesResponse.data.conversations)

            const websocketTicket = await Vue.axios.get('sms/ticket')
            const ws = new WebSocket(`${process.env.VUE_APP_WS_ROOT}sms/ws?ticket=${websocketTicket.data.ticket}`)
            ws.onmessage = ev => {
                const event = JSON.parse(ev.data)
                context.commit('messageEvent', event)
            }
        }
    }
})