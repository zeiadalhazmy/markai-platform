<template>
  <header class="h-16 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between px-6 shadow-sm z-10">
    <!-- Left: Page Title / Breadcrumbs -->
    <div class="flex items-center">
      <h1 class="text-xl font-bold text-gray-800 dark:text-white">{{ $t('common.dashboard') }}</h1>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-4">
      <!-- Language Switcher -->
      <button 
        @click="toggleLang"
        class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
        title="Switch Language"
      >
        <span class="font-bold text-xs">{{ $i18n.locale.toUpperCase() }}</span>
      </button>

      <!-- Profile Dropdown (simplified) -->
      <div class="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 font-bold border border-primary-200 dark:border-primary-800">
        {{ userInitials }}
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../../stores/auth'

const { locale } = useI18n()
const authStore = useAuthStore()

const userInitials = computed(() => {
    const email = authStore.user?.email || ''
    return email.substring(0, 2).toUpperCase()
})

function toggleLang() {
    const newLang = locale.value === 'ar' ? 'en' : 'ar'
    locale.value = newLang
    document.documentElement.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', newLang)
}
</script>
