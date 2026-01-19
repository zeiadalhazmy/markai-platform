<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 font-sans">
    <div class="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-10 rounded-2xl shadow-xl transition-all duration-300 hover:shadow-2xl border border-gray-100 dark:border-gray-700">
      
      <!-- Header -->
      <div class="text-center">
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {{ $t('common.welcome') }}
        </h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ step === 1 ? $t('auth.enter_email') : $t('auth.enter_otp') }}
        </p>
      </div>

      <!-- Form -->
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          
          <!-- Email Input -->
          <div v-if="step === 1">
            <label for="email-address" class="sr-only">{{ $t('common.email') }}</label>
            <input 
              id="email-address" 
              name="email" 
              type="email" 
              autocomplete="email" 
              required 
              v-model="email"
              :class="{'text-right': $i18n.locale === 'ar', 'text-left': $i18n.locale === 'en'}"
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-colors"
              :placeholder="$t('common.email')"
            />
          </div>

          <!-- OTP Input -->
          <div v-else>
            <label for="otp" class="sr-only">OTP</label>
             <input 
              id="otp" 
              name="otp" 
              type="text" 
              required 
              v-model="otp"
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white tracking-widest text-center text-lg font-mono"
              placeholder="123456"
              maxlength="6"
            />
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="authStore.error" class="text-red-500 text-sm text-center bg-red-50 p-2 rounded-md border border-red-100">
           {{ authStore.error }}
        </div>

        <!-- Actions -->
        <div>
          <button 
            type="submit" 
            :disabled="authStore.loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-200 transform hover:-translate-y-0.5 shadow-lg shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
           <span v-if="authStore.loading">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ $t('common.loading') }}
           </span>
            <span v-else>
               {{ step === 1 ? $t('common.send_otp') : $t('common.verify') }}
            </span>
          </button>
        </div>
        
        <div v-if="step === 2" class="text-center mt-4">
             <button type="button" @click="step = 1" class="text-sm text-primary-600 hover:text-primary-500 font-medium">
                Resend / Change Email
             </button>
        </div>
      </form>

      <!-- Language Switch -->
      <div class="mt-6 flex justify-center space-x-4">
          <button @click="switchLang('en')" :class="{'font-bold text-primary-600': $i18n.locale === 'en'}" class="text-gray-500 hover:text-gray-700 text-sm">English</button>
          <span class="text-gray-300">|</span>
          <button @click="switchLang('ar')" :class="{'font-bold text-primary-600': $i18n.locale === 'ar'}" class="text-gray-500 hover:text-gray-700 text-sm">العربية</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const { locale } = useI18n()

const step = ref(1)
const email = ref('')
const otp = ref('')

async function handleSubmit() {
    if (step.value === 1) {
        if (!email.value) return
        await authStore.signInWithOtp(email.value)
        if (!authStore.error) {
            step.value = 2
        }
    } else {
        if (!otp.value) return
        const success = await authStore.verifyOtp(email.value, otp.value)
        if (success) {
            router.push('/')
        }
    }
}

function switchLang(lang) {
    locale.value = lang
    document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', lang)
}
</script>
