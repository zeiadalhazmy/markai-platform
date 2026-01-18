<template>
  <div style="max-width:1100px;margin:30px auto;font-family:sans-serif">
    <h2>Courier Panel</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <button @click="loadAvailable" style="padding:8px 12px">Reload Available</button>
      <p v-if="err" style="color:red;margin-top:10px">{{ err }}</p>
      <p v-if="ok" style="color:green;margin-top:10px">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Available (pending)</h3>

      <div v-for="r in available" :key="r.id" style="border:1px solid #eee;padding:12px;margin:10px 0">
        <div><b>{{ r.id }}</b> — status: {{ r.status }}</div>
        <div style="color:#666">branch: {{ r.vendor_branch_id }} — address: {{ r.address_id }}</div>
        <div style="color:#666" v-if="r.details?.liters">liters: {{ r.details.liters }}</div>

        <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap">
          <button @click="accept(r.id)" style="padding:8px 12px">Accept</button>
          <button @click="complete(r.id)" style="padding:8px 12px">Complete</button>
        </div>
      </div>

      <p v-if="!available.length" style="color:#666">No pending requests.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../lib/api";

const available = ref([]);
const err = ref("");
const ok = ref("");

function resetMsgs() {
  err.value = "";
  ok.value = "";
}

async function loadAvailable() {
  resetMsgs();
  try {
    const { data } = await api.get("/v1/service-requests/available");
    available.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Load available failed (need courier/admin role)";
  }
}

async function accept(id) {
  resetMsgs();
  try {
    await api.post(`/v1/service-requests/${id}/accept`);
    ok.value = `Accepted: ${id}`;
    await loadAvailable();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Accept failed";
  }
}

async function complete(id) {
  resetMsgs();
  try {
    await api.post(`/v1/service-requests/${id}/complete`);
    ok.value = `Completed: ${id}`;
    await loadAvailable();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Complete failed";
  }
}
</script>
