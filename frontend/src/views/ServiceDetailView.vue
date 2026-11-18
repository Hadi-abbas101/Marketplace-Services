<template>
  <main class="min-h-screen bg-gray-100 p-8">
    <div class="mx-auto max-w-6xl">
      <p v-if="isLoading">Chargement...</p>
      <p v-else-if="error" class="text-red-600">{{ error }}</p>

      <div v-else>
        <router-link :to="categoryRoute" class="mb-4 inline-block text-gray-600 hover:underline">
          ← Retour à {{ service.categorie_nom }}
        </router-link>

        <div class="mb-2 flex items-start justify-between gap-4">
          <h1 class="text-3xl font-bold">{{ service.titre }}</h1>
          <div class="flex shrink-0 items-center gap-2">
            <div ref="shareMenuRef" class="relative">
              <button
                type="button"
                class="flex cursor-pointer items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm transition hover:bg-gray-50"
                aria-label="Partager ce service"
                @click="toggleShareMenu"
              >
                <ShareIcon class="h-5 w-5 text-gray-600" />
                Partager
              </button>

              <div
                v-if="showShareMenu"
                class="absolute right-0 z-10 mt-2 w-56 rounded-lg border bg-white p-2 shadow-lg"
              >
                <a
                  :href="shareLinks.facebook"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block rounded-md px-3 py-2 text-sm hover:bg-gray-50"
                  @click="showShareMenu = false"
                >
                  Facebook
                </a>
                <a
                  :href="shareLinks.twitter"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block rounded-md px-3 py-2 text-sm hover:bg-gray-50"
                  @click="showShareMenu = false"
                >
                  X (Twitter)
                </a>
                <a
                  :href="shareLinks.whatsapp"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block rounded-md px-3 py-2 text-sm hover:bg-gray-50"
                  @click="showShareMenu = false"
                >
                  WhatsApp
                </a>
                <a
                  :href="shareLinks.email"
                  class="block rounded-md px-3 py-2 text-sm hover:bg-gray-50"
                  @click="showShareMenu = false"
                >
                  Courriel
                </a>
                <div class="my-1 border-t"></div>
                <button
                  type="button"
                  class="flex w-full cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-gray-50"
                  @click="copyLink"
                >
                  <CheckIcon v-if="linkCopied" class="h-4 w-4 text-green-600" />
                  <ClipboardDocumentIcon v-else class="h-4 w-4 text-gray-500" />
                  {{ linkCopied ? 'Lien copié !' : 'Copier le lien' }}
                </button>
              </div>
            </div>

            <button
              v-if="!isOwner"
              type="button"
              class="flex cursor-pointer items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm transition hover:bg-gray-50"
              :aria-label="isFavori ? 'Retirer des favoris' : 'Ajouter aux favoris'"
              @click="toggleFavori"
            >
              <HeartSolidIcon v-if="isFavori" class="h-5 w-5 text-red-500" />
              <HeartIcon v-else class="h-5 w-5 text-gray-600" />
              {{ isFavori ? 'Retirer des favoris' : 'Ajouter aux favoris' }}
            </button>
          </div>
        </div>
        <p class="mb-6 whitespace-pre-line text-gray-700">{{ service.description }}</p>

        <div class="grid items-start gap-6 lg:grid-cols-3">
          <div :class="isOwner ? 'lg:col-span-3' : 'lg:col-span-2'">
            <section class="rounded-xl border bg-white p-6">
              <img
                v-if="service.photo"
                :src="service.photo"
                alt="Photo du service"
                class="mb-5 h-80 w-full rounded-lg object-cover"
              />
              <div v-else class="mb-5 flex h-80 items-center justify-center rounded-lg bg-gray-200 text-gray-500">
                Aucune photo
              </div>

              <div class="space-y-2 border-t pt-4">
                <p><strong>Catégorie :</strong> {{ service.categorie_nom }}</p>
                <p><strong>Budget :</strong> {{ service.budget_estime }} $</p>
                <p><strong>Lieu :</strong> {{ service.lieu }}</p>
                <p>
                  <strong>Statut :</strong>
                  <span :class="statutBadge(service.statut)">{{ statutLabel(service.statut) }}</span>
                </p>
                <p><strong>Publié par :</strong> {{ service.utilisateur_prenom }} {{ service.utilisateur_nom }}</p>
              </div>
            </section>

            <div v-if="isOwner" class="mt-6 flex flex-wrap gap-3">
              <router-link :to="`/services/${service.id}/edit`" class="rounded-lg border bg-white px-4 py-2">
                Modifier
              </router-link>
              <button
                v-if="service.statut !== 'complet'"
                type="button"
                :disabled="isUpdatingStatut"
                class="cursor-pointer rounded-lg border bg-white px-4 py-2 disabled:opacity-50"
                @click="handleToggleStatut"
              >
                {{ service.statut === 'actif' ? 'Mettre en pause' : 'Réactiver' }}
              </button>
              <button type="button" class="cursor-pointer rounded-lg border border-black bg-white px-4 py-2 text-black" @click="handleDelete">
                Supprimer
              </button>
              <p v-if="statutError" class="w-full text-sm text-red-600">{{ statutError }}</p>
            </div>

            <section class="mt-8 rounded-xl border bg-white p-6">
              <div class="mb-4 flex items-center justify-between">
                <h2 class="text-xl font-bold">Avis</h2>
                <div class="flex items-center gap-2">
                  <StarRating :note="service.note_moyenne" size="h-5 w-5" />
                  <span class="text-sm text-gray-500">
                    {{ service.note_moyenne ?? '—' }} ({{ service.nombre_avis || 0 }} avis)
                  </span>
                </div>
              </div>

              <form v-if="!isOwner && !hasReviewed" @submit.prevent="handleSubmitAvis" class="mb-6 border-b pb-6">
                <label class="mb-2 block font-medium">Votre note</label>
                <div class="mb-3 flex gap-1">
                  <button v-for="n in 5" :key="n" type="button" class="cursor-pointer" @click="avisNote = n">
                    <StarSolidIcon v-if="n <= avisNote" class="h-6 w-6 text-yellow-400" />
                    <StarIcon v-else class="h-6 w-6 text-gray-400" />
                  </button>
                </div>
                <textarea
                  v-model="avisCommentaire"
                  class="min-h-24 w-full rounded-lg border p-3"
                  maxlength="1000"
                  placeholder="Partagez votre expérience avec ce service."
                />
                <p v-if="avisError" class="mt-2 text-sm text-red-600">{{ avisError }}</p>
                <button
                  type="submit"
                  :disabled="isSubmittingAvis"
                  class="mt-3 cursor-pointer rounded-lg bg-black px-4 py-2 text-sm text-white disabled:bg-gray-400"
                >
                  {{ isSubmittingAvis ? 'Envoi en cours...' : 'Publier mon avis' }}
                </button>
              </form>
              <p v-else-if="!isOwner && hasReviewed" class="mb-6 border-b pb-6 text-sm text-gray-500">
                Vous avez déjà laissé un avis sur ce service.
              </p>

              <p v-if="avis.length === 0" class="text-gray-500">Aucun avis pour l'instant.</p>
              <div v-else class="space-y-4">
                <div v-for="item in avis" :key="item.id" class="rounded-lg border p-4">
                  <div class="flex items-center justify-between">
                    <p class="font-semibold">{{ item.auteur_prenom }} {{ item.auteur_nom }}</p>
                    <StarRating :note="item.note" />
                  </div>
                  <p class="mt-2 text-sm text-gray-700">{{ item.commentaire }}</p>
                </div>
              </div>
            </section>

            <section v-if="isOwner" class="mt-8 rounded-xl border bg-white p-6">
              <h2 class="mb-4 text-xl font-bold">Candidatures reçues</h2>
              <p v-if="candidatures.length === 0" class="text-gray-500">Aucune candidature pour l'instant.</p>
              <div v-else class="space-y-4">
                <div v-for="candidature in candidatures" :key="candidature.id" class="rounded-lg border p-4">
                  <p class="font-semibold">{{ candidature.candidat_prenom }} {{ candidature.candidat_nom }} <span class="text-sm text-gray-500">({{ candidature.candidat_courriel }})</span></p>
                  <p class="mt-1 text-sm text-gray-700">{{ candidature.message }}</p>
                  <div class="mt-3 flex items-center gap-3">
                    <span v-if="candidature.statut === 'en_attente'" class="text-sm text-yellow-600 font-medium">En attente</span>
                    <span v-else-if="candidature.statut === 'acceptee'" class="text-sm text-green-600 font-medium">Acceptée</span>
                    <span v-else-if="candidature.statut === 'refusee'" class="text-sm text-red-600 font-medium">Refusée</span>
                    <template v-if="candidature.statut === 'en_attente'">
                      <button type="button" @click="handleStatut(candidature, 'acceptee')" class="cursor-pointer rounded-lg bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700">Accepter</button>
                      <button type="button" @click="handleStatut(candidature, 'refusee')" class="cursor-pointer rounded-lg bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700">Refuser</button>
                    </template>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <aside v-if="!isOwner" class="rounded-xl border bg-white p-6 lg:sticky lg:top-6">
            <p class="text-sm text-gray-500">Budget estimé</p>
            <p class="mb-5 text-2xl font-bold">{{ service.budget_estime }} $</p>
            <h2 class="mb-4 border-t pt-5 text-xl font-bold">Postuler sur ce service</h2>

            <p v-if="postulSuccess" class="mb-3 rounded-lg bg-green-50 p-3 text-sm text-green-700 border border-green-200">
              Votre candidature a été envoyée avec succès !
            </p>
            <p v-if="postulError" class="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
              {{ postulError }}
            </p>
            <p v-if="service.statut !== 'actif' && !postulSuccess" class="mb-3 rounded-lg bg-gray-50 p-3 text-sm text-gray-600 border">
              Ce service n'accepte plus de candidatures pour le moment.
            </p>

            <form v-if="!postulSuccess && service.statut === 'actif'" @submit.prevent="handlePostuler">
              <label for="application-message" class="mb-2 block font-medium">Message</label>
              <textarea
                id="application-message"
                v-model="postulMessage"
                class="min-h-40 w-full rounded-lg border p-3"
                maxlength="1000"
                placeholder="Expliquez pourquoi vous souhaitez réaliser ce service."
              />
              <button type="submit" :disabled="isPostuling" class="mt-3 w-full cursor-pointer rounded-lg bg-black px-4 py-3 text-white disabled:bg-gray-400">
                {{ isPostuling ? 'Envoi en cours...' : 'Postuler' }}
              </button>
            </form>

            <div class="mt-6 border-t pt-5">
              <button
                v-if="!showContactForm"
                type="button"
                @click="showContactForm = true"
                class="w-full cursor-pointer rounded-lg border border-black bg-white px-4 py-3 text-sm font-semibold text-black hover:bg-gray-100"
              >
                Contacter {{ service.utilisateur_prenom }}
              </button>

              <form v-else @submit.prevent="handleContact">
                <label for="contact-message" class="mb-2 block font-medium">Message</label>
                <textarea
                  id="contact-message"
                  v-model="contactMessage"
                  class="min-h-24 w-full rounded-lg border p-3"
                  maxlength="2000"
                  placeholder="Écrivez votre message..."
                />
                <p v-if="contactError" class="mt-2 text-sm text-red-600">{{ contactError }}</p>
                <button
                  type="submit"
                  :disabled="isContacting"
                  class="mt-3 w-full cursor-pointer rounded-lg bg-black px-4 py-3 text-sm text-white disabled:bg-gray-400"
                >
                  {{ isContacting ? 'Envoi en cours...' : 'Envoyer le message' }}
                </button>
              </form>
            </div>
          </aside>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckIcon, ClipboardDocumentIcon, HeartIcon, ShareIcon, StarIcon } from '@heroicons/vue/24/outline'
import { HeartIcon as HeartSolidIcon, StarIcon as StarSolidIcon } from '@heroicons/vue/24/solid'
import { ajouterFavori, creerAvis, deleteService, getAvisService, getCandidatures, getFavoris, getService, getUserProfile, postulerService, retirerFavori, sendServiceMessage, updateCandidatureStatut, updateServiceStatut } from '../services/api'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const router = useRouter()
const service = ref({})
const currentUserId = ref('')
const isLoading = ref(true)
const error = ref('')
const postulMessage = ref('')
const postulSuccess = ref(false)
const postulError = ref('')
const isPostuling = ref(false)
const candidatures = ref([])
const isFavori = ref(false)
const showContactForm = ref(false)
const contactMessage = ref('')
const contactError = ref('')
const isContacting = ref(false)
const avis = ref([])
const avisNote = ref(5)
const avisCommentaire = ref('')
const avisError = ref('')
const isSubmittingAvis = ref(false)
const showShareMenu = ref(false)
const shareMenuRef = ref(null)
const linkCopied = ref(false)
const isUpdatingStatut = ref(false)
const statutError = ref('')

const isOwner = computed(() => currentUserId.value === service.value.id_utilisateur)
const hasReviewed = computed(() => avis.value.some(item => item.id_utilisateur === currentUserId.value))
const categoryRoute = computed(() => {
  const slug = (service.value.categorie_nom || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
  return `/services/${slug}`
})

const shareLinks = computed(() => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(service.value.titre || 'Découvrez ce service')
  return {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
    twitter: `https://twitter.com/intent/tweet?url=${url}&text=${text}`,
    whatsapp: `https://wa.me/?text=${text}%20${url}`,
    email: `mailto:?subject=${text}&body=${url}`
  }
})

const toggleShareMenu = () => {
  showShareMenu.value = !showShareMenu.value
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  } catch (err) {
    console.error(err)
  }
}

const handleClickOutsideShareMenu = (event) => {
  if (shareMenuRef.value && !shareMenuRef.value.contains(event.target)) {
    showShareMenu.value = false
  }
}

const loadService = async () => {
  try {
    const [serviceResponse, profileResponse] = await Promise.all([
      getService(route.params.id),
      getUserProfile()
    ])

    if (!serviceResponse.ok) {
      error.value = 'Impossible de charger le service.'
      return
    }

    service.value = await serviceResponse.json()

    const avisResponse = await getAvisService(route.params.id)
    if (avisResponse.ok) avis.value = await avisResponse.json()

    if (profileResponse.ok) {
      currentUserId.value = (await profileResponse.json()).id
      if (currentUserId.value === service.value.id_utilisateur) {
        const candResponse = await getCandidatures(route.params.id)
        if (candResponse.ok) candidatures.value = await candResponse.json()
      } else {
        const favResponse = await getFavoris()
        if (favResponse.ok) {
          const favoris = await favResponse.json()
          isFavori.value = favoris.some(favori => favori.id_service === service.value.id)
        }
      }
    }
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const statutLabel = (statut) => {
  if (statut === 'en_pause') return 'En pause'
  if (statut === 'complet') return 'Complet'
  return 'Actif'
}

const statutBadge = (statut) => {
  const base = 'ml-2 rounded-full px-3 py-1 text-xs font-medium'
  if (statut === 'en_pause') return `${base} bg-yellow-100 text-yellow-700`
  if (statut === 'complet') return `${base} bg-gray-200 text-gray-700`
  return `${base} bg-green-100 text-green-700`
}

const handleToggleStatut = async () => {
  statutError.value = ''
  isUpdatingStatut.value = true
  const nouveauStatut = service.value.statut === 'actif' ? 'en_pause' : 'actif'
  try {
    const response = await updateServiceStatut(route.params.id, nouveauStatut)
    if (!response.ok) {
      statutError.value = 'Impossible de mettre à jour le statut du service.'
      return
    }
    service.value.statut = (await response.json()).statut
  } catch (err) {
    statutError.value = 'Impossible de joindre le serveur.'
    console.error(err)
  } finally {
    isUpdatingStatut.value = false
  }
}

const handleDelete = async () => {
  try {
    const response = await deleteService(route.params.id)
    if (!response.ok) {
      error.value = 'Impossible de supprimer le service.'
      return
    }
    router.push(categoryRoute.value)
  } catch (err) {
    error.value = 'Impossible de joindre le serveur.'
    console.error(err)
  }
}

const toggleFavori = async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/register?tab=login')
    return
  }
  try {
    if (isFavori.value) {
      const response = await retirerFavori(service.value.id)
      if (response.ok) isFavori.value = false
    } else {
      const response = await ajouterFavori(service.value.id)
      if (response.ok) isFavori.value = true
    }
  } catch (err) {
    error.value = 'Impossible de mettre à jour les favoris.'
    console.error(err)
  }
}

const handleStatut = async (candidature, statut) => {
  try {
    const response = await updateCandidatureStatut(candidature.id, statut)
    if (response.ok) {
      candidature.statut = statut
    }
  } catch (err) {
    error.value = 'Impossible de mettre à jour la candidature.'
  }
}

const handlePostuler = async () => {
  postulError.value = ''
  isPostuling.value = true
  try {
    const response = await postulerService(route.params.id, postulMessage.value)
    if (response.status === 409) {
      postulError.value = 'Vous avez déjà postulé sur ce service.'
      return
    }
    if (!response.ok) {
      const data = await response.json()
      postulError.value = data.detail || 'Une erreur est survenue.'
      return
    }
    postulSuccess.value = true
  } catch (err) {
    postulError.value = 'Impossible de joindre le serveur.'
  } finally {
    isPostuling.value = false
  }
}

const handleContact = async () => {
  contactError.value = ''
  if (!contactMessage.value.trim()) {
    contactError.value = 'Veuillez écrire un message.'
    return
  }

  isContacting.value = true
  try {
    const response = await sendServiceMessage(route.params.id, contactMessage.value)
    if (!response.ok) {
      const data = await response.json()
      contactError.value = data.detail || "Impossible d'envoyer le message."
      return
    }
    const conversation = await response.json()
    router.push(`/messages/${conversation.id}`)
  } catch (err) {
    contactError.value = 'Impossible de joindre le serveur.'
  } finally {
    isContacting.value = false
  }
}

const handleSubmitAvis = async () => {
  avisError.value = ''
  isSubmittingAvis.value = true
  try {
    const response = await creerAvis(route.params.id, {
      note: avisNote.value,
      commentaire: avisCommentaire.value
    })
    if (response.status === 409) {
      avisError.value = 'Vous avez déjà laissé un avis sur ce service.'
      return
    }
    if (!response.ok) {
      const data = await response.json()
      avisError.value = data.detail || 'Une erreur est survenue.'
      return
    }
    const nouvelAvis = await response.json()
    avis.value.unshift(nouvelAvis)
    service.value.nombre_avis = avis.value.length
    service.value.note_moyenne = Math.round(
      (avis.value.reduce((total, item) => total + item.note, 0) / avis.value.length) * 10
    ) / 10
    avisCommentaire.value = ''
    avisNote.value = 5
  } catch (err) {
    avisError.value = 'Impossible de joindre le serveur.'
  } finally {
    isSubmittingAvis.value = false
  }
}

onMounted(() => {
  loadService()
  document.addEventListener('click', handleClickOutsideShareMenu)
})
onUnmounted(() => document.removeEventListener('click', handleClickOutsideShareMenu))
</script>
