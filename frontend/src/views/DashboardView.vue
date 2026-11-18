<template>
  <main class="min-h-screen bg-gray-100 p-8">
    <div class="mx-auto max-w-4xl">
      <h1 class="mb-6 text-3xl font-bold">Tableau de bord</h1>

      <p v-if="error" class="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-red-700">
        {{ error }}
      </p>

      <p v-if="isLoading">Chargement...</p>

      <div v-else class="space-y-6">
        <!-- Mes services publiés -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <h2 class="mb-4 text-xl font-bold">Mes services publiés</h2>

          <p v-if="services.length === 0" class="text-gray-500">Rien à afficher pour l'instant.</p>

          <ul v-else class="divide-y divide-gray-200">
            <li v-for="service in services" :key="service.id">
              <router-link
                :to="`/services/${service.id}`"
                class="flex items-center justify-between gap-4 py-4 transition hover:bg-gray-50"
              >
                <div>
                  <p class="font-medium">{{ service.titre }}</p>
                  <p class="text-sm text-gray-500">{{ service.lieu }} · publié le {{ formatDate(service.date_creation) }}</p>
                </div>
                <div class="flex items-center gap-3">
                  <span :class="statutBadge(service.statut)">{{ statutLabel(service.statut) }}</span>
                  <span class="font-semibold">{{ service.budget_estime }} $</span>
                </div>
              </router-link>
            </li>
          </ul>
        </section>

        <!-- Mes candidatures -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <h2 class="mb-4 text-xl font-bold">Mes candidatures</h2>

          <p v-if="candidatures.length === 0" class="text-gray-500">Rien à afficher pour l'instant.</p>

          <ul v-else class="divide-y divide-gray-200">
            <li v-for="candidature in candidatures" :key="candidature.id">
              <router-link
                :to="`/services/${candidature.id_service}`"
                class="flex items-center justify-between gap-4 py-4 transition hover:bg-gray-50"
              >
                <div>
                  <p class="font-medium">{{ candidature.service_titre }}</p>
                  <p class="text-sm text-gray-500">Postulé le {{ formatDate(candidature.date_creation) }}</p>
                </div>
                <span :class="candidatureBadge(candidature.statut)">{{ candidatureLabel(candidature.statut) }}</span>
              </router-link>
            </li>
          </ul>
        </section>

        <!-- Mes commandes -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <h2 class="mb-4 text-xl font-bold">Mes commandes</h2>
          <p class="text-gray-500">Rien à afficher pour l'instant.</p>
        </section>

        <!-- Mes favoris -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <h2 class="mb-4 text-xl font-bold">Mes favoris</h2>

          <p v-if="favoris.length === 0" class="text-gray-500">Rien à afficher pour l'instant.</p>

          <ul v-else class="divide-y divide-gray-200">
            <li v-for="favori in favoris" :key="favori.id" class="flex items-center justify-between gap-4 py-4">
              <router-link :to="`/services/${favori.id_service}`" class="flex-1 transition hover:bg-gray-50">
                <p class="font-medium">{{ favori.titre }}</p>
                <p class="text-sm text-gray-500">{{ favori.categorie_nom }} · {{ favori.lieu }}</p>
              </router-link>
              <div class="flex items-center gap-3">
                <span class="font-semibold">{{ favori.budget_estime }} $</span>
                <button
                  type="button"
                  class="cursor-pointer rounded-lg p-2 text-gray-600 transition hover:bg-gray-100 hover:text-black"
                  aria-label="Retirer des favoris"
                  title="Retirer des favoris"
                  @click="handleRetirerFavori(favori)"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { TrashIcon } from '@heroicons/vue/24/outline'
import { getUserProfile, getMesCandidatures, getFavoris, retirerFavori } from '../services/api'

const router = useRouter()
const isLoading = ref(true)
const error = ref('')
const services = ref([])
const candidatures = ref([])
const favoris = ref([])

const redirectToLogin = () => {
  localStorage.removeItem('access_token')
  router.push('/register?tab=login')
}

const loadDashboard = async () => {
  try {
    const [profileResponse, candidaturesResponse, favorisResponse] = await Promise.all([
      getUserProfile(),
      getMesCandidatures(),
      getFavoris()
    ])

    if ([profileResponse, candidaturesResponse, favorisResponse].some(r => r.status === 401)) {
      redirectToLogin()
      return
    }

    if (!profileResponse.ok || !candidaturesResponse.ok || !favorisResponse.ok) {
      error.value = 'Impossible de charger le tableau de bord.'
      return
    }

    services.value = (await profileResponse.json()).services
    candidatures.value = await candidaturesResponse.json()
    favoris.value = await favorisResponse.json()
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const handleRetirerFavori = async (favori) => {
  error.value = ''
  try {
    const response = await retirerFavori(favori.id_service)
    if (!response.ok) {
      error.value = 'Impossible de retirer le favori.'
      return
    }
    favoris.value = favoris.value.filter(item => item.id !== favori.id)
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  }
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('fr-CA')
}

const statutLabel = (statut) => {
  if (statut === 'en_pause') return 'En pause'
  if (statut === 'complet') return 'Complet'
  return 'Actif'
}

const statutBadge = (statut) => {
  const base = 'rounded-full px-3 py-1 text-xs font-medium'
  if (statut === 'en_pause') return `${base} bg-yellow-100 text-yellow-700`
  if (statut === 'complet') return `${base} bg-gray-200 text-gray-700`
  return `${base} bg-green-100 text-green-700`
}

const candidatureLabel = (statut) => {
  if (statut === 'acceptee') return 'Acceptée'
  if (statut === 'refusee') return 'Refusée'
  return 'En attente'
}

const candidatureBadge = (statut) => {
  const base = 'rounded-full px-3 py-1 text-xs font-medium'
  if (statut === 'acceptee') return `${base} bg-green-100 text-green-700`
  if (statut === 'refusee') return `${base} bg-red-100 text-red-700`
  return `${base} bg-yellow-100 text-yellow-700`
}

onMounted(loadDashboard)
</script>
