<template>
  <div style="max-width:1000px;margin:30px auto;font-family:sans-serif">
    <h2>Service Requests (Water Truck)</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Create Request</h3>

      <p style="color:#666">
        address_id (saved): <b>{{ addressId || "NOT SET" }}</b>
      </p>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <select v-model="branchId" style="padding:6px;min-width:420px">
          <option disabled value="">-- choose vendor branch --</option>
          <option v-for="b in branches" :key="b.id" :value="String(b.id)">
            {{ b.name || "Branch" }} — {{ b.id }}
          </option>
        </select>

        <input v-model.number="liters" type="number" min="1" placeholder="liters (e.g. 1000)" style="padding:6px;width:200px" />
        <input v-model.number="price" type="number" min="0" placeholder="quoted_price (optional)" style="padding:6px;width:220px" />

        <button @click="createReq" style="padding:8px 12px" :disabled="!addressId || !branchId">Create</button>
        <button @click="loadMine" style="padding:8px 12px">Reload My Requests</button>
      </div>

      <p v-if="err" style="color:red;margin-top:10px">{{ err }}</p>
      <p v-if="ok" style="color:green;margin-top:10px">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>My Requests</h3>
      <ul>
        <li v-for="r in mine" :key="r.id" style="margin:8px 0">
          <b>{{ r.id }}</b>
          — status: {{ r.status }}
          — branch: {{ r.vendor_branch_id }}
          <span v-if="r.details?.liters"> — liters: {{ r.details.liters }}</span>
        </li>
      </ul>
      <p v-if="!mine.length" style="color:#666">No requests yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const branches = ref([]);
const branchId = ref("");
const addressId = ref("");

const liters = ref(1000);
const price = ref(null);

const mine = ref([]);

const err = ref("");
const ok = ref("");

function resetMsgs() {
  err.value = "";
  ok.value = "";
}

function loadSavedAddress() {
  addressId.value = localStorage.getItem("markai_address_id") || "";
}

async function loadBranches() {
  try {
    const { data } = await api.get("/v1/vendor-branches");
    branches.value = data || [];
  } catch (e) {
    // ignore
  }
}

async function createReq() {
  resetMsgs();
  try {
    const payload = {
      address_id: addressId.value,
      vendor_branch_id: branchId.value,
      service_type: "water_truck",
      details: { liters: Number(liters.value || 0) },
      quoted_price: price.value == null ? undefined : Number(price.value),
      status: "pending",
    };

    const { data } = await api.post("/v1/service-requests", payload);
    ok.value = `Request created id: ${data?.id}`;
    await loadMine();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create request failed";
  }
}

async function loadMine() {
  resetMsgs();
  try {
    const { data } = await api.get("/v1/service-requests/me");
    mine.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Load my requests failed";
  }
}

onMounted(async () => {
  loadSavedAddress();
  await loadBranches();
  await loadMine();
});
</script>
