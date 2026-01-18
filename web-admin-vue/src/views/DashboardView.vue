<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>Dashboard</h2>
      <button @click="logout" style="padding:8px 12px">Logout</button>
    </div>

    <ul>
      <li><router-link to="/products">Products (Public)</router-link></li>
      <li><router-link to="/orders-me">My Orders (Auth)</router-link></li>

      <!-- ✅ الجديد -->
      <li><router-link to="/admin/vendors">My Vendors (Admin/Merchant)</router-link></li>
      <li><router-link to="/admin/branches">My Branches (Admin/Merchant)</router-link></li>
      <li><router-link to="/admin/inventory">Inventory (Admin/Merchant)</router-link></li>

    </ul>

    <p v-if="sessionEmail">Logged as: {{ sessionEmail }}</p>

    <!-- ✅ يطلع لك Vendor IDs حقّك -->
    <div v-if="vendorIds.length" style="margin-top:14px;padding:10px;border:1px solid #ddd">
      <b>Your Vendor IDs:</b>
      <div v-for="id in vendorIds" :key="id" style="font-family:monospace">
        {{ id }}
      </div>
      <small>انسخ واحد منها وحطه في صفحة إنشاء المنتجات/الفروع.</small>
    </div>

    <p v-if="vendorErr" style="color:#b00020;margin-top:10px">
      {{ vendorErr }}
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { supabase } from "../lib/supabase";
import { useRouter } from "vue-router";
import api from "../lib/api"; // ✅

const router = useRouter();
const sessionEmail = ref("");

const vendorIds = ref([]);
const vendorErr = ref("");

onMounted(async () => {
  const { data } = await supabase.auth.getSession();
  sessionEmail.value = data.session?.user?.email || "";

  // ✅ نجيب vendor_ids من API (يتطلب admin/merchant role)
  try {
    const res = await api.get("/v1/vendor-admin/me");
    vendorIds.value = res.data?.vendor_ids || [];
  } catch (e) {
    vendorErr.value =
      e?.response?.data?.detail ||
      "Could not load vendor ids (need admin/merchant role).";
  }
});

async function logout() {
  await supabase.auth.signOut();
  router.push("/login");
}
</script>
