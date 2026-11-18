<template>
  <main class="min-h-screen bg-gray-100 px-4 py-10 sm:px-8">
    <section class="mx-auto max-w-6xl">
      <p class="text-sm font-medium uppercase text-gray-500">Recherche</p>
      <h1 class="mt-1 text-3xl font-bold">Résultats de recherche</h1>
      <p v-if="displayKeyword" class="mt-2 text-gray-600">
        Mot-clé : <span class="font-semibold text-gray-900">{{ displayKeyword }}</span>
      </p>

      <form
        class="mt-6 grid gap-4 rounded-xl border border-gray-300 bg-white p-6 md:grid-cols-2 lg:grid-cols-4"
        @submit.prevent="applyFilters"
      >
        <label class="block text-sm font-medium text-gray-700">
          Catégorie
          <select
            v-model="filterCategory"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
          >
            <option value="">Toutes les catégories</option>
            <option v-for="category in categories" :key="category.id" :value="String(category.id)">
              {{ category.nom }}
            </option>
          </select>
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Budget maximum ($)
          <input
            v-model="filterBudgetMax"
            type="number"
            min="0"
            step="0.01"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Ex. 150"
          />
        </label>

        <div class="flex items-end gap-2 md:col-span-2 lg:col-span-2">
          <button
            type="submit"
            class="cursor-pointer rounded-lg bg-black px-4 py-2 font-semibold text-white hover:bg-gray-800"
          >
            Filtrer
          </button>
          <button
            type="button"
            class="cursor-pointer rounded-lg border border-gray-300 px-4 py-2 font-semibold hover:bg-gray-50"
            @click="resetFilters"
          >
            Réinitialiser
          </button>
        </div>
      </form>

      <p v-if="budgetError" class="mt-4 rounded-lg border border-red-300 bg-red-50 p-3 text-red-700">
        {{ budgetError }}
      </p>

      <p v-if="isLoading" class="mt-8 text-gray-600">Recherche en cours...</p>
      <p v-else-if="error" class="mt-8 text-red-600">{{ error }}</p>
      <p
        v-else-if="services.length === 0"
        class="mt-8 rounded-xl border bg-white p-6 text-gray-600"
      >
        Aucun service trouvé
      </p>

      <div v-else class="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <router-link
          v-for="service in services"
          :key="service.id"
          :to="`/services/${service.id}`"
          class="overflow-hidden rounded-xl border-2 border-gray-400 bg-white transition hover:border-gray-500 hover:shadow-md"
        >
          <img
            v-if="service.photo"
            :src="service.photo"
            alt=""
            class="h-40 w-full object-cover"
          />
          <div v-else class="flex h-40 w-full items-center justify-center bg-gray-200 text-sm text-gray-500">
            Aucune photo
          </div>

          <div class="p-6">
            <h2 class="text-xl font-bold">{{ service.titre }}</h2>
            <div class="mt-2 flex items-center gap-1 text-sm">
              <StarRating :note="service.note_moyenne" />
              <span class="text-gray-500">({{ service.nombre_avis || 0 }})</span>
            </div>
            <p class="mt-2 line-clamp-3 text-sm leading-6 text-gray-600">{{ service.description }}</p>
            <div class="mt-5 flex items-center justify-between text-sm">
              <span class="text-gray-500">{{ service.lieu }}</span>
              <span class="font-semibold">{{ service.budget_estime }} $</span>
            </div>
          </div>
        </router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCategories, searchServices } from '../services/api'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const router = useRouter()
const services = ref([])
const categories = ref([])
const isLoading = ref(true)
const error = ref('')
const budgetError = ref('')
const filterCategory = ref('')
const filterBudgetMax = ref('')

const displayKeyword = computed(() => {
  const value = route.query.mot_cle
  if (value === undefined || value === null) return ''
  return String(value).trim()
})

const syncFiltersFromRoute = () => {
  filterCategory.value = route.query.id_categorie ? String(route.query.id_categorie) : ''
  filterBudgetMax.value = route.query.budget_max ? String(route.query.budget_max) : ''
}

const loadCategories = async () => {
  try {
    const response = await getCategories()
    if (response.ok) {
      categories.value = await response.json()
    }
  } catch (err) {
    console.error(err)
  }
}

const runSearch = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const motCle = route.query.mot_cle ?? ''
    const filters = {}

    if (route.query.id_categorie) {
      filters.id_categorie = route.query.id_categorie
    }
    if (route.query.budget_max !== undefined && route.query.budget_max !== null && route.query.budget_max !== '') {
      filters.budget_max = route.query.budget_max
    }

    const response = await searchServices(String(motCle), filters)

    if (response.status === 422) {
      error.value = 'Le budget maximum doit être supérieur ou égal à zéro.'
      services.value = []
      return
    }

    if (!response.ok) {
      error.value = "Impossible d'effectuer la recherche."
      services.value = []
      return
    }

    services.value = await response.json()
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    services.value = []
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  budgetError.value = ''

  if (filterBudgetMax.value !== '' && Number(filterBudgetMax.value) < 0) {
    budgetError.value = 'Le budget maximum doit être supérieur ou égal à zéro.'
    return
  }

  const query = { mot_cle: route.query.mot_cle ?? '' }

  if (filterCategory.value) {
    query.id_categorie = filterCategory.value
  }
  if (filterBudgetMax.value !== '') {
    query.budget_max = filterBudgetMax.value
  }

  router.push({ name: 'SearchResults', query })
}

const resetFilters = () => {
  budgetError.value = ''
  filterCategory.value = ''
  filterBudgetMax.value = ''
  router.push({ name: 'SearchResults', query: { mot_cle: '' } })
}

onMounted(async () => {
  syncFiltersFromRoute()
  await loadCategories()
  await runSearch()
})

watch(
  () => [route.query.mot_cle, route.query.id_categorie, route.query.budget_max],
  async () => {
    syncFiltersFromRoute()
    await runSearch()
  }
)
</script>
