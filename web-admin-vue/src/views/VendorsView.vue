<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <h2>My Vendors</h2>

    <div style="border:1px solid #ddd;padding:12px;margin:12px 0">
      <h3>Create Vendor</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <input v-model="form.name" placeholder="name" />
        <input v-model="form.city" placeholder="city (optional)" />
        <button @click="createVendor" :disabled="loading">Create</button>
      </div>
      <p v-if="msg" style="color:green">{{ msg }}</p>
      <p v-if="err" style="color:#b00020">{{ err }}</p>
    </div>

    <button @click="load" :disabled="loading">Reload</button>

    <ul>
      <li v-for="v in vendors" :key="v.id" style="margin:10px 0">
        <b>{{ v.name || "Vendor" }}</b>
        <div style="font-family:monospace">{{ v.id }}</div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const vendors = ref([]);
const loading = ref(false);
const err = ref("");
const msg = ref("");

const form = ref({
  name: "",
  city: "",
});

async function load() {
  loading.value = true;
  err.value = "";
  try {
    const res = await api.get("/v1/vendor-admin/vendors");
    vendors.value = res.data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to load vendors";
  } finally {
    loading.value = false;
  }
}

async function createVendor() {
  msg.value = "";
  err.value = "";
  if (!form.value.name.trim()) {
    err.value = "name is required";
    return;
  }
  loading.value = true;
  try {
    // backend بيحط owner تلقائيًا لو العمود موجود
    const res = await api.post("/v1/vendor-admin/vendors", {
      name: form.value.name,
      city: form.value.city || undefined,
    });
    msg.value = `Created: ${res.data?.id}`;
    form.value.name = "";
    form.value.city = "";
    await load();
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to create vendor";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
