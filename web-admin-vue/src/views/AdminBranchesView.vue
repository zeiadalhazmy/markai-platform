<template>
  <div style="max-width:1000px;margin:30px auto;font-family:sans-serif">
    <h2>Admin - Branches</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Select Vendor</h3>

      <select v-model="vendorId" @change="loadBranches" style="padding:6px;min-width:320px">
        <option disabled value="">-- choose vendor --</option>
        <option v-for="v in vendors" :key="v.id" :value="String(v.id)">
          {{ v.name || v.title || "Vendor" }} — {{ v.id }}
        </option>
      </select>

      <p v-if="err" style="color:red">{{ err }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Create Branch</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <input v-model="branchName" placeholder="branch name" style="padding:6px;width:220px" />
        <input v-model="branchCity" placeholder="city" style="padding:6px;width:180px" />
        <button @click="createBranch" style="padding:8px 12px" :disabled="!vendorId">Create</button>
      </div>
      <p v-if="ok" style="color:green">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Branches</h3>
      <button @click="loadBranches" style="padding:6px 10px" :disabled="!vendorId">Reload</button>

      <ul>
        <li v-for="b in branches" :key="b.id">
          <b>{{ b.name || "Branch" }}</b>
          — id: {{ b.id }}
          <span v-if="b.city"> — city: {{ b.city }}</span>
        </li>
      </ul>
      <p v-if="vendorId && !branches.length">No branches for this vendor.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const vendors = ref([]);
const branches = ref([]);

const vendorId = ref("");
const branchName = ref("");
const branchCity = ref("");

const err = ref("");
const ok = ref("");

async function loadVendors() {
  err.value = "";
  try {
    const { data } = await api.get("/v1/vendor-admin/vendors");
    vendors.value = data || [];
    if (!vendorId.value && vendors.value.length) {
      vendorId.value = String(vendors.value[0].id);
      await loadBranches();
    }
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load vendors";
  }
}

async function loadBranches() {
  ok.value = "";
  err.value = "";
  branches.value = [];
  if (!vendorId.value) return;

  try {
    const { data } = await api.get("/v1/vendor-admin/branches", {
      params: { vendor_id: vendorId.value },
    });
    branches.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load branches";
  }
}

async function createBranch() {
  ok.value = "";
  err.value = "";
  if (!vendorId.value) {
    err.value = "Choose vendor first";
    return;
  }
  if (!branchName.value.trim()) {
    err.value = "branch name is required";
    return;
  }

  try {
    const payload = {
      vendor_id: vendorId.value,
      name: branchName.value.trim(),
      city: branchCity.value.trim() || undefined,
    };
    const { data } = await api.post("/v1/vendor-admin/branches", payload);
    ok.value = `Created branch id: ${data?.id}`;
    branchName.value = "";
    branchCity.value = "";
    await loadBranches();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create branch failed";
  }
}

onMounted(loadVendors);
</script>
