<template>
  <aside class="hidden md:flex flex-col w-64 bg-slate-900 border-r border-slate-800 transition-all duration-300">
    <!-- Brand -->
    <div class="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 shadow-lg shadow-primary-500/20"></div>
      <span class="text-lg font-bold text-white tracking-wide">MarkAi</span>
    </div>

    <!-- User Info (Mini) -->
    <div class="px-6 py-4 border-b border-slate-800/50">
        <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">Role</p>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-900/30 text-primary-400 ring-1 ring-inset ring-primary-500/20">
            {{ roleLabel }}
        </span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      <router-link 
        v-for="item in menu" 
        :key="item.to" 
        :to="item.to"
        class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
        :class="[
          isActive(item.to) 
            ? 'bg-primary-600 text-white shadow-md shadow-primary-900/20' 
            : 'text-slate-400 hover:bg-slate-800 hover:text-white'
        ]"
      >
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="p-4 border-t border-slate-800">
      <button @click="$emit('logout')" class="w-full flex items-center justify-center px-4 py-2 border border-slate-700 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
        {{ $t('common.logout') }}
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps(['role', 'menu'])
const route = useRoute()

// Map roles to nice labels if needed, or pass from parent
const roleLabel = computed(() => {
    return props.role?.charAt(0).toUpperCase() + props.role?.slice(1) || 'Guest'
})

function isActive(path) {
    return route.path.startsWith(path)
}
</script>
