<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <h2>My Addresses</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Create Address</h3>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <input v-model="label" placeholder="label (home/work)" style="padding:6px;width:220px" />
        <input v-model="city" placeholder="city" style="padding:6px;width:160px" />
        <input v-model="area" placeholder="area/district" style="padding:6px;width:200px" />
        <input v-model="street" placeholder="street" style="padding:6px;width:240px" />
        <input v-model="notes" placeholder="notes/landmark" style="padding:6px;width:280px" />
        <button @click="createAddress" style="padding:8px 12px">Save</button>
      </div>

      <p v-if="ok" style="color:green;margin-top:10px">{{ ok }}</p>
      <p v-if="err" style="color:red;margin-top:10px">{{ err }}</p>

      <div v-if="savedAddressId" style="margin-top:10px;color:#333">
        ✅ Default address_id saved: <b>{{ savedAddressId }}</b>
      </div>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>Saved (local)</h3>
      <p style="color:#666">
        نخزّن آخر address_id في localStorage لاستخدامه في الطلبات.
      </p>
      <button @click="clearSaved" style="padding:6px 10px">Clear saved address_id</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const label = ref("home");
const city = ref("Sana'a");
const area = ref("");
const street = ref("");
const notes = ref("");

const ok = ref("");
const err = ref("");

const savedAddressId = ref("");

function resetMsgs() {
  ok.value = "";
  err.value = "";
}

function loadSaved() {
  savedAddressId.value = localStorage.getItem("markai_address_id") || "";
}

async function createAddress() {
  resetMsgs();
  try {
    const payload = {
      label: label.value,
      city: city.value,
      area: area.value,
      street: street.value,
      notes: notes.value,
      is_default: true,
    };

    const { data } = await api.post("/v1/addresses", payload);
    const id = String(data?.id || "");
    if (!id) throw new Error("No id returned");

    localStorage.setItem("markai_address_id", id);
    savedAddressId.value = id;

    ok.value = `Address created. id: ${id}`;
    area.value = "";
    street.value = "";
    notes.value = "";
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create address failed";
  }
}

function clearSaved() {
  localStorage.removeItem("markai_address_id");
  loadSaved();
}

onMounted(loadSaved);
</script>
