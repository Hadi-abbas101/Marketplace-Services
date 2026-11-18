<template>
  <span v-if="note === null || note === undefined" class="text-xs text-gray-500">Aucun avis</span>
  <span v-else class="flex items-center gap-0.5">
    <StarSolidIcon
      v-for="n in 5"
      :key="n"
      :class="[size, n <= Math.round(note) ? 'text-yellow-400' : 'text-gray-300']"
    />
  </span>
</template>

<script setup>
import { StarIcon as StarSolidIcon } from '@heroicons/vue/24/solid'

defineProps({
  note: {
    type: Number,
    default: null
  },
  size: {
    type: String,
    default: 'h-4 w-4'
  }
})
</script>
