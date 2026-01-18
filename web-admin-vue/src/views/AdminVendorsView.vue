<template>
  <div style="max-width:1000px;margin:30px auto;font-family:sans-serif">
    <h2>Admin - Vendors</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Create Vendor</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <input v-model="name" placeholder="name" style="padding:6px;width:220px" />
        <input v-model="city" placeholder="city" style="padding:6px;width:180px" />
        <button @click="createVendor" style="padding:8px 12px">Create</button>
      </div>
      <p v-if="err" style="color:red">{{ err }}</p>
      <p v-if="ok" style="color:green">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>My Vendors</h3>
      <button @click="load" style="padding:6px 10px">Reload</button>

      <ul>
        <li v-for="v in vendors" :key="v.id">
          <b>{{ v.name || v.title || "Vendor" }}</b>
          — id: {{ v.id }}
          <span v-if="v.city"> — city: {{ v.city }}</span>
        </li>
      </ul>
      <p v-if="!vendors.length">No vendors yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const vendors = ref([]);
const name = ref("");
const city = ref("");
const err = ref("");
const ok = ref("");

async function load() {
  err.value = "";
  ok.value = "";
  try {
    const { data } = await api.get("/v1/vendor-admin/vendors");
    vendors.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load vendors";
  }
}

async function createVendor() {
  err.value = "";
  ok.value = "";
  if (!name.value.trim()) {
    err.value = "name is required";
    return;
  }
  try {
    const payload = { name: name.value.trim(), city: city.value.trim() || undefined };
    const { data } = await api.post("/v1/vendor-admin/vendors", payload);
    ok.value = `Created vendor id: ${data?.id}`;
    name.value = "";
    city.value = "";
    await load();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create vendor failed";
  }
}

onMounted(load);
</script>
