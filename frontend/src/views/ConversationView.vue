<template>
  <main class="min-h-screen bg-gray-100 px-4 py-8 sm:px-8">
    <div class="mx-auto max-w-3xl">
      <button
        @click="router.push('/messages')"
        class="mb-6 inline-flex cursor-pointer items-center gap-2 border-0 bg-transparent p-0 text-sm font-medium text-gray-600 transition hover:text-black"
      >
        <span aria-hidden="true">←</span>
        Retour aux messages
      </button>

      <p v-if="isLoading" class="text-gray-600">Chargement...</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>

      <section v-else class="flex flex-col rounded-xl border bg-white">
        <div class="border-b p-5">
          <h1 class="text-xl font-bold">{{ conversation.autre_utilisateur_prenom }} {{ conversation.autre_utilisateur_nom }}</h1>
          <router-link :to="`/services/${conversation.id_service}`" class="text-sm text-gray-500 hover:underline">
            {{ conversation.service_titre }}
          </router-link>
        </div>

        <div ref="threadEl" class="max-h-[28rem] space-y-3 overflow-y-auto p-5">
          <div
            v-for="msg in conversation.messages"
            :key="msg.id"
            class="flex"
            :class="msg.id_expediteur === currentUserId ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[75%] rounded-lg px-4 py-2 text-sm"
              :class="msg.id_expediteur === currentUserId ? 'bg-black text-white' : 'bg-gray-100 text-gray-800'"
            >
              <p class="whitespace-pre-line">{{ msg.contenu }}</p>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSend" class="flex gap-3 border-t p-5">
          <textarea
            v-model="newMessage"
            rows="1"
            maxlength="2000"
            placeholder="Écrire un message..."
            class="min-h-12 flex-1 resize-none rounded-lg border p-3"
            @keydown.enter.exact.prevent="handleSend"
          />
          <button
            type="submit"
            :disabled="isSending"
            class="cursor-pointer rounded-lg bg-black px-5 text-sm font-semibold text-white disabled:bg-gray-400"
          >
            Envoyer
          </button>
        </form>
        <p v-if="sendError" class="px-5 pb-4 text-sm text-red-600">{{ sendError }}</p>
      </section>
    </div>
  </main>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getConversation, getUserProfile, openConversationSocket, sendMessage } from '../services/api'

const route = useRoute()
const router = useRouter()
const conversation = ref(null)
const currentUserId = ref('')
const isLoading = ref(true)
const error = ref('')
const newMessage = ref('')
const sendError = ref('')
const isSending = ref(false)
const threadEl = ref(null)
let socket = null

const scrollToBottom = () => {
  nextTick(() => {
    if (threadEl.value) threadEl.value.scrollTop = threadEl.value.scrollHeight
  })
}

const loadConversation = async () => {
  try {
    const [convResponse, profileResponse] = await Promise.all([
      getConversation(route.params.id),
      getUserProfile()
    ])

    if (profileResponse.ok) {
      currentUserId.value = (await profileResponse.json()).id
    }

    if (!convResponse.ok) {
      error.value = 'Impossible de charger cette conversation.'
      return
    }

    conversation.value = await convResponse.json()
    scrollToBottom()

    // Les nouveaux messages arrivent uniquement via le WebSocket, jamais ajoutés manuellement à l'envoi.
    socket = openConversationSocket(route.params.id)
    socket.onmessage = (event) => {
      conversation.value.messages.push(JSON.parse(event.data))
      scrollToBottom()
    }
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const handleSend = async () => {
  if (!newMessage.value.trim()) return

  sendError.value = ''
  isSending.value = true
  try {
    const response = await sendMessage(route.params.id, newMessage.value)
    if (!response.ok) {
      const data = await response.json()
      sendError.value = data.detail || "Impossible d'envoyer le message."
      return
    }
    newMessage.value = ''
  } catch (err) {
    sendError.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isSending.value = false
  }
}

onMounted(loadConversation)
onUnmounted(() => socket?.close())
</script>
