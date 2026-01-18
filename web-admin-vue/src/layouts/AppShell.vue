<template>
  <div class="app">
    <aside class="side">
      <div class="brand">
        <div class="logo"></div>
        <div>
          <div class="title">MarkAi</div>
          <div class="muted" style="font-size:12px;">{{ roleLabel }}</div>
        </div>
      </div>

      <nav class="nav">
        <router-link v-for="it in menu" :key="it.to" class="navItem" :to="it.to">
          {{ it.label }}
        </router-link>
      </nav>

      <div class="sideFooter">
        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>
    </aside>

    <main class="main">
      <header class="top">
        <div>
          <div style="font-weight:900;">لوحة التحكم</div>
          <div class="muted" style="font-size:12px;">واجهة Responsive + Usability</div>
        </div>
        <div class="row">
          <span class="badge">{{ roleLabel }}</span>
        </div>
      </header>

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../lib/supabase";
import { getUserRole } from "../lib/profile";
import { ROLE_LABEL } from "../lib/roles";

const router = useRouter();
const role = ref("customer");

const roleLabel = computed(() => ROLE_LABEL[role.value] || "—");

const menu = computed(() => {
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
    return [
      { to: "/admin", label: "الرئيسية" },
    ];
  }
  return [
    { to: "/client", label: "الرئيسية" },
    { to: "/client/products", label: "المنتجات" },
    { to: "/client/orders", label: "طلباتي" },
  ];
});

async function logout() {
  await supabase.auth.signOut();
  router.replace("/auth");
}

onMounted(async () => {
  try {
    const r = await getUserRole();
    if (r) role.value = r;
  } catch {
    // ignore
  }
});
</script>

<style scoped>
.app{
  display:grid;
  grid-template-columns: 280px 1fr;
  min-height:100vh;
}
@media (max-width: 900px){
  .app{ grid-template-columns: 1fr; }
  .side{ position: sticky; top:0; z-index:10; }
}
.side{
  border-right:1px solid var(--border);
  background: rgba(0,0,0,.18);
  padding:14px;
}
.brand{
  display:flex; gap:10px; align-items:center;
  padding:12px;
  border:1px solid var(--border);
  border-radius: var(--radius);
  background: rgba(255,255,255,.04);
}
.logo{
  width:38px; height:38px; border-radius:12px;
  background: linear-gradient(135deg, rgba(200,155,98,.95), rgba(138,90,43,.95));
}
.title{ font-weight:900; }
.nav{ display:flex; flex-direction:column; gap:8px; margin-top:12px; }
.navItem{
  padding:10px 12px;
  border-radius: 12px;
  border:1px solid var(--border);
  background: rgba(255,255,255,.04);
  font-weight:800;
}
.navItem.router-link-active{
  border-color: rgba(200,155,98,.55);
  background: rgba(200,155,98,.10);
}
.sideFooter{ margin-top:12px; }
.main{ padding:14px; }
.top{
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding:12px 14px;
  border:1px solid var(--border);
  border-radius: var(--radius);
  background: rgba(255,255,255,.04);
  margin-bottom:14px;
}
</style>
