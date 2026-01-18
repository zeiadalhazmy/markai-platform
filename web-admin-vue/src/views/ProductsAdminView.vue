<template>
  <div style="max-width: 900px; margin: 30px auto;">
    <h2>Admin - Products</h2>

    <div style="border:1px solid #ddd; padding:12px; margin:12px 0;">
      <h3>Create Product</h3>
      <input v-model="form.vendor_id" placeholder="vendor_id (optional)" />
      <input v-model="form.name" placeholder="name" />
      <input v-model.number="form.price" placeholder="price" />
      <input v-model="form.category_id" placeholder="category_id (optional)" />
      <button @click="createProduct">Create</button>
      <span style="color:#b00; margin-left:10px;">{{ err }}</span>
    </div>

    <div style="border:1px solid #ddd; padding:12px; margin:12px 0;">
      <h3>Add Image</h3>
      <input v-model="img.product_id" placeholder="product_id" />
      <input v-model="img.url" placeholder="image url" />
      <button @click="addImage">Add</button>
    </div>

    <div style="margin: 12px 0;">
      <input v-model="filterVendorId" placeholder="filter vendor_id (optional)" />
      <button @click="load">Reload</button>
    </div>

    <ul>
      <li v-for="p in products" :key="p.id" style="margin: 8px 0;">
        <b>{{ p.name }}</b> — {{ p.id }} — price: {{ p.price }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from "../lib/api";

export default {
  data() {
    return {
      products: [],
      err: "",
      filterVendorId: "",
      form: { vendor_id: "", name: "", price: 0, category_id: "" },
      img: { product_id: "", url: "" },
    };
  },
  methods: {
    async load() {
      this.err = "";
      try {
        const q = this.filterVendorId ? `?vendor_id=${encodeURIComponent(this.filterVendorId)}` : "";
        const res = await api.get(`/v1/vendor-admin/products${q}`);
        this.products = res.data;
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
    async createProduct() {
      this.err = "";
      try {
        const payload = { ...this.form };
        if (!payload.vendor_id) delete payload.vendor_id;
        if (!payload.category_id) delete payload.category_id;
        await api.post("/v1/vendor-admin/products", payload);
        this.form = { vendor_id: "", name: "", price: 0, category_id: "" };
        await this.load();
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
    async addImage() {
      this.err = "";
      try {
        await api.post(`/v1/vendor-admin/products/${this.img.product_id}/images`, { url: this.img.url });
        this.img = { product_id: "", url: "" };
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
  },
  mounted() {
    this.load();
  },
};
</script>
