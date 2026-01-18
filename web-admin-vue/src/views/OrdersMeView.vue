<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <h2>My Orders</h2>

    <button @click="load" style="padding:8px 12px">Refresh</button>

    <p v-if="loading">Loading...</p>
    <p v-if="error" style="color:red">{{ error }}</p>

    <div v-for="o in orders" :key="o.id" style="border:1px solid #ddd;padding:12px;margin:10px 0">
      <b>Order: {{ o.id }}</b>
      <div>Status: {{ o.status }}</div>
      <div>Total: {{ o.total || o.total_amount || o.amount_total }}</div>
      <div>Created: {{ o.created_at }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../lib/api";

const orders = ref([]);
const loading = ref(false);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await api.get("/v1/orders/me");
    orders.value = res.data;
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message;
  } finally {
    loading.value = false;
  }
}

load();
</script>
