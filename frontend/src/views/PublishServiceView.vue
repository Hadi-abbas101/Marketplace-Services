<template>
  <main class="min-h-screen bg-gray-100 px-4 py-8 sm:px-8 sm:py-12">
    <div class="mx-auto w-full max-w-3xl">
      <button
        @click="router.push(returnRoute)"
        class="mb-6 inline-flex cursor-pointer items-center gap-2 border-0 bg-transparent p-0 text-sm font-medium text-gray-600 transition hover:text-black"
      >
        <span aria-hidden="true">←</span>
        {{ isEditMode ? 'Retour au service' : 'Retour à l’accueil' }}
      </button>

      <section class="rounded-xl border border-gray-200 bg-white p-6 sm:p-10">
        <div class="border-b border-gray-200 pb-6">
          <h1 class="mb-2 text-3xl font-bold text-black">
            {{ isEditMode ? 'Modifier le service' : 'Publier un service' }}
          </h1>
          <p class="max-w-xl text-sm leading-6 text-gray-600">
            {{ isEditMode
              ? 'Modifiez les informations de votre service.'
              : 'Décrivez votre service pour que les autres utilisateurs puissent le découvrir.' }}
          </p>
        </div>

        <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div v-if="apiError" class="bg-red-50 text-red-600 p-4 rounded-xl text-sm border border-red-100 font-medium">
          {{ apiError }}
        </div>

        <!-- Catégorie -->
        <div>
          <label for="id_categorie" class="mb-1 block text-sm font-medium text-gray-700">Catégorie</label>
          <select 
            id="id_categorie" 
            v-model="form.id_categorie" 
            @change="validateField('id_categorie')"
            class="w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
            :class="{'border-red-500 focus:ring-red-500': errors.id_categorie}"
          >
            <option value="" disabled>-- Choisir une catégorie --</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.nom }}
            </option>
          </select>
          <span v-if="errors.id_categorie" class="text-xs text-red-500 mt-1 block">{{ errors.id_categorie }}</span>
        </div>

        <!-- Titre -->
        <div>
          <label for="titre" class="mb-1 block text-sm font-medium text-gray-700">Titre du service</label>
          <input 
            type="text" 
            id="titre" 
            v-model="form.titre" 
            @input="validateField('titre')"
            placeholder="Ex : Réparation de vélo à domicile" 
            class="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
            :class="{'border-red-500 focus:ring-red-500': errors.titre}"
          />
          <span v-if="errors.titre" class="text-xs text-red-500 mt-1 block">{{ errors.titre }}</span>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="mb-1 block text-sm font-medium text-gray-700">Description</label>
          <textarea 
            id="description" 
            v-model="form.description" 
            @input="validateField('description')"
            rows="4"
            placeholder="Décrivez votre offre..." 
            class="w-full resize-y rounded-lg border border-gray-300 px-4 py-3 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
            :class="{'border-red-500 focus:ring-red-500': errors.description}"
          ></textarea>
          <span v-if="errors.description" class="text-xs text-red-500 mt-1 block">{{ errors.description }}</span>
        </div>

        <!-- Photo -->
        <div>
          <label for="photo" class="mb-1 block text-sm font-medium text-gray-700">Photo (optionnelle)</label>
          <input
            type="file"
            id="photo"
            accept="image/*"
            @change="handlePhotoChange"
            class="w-full cursor-pointer rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
          />
          <span v-if="errors.photo" class="text-xs text-red-500 mt-1 block">{{ errors.photo }}</span>
          <img v-if="form.photo" :src="form.photo" alt="Aperçu de la photo" class="mt-3 h-40 w-auto rounded-lg border border-gray-200 object-cover" />
        </div>

        <!-- Budget & Lieu -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Budget -->
          <div>
            <label for="budget_estime" class="mb-1 block text-sm font-medium text-gray-700">Budget estimé</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-4 font-medium text-gray-500">$</span>
              <input 
                type="number" 
                step="0.01"
                id="budget_estime" 
                v-model.number="form.budget_estime" 
                @input="validateField('budget_estime')"
                placeholder="0.00" 
                class="w-full rounded-lg border border-gray-300 py-3 pl-8 pr-4 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
                :class="{'border-red-500 focus:ring-red-500': errors.budget_estime}"
              />
            </div>
            <span v-if="errors.budget_estime" class="text-xs text-red-500 mt-1 block">{{ errors.budget_estime }}</span>
          </div>

          <!-- Lieu -->
          <div>
            <label for="lieu" class="mb-1 block text-sm font-medium text-gray-700">Lieu</label>
            <input 
              type="text" 
              id="lieu" 
              v-model="form.lieu" 
              @input="validateField('lieu')"
              placeholder="Ex : Montréal, QC" 
              class="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-800 transition focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
              :class="{'border-red-500 focus:ring-red-500': errors.lieu}"
            />
            <span v-if="errors.lieu" class="text-xs text-red-500 mt-1 block">{{ errors.lieu }}</span>
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="flex w-full cursor-pointer items-center justify-center space-x-2 rounded-lg border-0 bg-black px-4 py-3 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          <span v-if="isSubmitting" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <span>{{ isEditMode ? 'Enregistrer les modifications' : 'Publier le service' }}</span>
        </button>
        </form>
      </section>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createService, getCategories, getService, updateService } from '../services/api'

const route = useRoute()
const router = useRouter()
const isEditMode = computed(() => route.name === 'EditService')
const returnRoute = computed(() => {
  if (route.query.from === 'profile') return '/profile'
  return isEditMode.value ? `/services/${route.params.id}` : '/'
})
const categories = ref([])
const isSubmitting = ref(false)
const apiError = ref(null)

const form = reactive({
  id_categorie: '',
  titre: '',
  description: '',
  photo: '',
  budget_estime: 0,
  lieu: ''
})

const errors = reactive({
  id_categorie: null,
  titre: null,
  description: null,
  photo: null,
  budget_estime: null,
  lieu: null
})

const MAX_PHOTO_SIZE = 5 * 1024 * 1024

const handlePhotoChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > MAX_PHOTO_SIZE) {
    errors.photo = "L'image ne doit pas dépasser 5 Mo."
    event.target.value = ''
    return
  }

  errors.photo = null
  const reader = new FileReader()
  reader.onload = () => {
    form.photo = reader.result
  }
  reader.readAsDataURL(file)
}

const fetchCategories = async () => {
  try {
    const response = await getCategories()
    if (response.ok) {
      categories.value = await response.json()
    } else {
      apiError.value = "Impossible de récupérer les catégories de services."
    }
  } catch (err) {
    apiError.value = "Erreur de connexion au serveur lors du chargement des catégories."
    console.error(err)
  }
}

const loadService = async () => {
  try {
    const response = await getService(route.params.id)
    if (!response.ok) {
      apiError.value = 'Impossible de charger le service.'
      return
    }

    const service = await response.json()
    form.id_categorie = service.id_categorie
    form.titre = service.titre
    form.description = service.description
    form.photo = service.photo || ''
    form.budget_estime = service.budget_estime
    form.lieu = service.lieu
  } catch (err) {
    apiError.value = 'Impossible de joindre le serveur.'
    console.error(err)
  }
}

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/register')
    return
  }
  await fetchCategories()
  if (isEditMode.value) await loadService()
})

const validateField = (field) => {
  if (field === 'id_categorie') {
    if (!form.id_categorie) {
      errors.id_categorie = 'Veuillez sélectionner une catégorie.'
    } else {
      errors.id_categorie = null
    }
  }

  if (field === 'titre') {
    if (!form.titre.trim()) {
      errors.titre = 'Le titre du service est obligatoire.'
    } else if (form.titre.length > 100) {
      errors.titre = 'Le titre ne doit pas dépasser 100 caractères.'
    } else {
      errors.titre = null
    }
  }

  if (field === 'description') {
    if (!form.description.trim()) {
      errors.description = 'La description est obligatoire.'
    } else if (form.description.length > 1000) {
      errors.description = 'La description ne doit pas dépasser 1000 caractères.'
    } else {
      errors.description = null
    }
  }

  if (field === 'budget_estime') {
    if (form.budget_estime === '' || form.budget_estime === null) {
      errors.budget_estime = 'Le budget est obligatoire (0 par défaut).'
    } else if (form.budget_estime < 0) {
      errors.budget_estime = 'Le budget ne peut pas être négatif.'
    } else {
      errors.budget_estime = null
    }
  }

  if (field === 'lieu') {
    if (!form.lieu.trim()) {
      errors.lieu = 'Le lieu est obligatoire.'
    } else if (form.lieu.length > 100) {
      errors.lieu = 'Le lieu ne doit pas dépasser 100 caractères.'
    } else {
      errors.lieu = null
    }
  }
}

const validateAll = () => {
  validateField('id_categorie')
  validateField('titre')
  validateField('description')
  validateField('budget_estime')
  validateField('lieu')

  return !errors.id_categorie &&
    !errors.titre &&
    !errors.description &&
    !errors.budget_estime &&
    !errors.lieu
}

const handleSubmit = async () => {
  apiError.value = null
  if (!validateAll()) return

  isSubmitting.value = true

  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/register')
    return
  }

  try {
    const payload = {
      id_categorie: parseInt(form.id_categorie),
      titre: form.titre,
      description: form.description,
      photo: form.photo || null,
      budget_estime: parseFloat(form.budget_estime || 0),
      lieu: form.lieu
    }

    const response = isEditMode.value
      ? await updateService(route.params.id, payload)
      : await createService(payload)

    const data = await response.json()

    if (!response.ok) {
      if (response.status === 400 && data.detail === "Contenu refusé") {
        apiError.value = "Contenu refusé : le titre ou la description contient des propos inacceptables."
      } else if (data.detail) {
        if (Array.isArray(data.detail)) {
          apiError.value = data.detail.map(err => err.msg).join(', ')
        } else {
          apiError.value = data.detail
        }
      } else {
        apiError.value = isEditMode.value
          ? "Une erreur est survenue lors de la modification."
          : "Une erreur est survenue lors de la publication."
      }
      return
    }

    if (isEditMode.value && route.query.from === 'profile') {
      router.push('/profile')
    } else {
      router.push(`/services/${isEditMode.value ? route.params.id : data.id}`)
    }
  } catch (err) {
    apiError.value = "Impossible de se connecter au serveur backend. Vérifiez que l'API est démarrée."
    console.error(err)
  } finally {
    isSubmitting.value = false
  }
}
</script>
