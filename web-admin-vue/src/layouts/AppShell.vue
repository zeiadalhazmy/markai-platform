<template>
  <div class="shell">
    <aside class="side card">
      <div class="brand">
        <div class="logo">ماركاي</div>
        <div class="muted">{{ roleLabel }}</div>
      </div>

      <nav class="nav">
        <router-link v-for="i in items" :key="i.to" :to="i.to" class="navItem">
          <span>{{ i.label }}</span>
        </router-link>
      </nav>

      <div class="footer">
        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>
    </aside>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole } from "../lib/profile";
import { ROLE_LABEL } from "../lib/roles";

const router = useRouter();
const role = ref("customer");

onMounted(async () => {
  role.value = (await getUserRole()) || "customer";
});

const roleLabel = computed(() => ROLE_LABEL[role.value] || role.value);

const items = computed(() => {
  if (role.value === "merchant") {
    return [
      { to: "/merchant", label: "الرئيسية" },
      { to: "/merchant/products", label: "المنتجات" },
      { to: "/merchant/orders", label: "الطلبات" },
    ];
  }
  if (role.value === "courier") {
    return [
      { to: "/courier", label: "الرئيسية" },
      { to: "/courier/tasks", label: "المهام" },
    ];
  }
  if (role.value === "admin") {
    return [{ to: "/admin", label: "لوحة الإدارة" }];
  }
  return [
    { to: "/client", label: "الرئيسية" },
    { to: "/client/products", label: "المنتجات" },
    { to: "/client/orders", label: "طلباتي" },
  ];
});

async function logout() {
  await supabase.auth.signOut();
  router.push("/auth");
}
</script>

<style scoped>
.shell{
  display:grid;
  grid-template-columns: 280px 1fr;
  gap:14px;
  padding: 14px;
}
.side{
  padding: 14px;
  height: calc(100vh - 28px);
  position: sticky;
  top: 14px;
  display:flex;
  flex-direction: column;
}
.brand{ padding: 10px 10px 14px; border-bottom: 1px solid var(--border); }
.logo{ font-weight: 900; font-size: 22px; letter-spacing: .5px; }
.nav{ display:flex; flex-direction: column; gap: 8px; padding: 14px 6px; }
.navItem{
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: rgba(255,255,255,.04);
}
.navItem.router-link-active{
  border-color: rgba(77,214,165,.45);
  background: rgba(77,214,165,.12);
}
.footer{ margin-top:auto; padding-top: 12px; border-top: 1px solid var(--border); }

.main{ padding: 8px; }
@media (max-width: 980px){
  .shell{ grid-template-columns: 1fr; }
  .side{ height:auto; position: relative; }
}
</style>
