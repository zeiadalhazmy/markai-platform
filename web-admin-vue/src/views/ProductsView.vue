<template>
  <div style="max-width:900px;margin:30px auto;font-family:sans-serif">
    <h2>Products</h2>

    <div style="margin:12px 0">
      <input v-model="q" placeholder="search..." style="padding:8px;width:240px" />
      <button @click="load" style="margin-left:8px;padding:8px 12px">Load</button>
    </div>

    <p v-if="loading">Loading...</p>
    <p v-if="error" style="color:red">{{ error }}</p>

    <div v-for="p in products" :key="p.id" style="border:1px solid #ddd;padding:12px;margin:10px 0">
      <b>{{ p.name || p.title || "Product" }}</b>
      <div>ID: {{ p.id }}</div>
      <div v-if="p.images?.length">Images: {{ p.images.length }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../lib/api";

const q = ref("");
const products = ref([]);
const loading = ref(false);
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await api.get("/v1/products", { params: { q: q.value || undefined } });
    products.value = res.data;
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message;
  } finally {
    loading.value = false;
  }
}

load();
</script>
