<template>
  <main class="min-h-screen bg-gray-100 px-4 py-10 sm:px-8">
    <section class="mx-auto max-w-6xl">
      <p class="text-sm font-medium uppercase text-gray-500">Services</p>
      <h1 class="mt-1 text-3xl font-bold">{{ categoryName }}</h1>

      <p v-if="isLoading" class="mt-8 text-gray-600">Chargement des services...</p>
      <p v-else-if="error" class="mt-8 text-red-600">{{ error }}</p>
      <p v-else-if="services.length === 0" class="mt-8 rounded-xl border bg-white p-6 text-gray-600">
        Aucun service disponible dans cette catégorie.
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
import { useRoute } from 'vue-router'
import { getCategories, getServices } from '../services/api'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const allServices = ref([])
const categories = ref([])
const isLoading = ref(true)
const error = ref('')

const normalize = (value) => value
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()

const currentCategory = computed(() =>
  categories.value.find(category => normalize(category.nom) === route.params.category)
)

const categoryName = computed(() => currentCategory.value?.nom || route.params.category)
const services = computed(() => {
  if (!currentCategory.value) return []
  return allServices.value.filter(service => service.id_categorie === currentCategory.value.id)
})

const loadData = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const [categoriesResponse, servicesResponse] = await Promise.all([
      getCategories(),
      getServices()
    ])

    if (!categoriesResponse.ok || !servicesResponse.ok) {
      error.value = 'Impossible de charger les services.'
      return
    }

    categories.value = await categoriesResponse.json()
    allServices.value = await servicesResponse.json()
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)
watch(() => route.params.category, loadData)
</script>
