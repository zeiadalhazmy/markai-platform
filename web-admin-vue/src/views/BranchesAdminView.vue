<template>
  <div style="max-width: 900px; margin: 30px auto;">
    <h2>Admin - Branches</h2>

    <div style="border:1px solid #ddd; padding:12px; margin:12px 0;">
      <h3>Create Branch</h3>
      <input v-model="form.vendor_id" placeholder="vendor_id" />
      <input v-model="form.name" placeholder="name" />
      <input v-model="form.city" placeholder="city" />
      <button @click="createBranch">Create</button>
      <span style="color:#b00; margin-left:10px;">{{ err }}</span>
    </div>

    <div style="margin: 12px 0;">
      <input v-model="filterVendorId" placeholder="filter vendor_id (optional)" />
      <button @click="load">Reload</button>
    </div>

    <ul>
      <li v-for="b in branches" :key="b.id" style="margin: 8px 0;">
        <b>{{ b.name }}</b> — {{ b.id }} — vendor: {{ b.vendor_id }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from "../lib/api";

export default {
  data() {
    return {
      branches: [],
      err: "",
      filterVendorId: "",
      form: { vendor_id: "", name: "", city: "" },
    };
  },
  methods: {
    async load() {
      this.err = "";
      try {
        const q = this.filterVendorId ? `?vendor_id=${encodeURIComponent(this.filterVendorId)}` : "";
        const res = await api.get(`/v1/vendor-admin/branches${q}`);
        this.branches = res.data;
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
    async createBranch() {
      this.err = "";
      try {
        await api.post("/v1/vendor-admin/branches", { ...this.form });
        this.form = { vendor_id: "", name: "", city: "" };
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
