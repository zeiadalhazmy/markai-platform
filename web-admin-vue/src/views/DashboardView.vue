<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>Dashboard</h2>
      <button @click="logout" style="padding:8px 12px">Logout</button>
    </div>

    <ul>
      <li><router-link to="/products">Products (Public)</router-link></li>
      <li><router-link to="/orders-me">My Orders (Auth)</router-link></li>
    </ul>

    <p v-if="sessionEmail">Logged as: {{ sessionEmail }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { supabase } from "../lib/supabase";
import { useRouter } from "vue-router";

const router = useRouter();
const sessionEmail = ref("");

onMounted(async () => {
  const { data } = await supabase.auth.getSession();
  sessionEmail.value = data.session?.user?.email || "";
});

async function logout() {
  await supabase.auth.signOut();
  router.push("/login");
}
</script>
