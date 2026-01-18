<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <h2>My Branches</h2>

    <div style="border:1px solid #ddd;padding:12px;margin:12px 0">
      <h3>Create Branch</h3>

      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <input v-model="form.vendor_id" placeholder="vendor_id" style="min-width:260px" />
        <input v-model="form.name" placeholder="branch name" />
        <input v-model="form.address" placeholder="address (optional)" />
        <button @click="createBranch" :disabled="loading">Create</button>
      </div>

      <small>
        vendor_id لازم يكون من Vendor IDs حقّك (من Dashboard أو صفحة Vendors).
      </small>

      <p v-if="msg" style="color:green">{{ msg }}</p>
      <p v-if="err" style="color:#b00020">{{ err }}</p>
    </div>

    <div style="margin:10px 0;display:flex;gap:8px;align-items:center">
      <input v-model="filterVendorId" placeholder="filter vendor_id (optional)" style="min-width:260px" />
      <button @click="load" :disabled="loading">Reload</button>
    </div>

    <ul>
      <li v-for="b in branches" :key="b.id" style="margin:10px 0">
        <b>{{ b.name || "Branch" }}</b>
        <div>vendor_id: <span style="font-family:monospace">{{ b.vendor_id }}</span></div>
        <div>id: <span style="font-family:monospace">{{ b.id }}</span></div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const branches = ref([]);
const loading = ref(false);
const err = ref("");
const msg = ref("");

const filterVendorId = ref("");

const form = ref({
  vendor_id: "",
  name: "",
  address: "",
});

async function load() {
  loading.value = true;
  err.value = "";
  try {
    const qs = filterVendorId.value ? `?vendor_id=${encodeURIComponent(filterVendorId.value)}` : "";
    const res = await api.get(`/v1/vendor-admin/branches${qs}`);
    branches.value = res.data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to load branches";
  } finally {
    loading.value = false;
  }
}

async function createBranch() {
  msg.value = "";
  err.value = "";

  if (!form.value.vendor_id.trim()) return (err.value = "vendor_id is required");
  if (!form.value.name.trim()) return (err.value = "name is required");

  loading.value = true;
  try {
    const res = await api.post("/v1/vendor-admin/branches", {
      vendor_id: form.value.vendor_id,
      name: form.value.name,
      address: form.value.address || undefined,
    });
    msg.value = `Created branch: ${res.data?.id}`;
    form.value.name = "";
    form.value.address = "";
    await load();
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to create branch";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
