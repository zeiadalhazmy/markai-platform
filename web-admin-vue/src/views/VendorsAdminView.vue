<template>
  <div style="max-width: 900px; margin: 30px auto;">
    <h2>Admin - Vendors</h2>

    <div style="border:1px solid #ddd; padding:12px; margin:12px 0;">
      <h3>Create Vendor</h3>
      <input v-model="form.name" placeholder="name" />
      <input v-model="form.description" placeholder="description" />
      <button @click="createVendor">Create</button>
      <span style="color:#b00; margin-left:10px;">{{ err }}</span>
    </div>

    <button @click="load">Reload</button>

    <ul>
      <li v-for="v in vendors" :key="v.id" style="margin: 8px 0;">
        <b>{{ v.name }}</b> — {{ v.id }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from "../lib/api";

export default {
  data() {
    return {
      vendors: [],
      err: "",
      form: { name: "", description: "" },
    };
  },
  methods: {
    async load() {
      this.err = "";
      try {
        const res = await api.get("/v1/vendor-admin/vendors");
        this.vendors = res.data;
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
    async createVendor() {
      this.err = "";
      try {
        await api.post("/v1/vendor-admin/vendors", { ...this.form });
        this.form = { name: "", description: "" };
        await this.load();
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
