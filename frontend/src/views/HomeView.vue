<template>
  <main>
    <!-- Section hero -->
    <section class="relative mx-auto mt-6 max-w-6xl overflow-hidden rounded-xl bg-gray-800 text-white">
      <img
        src="../assets/services-hero.png"
        alt="Des professionnels au travail"
        class="absolute h-full w-full object-cover"
      />
      <div class="absolute h-full w-full bg-black opacity-60"></div>

      <div class="relative mx-auto max-w-6xl px-6 py-28">
        <p class="mb-3 font-semibold">DES SERVICES PRÈS DE CHEZ VOUS</p>
        <h1 class="mb-4 max-w-2xl text-4xl font-bold md:text-5xl">Trouvez la bonne personne pour votre projet</h1>
        <p class="mb-8 max-w-xl text-lg">Consultez les services offerts par des professionnels locaux.</p>

        <div class="flex max-w-xl overflow-hidden rounded-lg bg-white">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="Quel service recherchez-vous?"
            class="min-w-0 w-full px-4 py-3 text-black outline-none focus:outline-none focus:ring-0"
            @keyup.enter="submitSearch"
          />
          <button
            type="button"
            class="cursor-pointer bg-black px-5 py-3 font-semibold text-white"
            @click="submitSearch"
          >
            Rechercher
          </button>
        </div>
      </div>
    </section>

    <!-- Catégories populaires -->
    <section class="mx-auto max-w-6xl p-8">
      <div class="mb-6">
        <p class="text-sm text-gray-500">EXPLORER LES SERVICES</p>
        <h2 class="text-3xl font-bold">Catégories populaires</h2>
      </div>

      <div class="flex flex-wrap gap-4">
        <router-link
          v-for="category in categories"
          :key="category.slug"
          :to="`/services/${category.slug}`"
          class="w-full flex-grow rounded border bg-white p-5 hover:border-gray-500 hover:shadow-md md:w-1/4"
        >
          <component :is="category.icon" class="mb-3 h-8 w-8 text-gray-700" />
          <h3 class="mb-2 text-lg font-bold">{{ category.title }}</h3>
          <p class="text-gray-600">{{ category.description }}</p>
        </router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ComputerDesktopIcon,
  HomeIcon,
  MegaphoneIcon,
  PaintBrushIcon,
  PencilSquareIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const searchKeyword = ref('')

const submitSearch = () => {
  router.push({
    name: 'SearchResults',
    query: { mot_cle: searchKeyword.value.trim() }
  })
}

const categories = [
  { icon: HomeIcon, title: 'Maison', slug: 'maison', description: 'Travaux, réparations et entretien.' },
  { icon: PaintBrushIcon, title: 'Création', slug: 'creation', description: 'Création visuelle et projets créatifs.' },
  { icon: ComputerDesktopIcon, title: 'Informatique', slug: 'informatique', description: 'Aide technique et projets numériques.' },
  { icon: PencilSquareIcon, title: 'Rédaction', slug: 'redaction', description: 'Correction et rédaction de textes.' },
  { icon: MegaphoneIcon, title: 'Marketing', slug: 'marketing', description: 'Publicité et réseaux sociaux.' },
  { icon: UserGroupIcon, title: 'Administration', slug: 'administration', description: 'Organisation et tâches administratives.' }
]
</script>
