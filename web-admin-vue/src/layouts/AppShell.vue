<template>
  <div class="section">
    <div class="container">
      <div class="row-between">
        <div>
          <div class="row" style="gap:10px;">
            <div class="badge">
              <span style="width:10px;height:10px;border-radius:99px;background:var(--primary);display:inline-block;"></span>
              MarkAi
            </div>
            <div class="badge" v-if="role">{{ roleLabel }}</div>
          </div>
          <div class="muted" style="margin-top:6px" v-if="email">{{ email }}</div>
        </div>

        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>

      <div class="divider"></div>

      <div class="grid2" style="grid-template-columns: 260px 1fr;">
        <!-- Side menu -->
        <aside class="card p16" style="height: fit-content;">
          <div class="h2">القائمة</div>

          <div v-if="loading">
            <div class="skeleton" style="height:14px;margin:10px 0;"></div>
            <div class="skeleton" style="height:14px;margin:10px 0;width:80%"></div>
            <div class="skeleton" style="height:14px;margin:10px 0;width:60%"></div>
          </div>

          <ul v-else style="list-style:none;padding:0;margin:10px 0;display:flex;flex-direction:column;gap:10px;">
            <li v-for="item in menu" :key="item.to">
              <router-link
                :to="item.to"
                class="btn btn-ghost"
                style="display:block;text-align:start;width:100%;"
              >
                {{ item.label }}
              </router-link>
            </li>
          </ul>
        </aside>

        <!-- Page -->
        <main style="min-width:0;">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole } from "../lib/profile";
import { ROLE_LABEL } from "../lib/roles";

const router = useRouter();
const role = ref(null);
const email = ref("");
const loading = ref(true);

const roleLabel = computed(() => ROLE_LABEL[role.value] || role.value);

const menu = computed(() => {
  switch (role.value) {
    case "merchant":
      return [
        { label: "الرئيسية", to: "/merchant" },
        { label: "منتجاتي", to: "/merchant/products" },
        { label: "طلبات الزبائن", to: "/merchant/orders" },
      ];
    case "courier":
      return [
        { label: "الرئيسية", to: "/courier" },
        { label: "المهام", to: "/courier/tasks" },
      ];
    case "admin":
      return [
        { label: "الرئيسية", to: "/admin" },
        { label: "إدارة المستخدمين", to: "/admin/users" },
        { label: "الطلبات", to: "/admin/orders" },
        { label: "المنتجات", to: "/admin/products" },
      ];
    default:
      return [
        { label: "الرئيسية", to: "/client" },
        { label: "المنتجات", to: "/client/products" },
        { label: "طلباتي", to: "/client/orders" },
      ];
  }
});

onMounted(async () => {
  const { data } = await supabase.auth.getSession();
  email.value = data.session?.user?.email || data.session?.user?.phone || "";
  role.value = await getUserRole();
  loading.value = false;
});

async function logout() {
  await supabase.auth.signOut();
  router.push("/auth");
}
</script>

<style scoped>
@media (max-width: 900px){
  .grid2{ grid-template-columns: 1fr !important; }
}
</style>
