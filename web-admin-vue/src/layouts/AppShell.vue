<template>
  <div class="flex h-screen bg-gray-50 dark:bg-slate-950 overflow-hidden font-sans" :dir="$i18n.locale === 'ar' ? 'rtl' : 'ltr'">
    
    <Sidebar :role="currentRole" :menu="menuItems" @logout="handleLogout" />

    <div class="flex-1 flex flex-col overflow-hidden relative">
      <Navbar />

      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-slate-950 p-6 scroll-smooth">
        <div class="max-w-7xl mx-auto">
             <router-view v-slot="{ Component }">
                <transition 
                    enter-active-class="transition ease-out duration-200" 
                    enter-from-class="opacity-0 translate-y-2" 
                    enter-to-class="opacity-100 translate-y-0" 
                    leave-active-class="transition ease-in duration-150" 
                    leave-from-class="opacity-100 translate-y-0" 
                    leave-to-class="opacity-0 translate-y-2"
                >
                    <component :is="Component" />
                </transition>
            </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../components/layout/Sidebar.vue'
import Navbar from '../components/layout/Navbar.vue'

// Basic Role Logic (Ideally should be in a stricter Store or Composable)
// Re-using logic from original file but making it reactive via pinia if possible
// For now, we fetch manually to respect existing structure, but wrapped in clean code.
import { getUserRole } from "../lib/profile"

const router = useRouter()
const authStore = useAuthStore()
const currentRole = ref("customer")

const menu = {
  merchant: [
      { to: "/merchant", label: "الرئيسية" },
      { to: "/merchant/products", label: "المنتجات" },
      { to: "/merchant/orders", label: "الطلبات" },
  ],
  courier: [
      { to: "/courier", label: "الرئيسية" },
      { to: "/courier/tasks", label: "المهام" },
  ],
  admin: [
      { to: "/admin", label: "الرئيسية" },
  ],
  customer: [
    { to: "/client", label: "الرئيسية" },
    { to: "/client/products", label: "المنتجات" },
    { to: "/client/orders", label: "طلباتي" },
  ]
}

const menuItems = computed(() => {
    return menu[currentRole.value] || menu.customer
})

async function handleLogout() {
    await authStore.signOut()
    router.replace('/auth')
}

onMounted(async () => {
    // Sync Pinia
    if (!authStore.session) {
        await authStore.init()
    }
    
    // Fetch Role
    try {
        const r = await getUserRole()
        if (r) currentRole.value = r
    } catch (e) {
        console.error("Failed to fetch role", e)
    }
})
</script>
