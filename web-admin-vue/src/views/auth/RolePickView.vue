<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 font-sans">
    <div class="max-w-2xl w-full">
      <div class="text-center mb-10">
        <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white">
          {{ $t('auth.select_role_title') }}
        </h2>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ $t('auth.select_role_subtitle') }}
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Client -->
        <button @click="selectRole('customer')" class="group relative bg-white dark:bg-gray-800 p-6 rounded-2xl border-2 border-transparent hover:border-primary-500 shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-4 group-hover:scale-110 transition-transform">
             <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ $t('roles.customer') }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Browse products and make orders.</p>
        </button>

        <!-- Merchant -->
        <button @click="selectRole('merchant')" class="group relative bg-white dark:bg-gray-800 p-6 rounded-2xl border-2 border-transparent hover:border-emerald-500 shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="h-12 w-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 mb-4 group-hover:scale-110 transition-transform">
             <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ $t('roles.merchant') }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Manage your store and products.</p>
        </button>

        <!-- Courier -->
        <button @click="selectRole('courier')" class="group relative bg-white dark:bg-gray-800 p-6 rounded-2xl border-2 border-transparent hover:border-amber-500 shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div class="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 mb-4 group-hover:scale-110 transition-transform">
             <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ $t('roles.courier') }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Deliver orders and earn money.</p>
        </button>
      </div>
      
       <div v-if="error" class="mt-6 text-center text-red-500 text-sm">
           {{ error }}
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
// import axios from 'axios' // We'll use a service in real implementation

const router = useRouter()
const authStore = useAuthStore()
const error = ref(null)

async function selectRole(role) {
    try {
        const { session } = authStore
        // Simple fetch wrapper since we haven't set up global axios instance fully yet
        const res = await fetch('http://localhost:8000/v1/roles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session?.access_token}`
            },
            body: JSON.stringify({ role })
        })
        
        if (!res.ok) throw new Error('Role assignment failed')
        
        // Refresh profile/role logic in store (if we had it) or just push
        if (role === 'merchant') router.push('/merchant')
        else if (role === 'courier') router.push('/courier')
        else router.push('/client')
    } catch (e) {
        console.error(e)
        error.value = "Failed to assign role. Try again."
    }
}
</script>
