<template>
  <div style="max-width: 1000px; margin: 30px auto;">
    <h2>Admin - Orders</h2>

    <div style="margin: 12px 0;">
      <input v-model="vendorId" placeholder="vendor_id (optional for admin)" />
      <input v-model="branchId" placeholder="branch_id (optional)" />
      <button @click="load">Reload</button>
      <span style="color:#b00; margin-left:10px;">{{ err }}</span>
    </div>

    <div style="border:1px solid #ddd; padding:12px; margin:12px 0;">
      <h3>Update Order Status</h3>
      <input v-model="statusForm.order_id" placeholder="order_id" />
      <input v-model="statusForm.status" placeholder="status (placed/accepted/...)" />
      <button @click="updateStatus">Update</button>
    </div>

    <ul>
      <li v-for="o in orders" :key="o.id" style="margin: 10px 0;">
        <b>{{ o.id }}</b> — status: {{ o.status }} — total: {{ o.total || o.total_amount || o.total_price }}
      </li>
    </ul>
  </div>
</template>

<script>
import api from "../lib/api";

export default {
  data() {
    return {
      orders: [],
      err: "",
      vendorId: "",
      branchId: "",
      statusForm: { order_id: "", status: "accepted" },
    };
  },
  methods: {
    async load() {
      this.err = "";
      try {
        const params = [];
        if (this.vendorId) params.push(`vendor_id=${encodeURIComponent(this.vendorId)}`);
        if (this.branchId) params.push(`branch_id=${encodeURIComponent(this.branchId)}`);
        const q = params.length ? `?${params.join("&")}` : "";
        const res = await api.get(`/v1/vendor-admin/orders${q}`);
        this.orders = res.data;
      } catch (e) {
        this.err = e?.response?.data?.detail || e.message;
      }
    },
    async updateStatus() {
      this.err = "";
      try {
        await api.patch(`/v1/orders/${this.statusForm.order_id}/status`, { status: this.statusForm.status });
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
