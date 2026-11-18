<template>
  <header class="border-b bg-white">
    
    <!-- Navigation principale -->
    <nav class="mx-auto flex h-16 max-w-6xl items-center gap-6 px-5">
      <router-link to="/" class="text-xl font-bold">Services+</router-link>

      <div class="ml-auto flex items-center gap-4 text-sm">
        <router-link to="/services/publier" class="flex items-center gap-1 text-gray-600 hover:text-black">
          <Squares2X2Icon class="h-5 w-5" />
          Services
        </router-link>

        <template v-if="isLoggedIn">
          <router-link to="/tableau-de-bord" class="flex items-center gap-1 text-gray-600 hover:text-black">
            <Squares2X2Icon class="h-5 w-5" />
            Tableau de bord
          </router-link>
          <router-link to="/messages" class="flex items-center gap-1 text-gray-600 hover:text-black">
            <span class="relative">
              <ChatBubbleLeftRightIcon class="h-5 w-5" />
              <span
                v-if="unreadCount > 0"
                class="absolute -right-2 -top-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-black px-1 text-[10px] font-semibold leading-none text-white"
              >{{ unreadCount }}</span>
            </span>
            Messages
          </router-link>
          <router-link to="/profile" class="flex items-center gap-1">
            <UserCircleIcon class="h-5 w-5" />
            Profil
          </router-link>
          <button type="button" class="flex items-center gap-1 rounded border px-3 py-2 hover:bg-gray-100" @click="logout">
            <ArrowRightStartOnRectangleIcon class="h-5 w-5" />
            Déconnexion
          </button>
        </template>

        <template v-else>
          <router-link to="/register?tab=login" class="flex items-center gap-1">
            <ArrowRightEndOnRectangleIcon class="h-5 w-5" />
            Connexion
          </router-link>
          <router-link to="/register" class="flex items-center gap-1 rounded bg-black px-4 py-2 text-white">
            <UserPlusIcon class="h-5 w-5" />
            Inscription
          </router-link>
        </template>
      </div>
    </nav>

    <!-- Catégories principales -->
    <div class="border-t">
      <nav class="mx-auto hidden h-12 max-w-6xl items-center justify-between px-5 text-sm text-gray-600 md:flex">
        <router-link
          v-for="category in categories"
          :key="category.slug"
          :to="`/services/${category.slug}`"
          class="flex items-center gap-2 hover:text-black"
        >
          <component :is="category.icon" class="h-5 w-5" />
          {{ category.name }}
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRightEndOnRectangleIcon,
  ArrowRightStartOnRectangleIcon,
  BuildingOffice2Icon,
  ChatBubbleLeftRightIcon,
  ComputerDesktopIcon,
  HomeIcon,
  MegaphoneIcon,
  PaintBrushIcon,
  PencilSquareIcon,
  Squares2X2Icon,
  UserCircleIcon,
  UserPlusIcon
} from '@heroicons/vue/24/outline'
import { getConversations } from '../services/api'

const route = useRoute()
const router = useRouter()

const categories = [
  { name: 'Maison', slug: 'maison', icon: HomeIcon },
  { name: 'Informatique', slug: 'informatique', icon: ComputerDesktopIcon },
  { name: 'Création', slug: 'creation', icon: PaintBrushIcon },
  { name: 'Marketing', slug: 'marketing', icon: MegaphoneIcon },
  { name: 'Rédaction', slug: 'redaction', icon: PencilSquareIcon },
  { name: 'Administration', slug: 'administration', icon: BuildingOffice2Icon }
]

const isLoggedIn = computed(() => {
  return route.path && localStorage.getItem('access_token') !== null
})

const unreadCount = ref(0)
let unreadPollTimer = null

const checkUnreadMessages = async () => {
  if (!isLoggedIn.value) {
    unreadCount.value = 0
    return
  }

  try {
    const response = await getConversations()
    if (!response.ok) return
    const conversations = await response.json()
    const lastSeen = localStorage.getItem('messages_last_seen')
    unreadCount.value = conversations.filter(
      conv => conv.date_dernier_message && (!lastSeen || conv.date_dernier_message > lastSeen)
    ).length
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  checkUnreadMessages()
  unreadPollTimer = setInterval(checkUnreadMessages, 15000)
})

onUnmounted(() => clearInterval(unreadPollTimer))

watch(() => route.path, checkUnreadMessages)

const logout = () => {
  localStorage.removeItem('access_token')
  router.push('/')
}
</script>
