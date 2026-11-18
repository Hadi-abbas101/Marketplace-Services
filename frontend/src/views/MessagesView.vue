<template>
  <main class="min-h-screen bg-gray-100 px-4 py-8 sm:px-8">
    <div class="mx-auto max-w-3xl">
      <h1 class="mb-6 text-3xl font-bold">Messages</h1>

      <p v-if="isLoading" class="text-gray-600">Chargement...</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>
      <p v-else-if="conversations.length === 0" class="rounded-xl border bg-white p-6 text-gray-600">
        Vous n'avez aucune conversation pour l'instant.
      </p>

      <div v-else class="space-y-3">
        <router-link
          v-for="conv in conversations"
          :key="conv.id"
          :to="`/messages/${conv.id}`"
          class="block rounded-xl border bg-white p-5 transition hover:border-gray-400 hover:shadow-sm"
        >
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-bold">{{ conv.autre_utilisateur_prenom }} {{ conv.autre_utilisateur_nom }}</h2>
            <span class="shrink-0 text-xs text-gray-500">{{ formatDate(conv.date_dernier_message) }}</span>
          </div>
          <p class="text-sm text-gray-500">{{ conv.service_titre }}</p>
          <p class="mt-2 line-clamp-1 text-sm text-gray-700">{{ conv.dernier_message }}</p>
        </router-link>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getConversations } from '../services/api'

const conversations = ref([])
const isLoading = ref(true)
const error = ref('')

const formatDate = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleDateString('fr-CA', { day: 'numeric', month: 'short' })
}

onMounted(async () => {
  try {
    const response = await getConversations()
    if (!response.ok) {
      error.value = 'Impossible de charger vos messages.'
      return
    }
    conversations.value = await response.json()

    const lastMessageDate = conversations.value
      .map(conv => conv.date_dernier_message)
      .filter(Boolean)
      .sort()
      .at(-1)
    if (lastMessageDate) {
      localStorage.setItem('messages_last_seen', lastMessageDate)
    }
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
})
</script>
