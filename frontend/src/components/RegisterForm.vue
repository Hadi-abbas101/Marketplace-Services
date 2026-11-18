<template>
  <div class="w-full">
    <h2 v-if="activeTab === 'register'" class="mb-2 text-3xl font-semibold">Créer un compte</h2>
    <h2 v-else class="mb-2 text-3xl font-semibold">Se connecter</h2>
    <p v-if="activeTab === 'register'" class="mb-6 text-sm text-stone-600">
      Remplissez le formulaire pour créer votre compte.
    </p>
    <p v-else class="mb-6 text-sm text-stone-600">Entrez vos informations pour continuer.</p>

    <div class="mb-6 flex border-b">
      <button
        type="button"
        class="flex-1 py-3"
        :class="{
          'border-b-2 border-black font-semibold': activeTab === 'register',
          'text-stone-500': activeTab !== 'register'
        }"
        @click="activeTab = 'register'"
      >
        Inscription
      </button>
      <button
        type="button"
        class="flex-1 py-3"
        :class="{
          'border-b-2 border-black font-semibold': activeTab === 'login',
          'text-stone-500': activeTab !== 'login'
        }"
        @click="activeTab = 'login'"
      >
        Connexion
      </button>
    </div>

    <form v-if="activeTab === 'register'" class="space-y-4" @submit.prevent="handleRegister">
      <p v-if="registerError" class="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
        {{ registerError }}
      </p>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="nom" class="mb-1 block text-sm">Nom</label>
          <input id="nom" v-model="form.nom" class="w-full rounded-lg border p-3" type="text" maxlength="50" required />
        </div>
        <div>
          <label for="prenom" class="mb-1 block text-sm">Prénom</label>
          <input id="prenom" v-model="form.prenom" class="w-full rounded-lg border p-3" type="text" maxlength="50" required />
        </div>
      </div>

      <div>
        <label for="courriel" class="mb-1 block text-sm">Adresse courriel</label>
        <input id="courriel" v-model="form.courriel" class="w-full rounded-lg border p-3" type="email" required />
      </div>

      <div>
        <label for="date_naissance" class="mb-1 block text-sm">Date de naissance</label>
        <input id="date_naissance" v-model="form.date_naissance" class="w-full rounded-lg border p-3" type="date" required />
      </div>

      <div>
        <label for="mot_de_passe" class="mb-1 block text-sm">Mot de passe</label>
        <input id="mot_de_passe" v-model="form.mot_de_passe" class="w-full rounded-lg border p-3" type="password" minlength="8" required />
      </div>

      <div>
        <label for="confirmation" class="mb-1 block text-sm">Confirmer le mot de passe</label>
        <input id="confirmation" v-model="form.mot_de_passe_confirmation" class="w-full rounded-lg border p-3" type="password" minlength="8" required />
      </div>

      <button class="w-full rounded-lg bg-black p-3 text-white" type="submit" :disabled="isLoading">
        <span v-if="isLoading">Chargement...</span>
        <span v-else>Créer le compte</span>
      </button>
    </form>

    <form v-else class="space-y-4" @submit.prevent="handleLogin">
      <p v-if="loginMessage" class="rounded-lg border bg-stone-50 p-3 text-sm">
        {{ loginMessage }}
      </p>

      <div>
        <label for="login_courriel" class="mb-1 block text-sm">Adresse courriel</label>
        <input id="login_courriel" v-model="loginForm.courriel" class="w-full rounded-lg border p-3" type="email" required />
      </div>

      <div>
        <label for="login_password" class="mb-1 block text-sm">Mot de passe</label>
        <input id="login_password" v-model="loginForm.mot_de_passe" class="w-full rounded-lg border p-3" type="password" required />
      </div>

      <button class="w-full rounded-lg bg-black p-3 text-white" type="submit" :disabled="isLoading">
        <span v-if="isLoading">Chargement...</span>
        <span v-else>Se connecter</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loginUser, registerUser } from '../services/api'

const route = useRoute()
const router = useRouter()

const activeTab = ref('register')
if (route.query.tab === 'login') {
  activeTab.value = 'login'
} else {
  activeTab.value = 'register'
}
const isLoading = ref(false)
const registerError = ref('')
const loginMessage = ref('')

const form = reactive({
  nom: '',
  prenom: '',
  courriel: '',
  date_naissance: '',
  mot_de_passe: '',
  mot_de_passe_confirmation: ''
})

const loginForm = reactive({
  courriel: '',
  mot_de_passe: ''
})

watch(() => route.query.tab, (tab) => {
  if (tab === 'login') {
    activeTab.value = 'login'
  } else {
    activeTab.value = 'register'
  }
})

const readError = (data, defaultMessage) => {
  if (typeof data.detail === 'string') return data.detail
  return defaultMessage
}

const handleRegister = async () => {
  registerError.value = ''

  if (form.mot_de_passe !== form.mot_de_passe_confirmation) {
    registerError.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  isLoading.value = true

  try {
    const response = await registerUser(form)
    const data = await response.json()

    if (!response.ok) {
      registerError.value = readError(data, "Impossible de créer le compte.")
      return
    }

    loginForm.courriel = form.courriel
    loginMessage.value = 'Compte créé. Vous pouvez maintenant vous connecter.'
    activeTab.value = 'login'
  } catch (error) {
    registerError.value = "Impossible de joindre le serveur."
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const handleLogin = async () => {
  loginMessage.value = ''
  isLoading.value = true

  try {
    const response = await loginUser(loginForm)
    const data = await response.json()

    if (!response.ok) {
      loginMessage.value = readError(data, 'Courriel ou mot de passe incorrect.')
      return
    }

    localStorage.setItem('access_token', data.access_token)
    router.push('/')
  } catch (error) {
    loginMessage.value = "Impossible de joindre le serveur."
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
</script>
