<template>
  <main class="min-h-screen bg-gray-100 p-8">
    <!-- Page profil -->
    <div class="mx-auto max-w-4xl">
      <h1 class="mb-6 text-3xl font-bold">Mon profil</h1>

      <!-- Erreur -->
      <p v-if="error" class="mb-4 border border-red-500 bg-red-100 p-3 text-red-700">
        {{ error }}
      </p>

      <!-- Chargement -->
      <p v-if="isLoading">Chargement...</p>

      <div v-else class="space-y-6">
        <!-- Informations personnelles -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-bold">Informations personnelles</h2>
            <button
              v-if="!isEditing"
              type="button"
              class="cursor-pointer rounded-lg border border-gray-300 bg-transparent px-3 py-1.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-100"
              @click="startEditing"
            >
              Modifier
            </button>
          </div>

          <p v-if="updateError" class="mb-4 border border-red-500 bg-red-100 p-3 text-red-700">
            {{ updateError }}
          </p>
          <p v-if="updateSuccess" class="mb-4 border border-green-500 bg-green-100 p-3 text-green-700">
            Profil mis à jour avec succès.
          </p>

          <form v-if="isEditing" class="space-y-4" @submit.prevent="handleSave">
            <div>
              <label class="mb-1 block text-sm font-semibold" for="prenom">Prénom</label>
              <input id="prenom" v-model="editForm.prenom" type="text" required class="w-full rounded-lg border border-gray-300 p-2" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold" for="nom">Nom</label>
              <input id="nom" v-model="editForm.nom" type="text" required class="w-full rounded-lg border border-gray-300 p-2" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold" for="courriel">Courriel</label>
              <input id="courriel" v-model="editForm.courriel" type="email" required class="w-full rounded-lg border border-gray-300 p-2" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-semibold" for="date_naissance">Date de naissance</label>
              <input id="date_naissance" v-model="editForm.date_naissance" type="date" required class="w-full rounded-lg border border-gray-300 p-2" />
            </div>
            <div class="flex gap-2">
              <button
                type="submit"
                :disabled="isSaving"
                class="cursor-pointer rounded-lg bg-black px-4 py-2 font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {{ isSaving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
              <button
                type="button"
                :disabled="isSaving"
                class="cursor-pointer rounded-lg border border-gray-300 bg-transparent px-4 py-2 font-semibold text-gray-700 transition hover:bg-gray-100"
                @click="cancelEditing"
              >
                Annuler
              </button>
            </div>
          </form>

          <template v-else>
            <p><strong>Nom :</strong> {{ user.prenom }} {{ user.nom }}</p>
            <p><strong>Courriel :</strong> {{ user.courriel }}</p>
            <p><strong>Date de naissance :</strong> {{ formatDate(user.date_naissance) }}</p>
            <p><strong>Statut :</strong> {{ getStatus() }}</p>
          </template>
        </section>

        <!-- Services de l'utilisateur -->
        <section class="rounded-xl border border-gray-300 bg-white p-6">
          <h2 class="mb-4 text-xl font-bold">Mes services</h2>

          <p v-if="user.services.length === 0">Vous n'avez pas encore publié de service.</p>

          <div v-else class="overflow-x-auto">
            <table class="w-full border-collapse text-left">
              <thead>
                <tr class="border-b border-gray-300 text-sm text-gray-600">
                  <th class="px-3 py-3 font-semibold">Service</th>
                  <th class="px-3 py-3 font-semibold">Lieu</th>
                  <th class="px-3 py-3 text-right font-semibold">Coût</th>
                  <th class="px-3 py-3 text-right font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="service in user.services"
                  :key="service.id"
                  class="border-b border-gray-300 last:border-b-0"
                >
                  <td class="px-3 py-4 font-medium">{{ service.titre }}</td>
                  <td class="px-3 py-4 text-gray-600">{{ service.lieu }}</td>
                  <td class="px-3 py-4 text-right">{{ service.budget_estime }} $</td>
                  <td class="px-3 py-4">
                    <div class="flex justify-end gap-2">
                      <router-link
                        :to="`/services/${service.id}/edit?from=profile`"
                        class="rounded-lg p-2 text-gray-600 transition hover:bg-gray-100 hover:text-black"
                        aria-label="Modifier le service"
                        title="Modifier"
                      >
                        <PencilSquareIcon class="h-5 w-5" />
                      </router-link>
                      <button
                        type="button"
                        class="cursor-pointer rounded-lg border-0 bg-transparent p-2 text-gray-600 transition hover:bg-gray-100 hover:text-black"
                        aria-label="Supprimer le service"
                        title="Supprimer"
                        @click="handleDelete(service)"
                      >
                        <TrashIcon class="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { deleteService, getUserProfile, updateUserProfile } from '../services/api'

const router = useRouter()
const isLoading = ref(true)
const error = ref('')
const user = ref({ services: [] })

const isEditing = ref(false)
const isSaving = ref(false)
const updateError = ref('')
const updateSuccess = ref(false)
const editForm = ref({ nom: '', prenom: '', courriel: '', date_naissance: '' })

const loadProfile = async () => {
  try {
    const response = await getUserProfile()

    if (response.status === 401) {
      localStorage.removeItem('access_token')
      router.push('/register?tab=login')
      return
    }

    if (!response.ok) {
      error.value = 'Impossible de charger le profil.'
      return
    }

    user.value = await response.json()
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('fr-CA')
}

const getStatus = () => {
  if (user.value.statut === 1) {
    return 'Actif'
  } else {
    return 'Inactif'
  }
}

const startEditing = () => {
  editForm.value = {
    nom: user.value.nom,
    prenom: user.value.prenom,
    courriel: user.value.courriel,
    date_naissance: user.value.date_naissance
  }
  updateError.value = ''
  updateSuccess.value = false
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  updateError.value = ''
}

const handleSave = async () => {
  isSaving.value = true
  updateError.value = ''
  updateSuccess.value = false

  try {
    const response = await updateUserProfile(editForm.value)

    if (response.status === 401) {
      localStorage.removeItem('access_token')
      router.push('/register?tab=login')
      return
    }

    if (response.status === 409) {
      updateError.value = 'Cette adresse courriel est déjà associée à un compte existant.'
      return
    }

    if (!response.ok) {
      updateError.value = 'Impossible de mettre à jour le profil.'
      return
    }

    user.value = await response.json()
    isEditing.value = false
    updateSuccess.value = true
  } catch (err) {
    updateError.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

const handleDelete = async (service) => {
  error.value = ''
  try {
    const response = await deleteService(service.id)
    if (!response.ok) {
      error.value = 'Impossible de supprimer le service.'
      return
    }

    user.value.services = user.value.services.filter(item => item.id !== service.id)
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  }
}

onMounted(loadProfile)
</script>
