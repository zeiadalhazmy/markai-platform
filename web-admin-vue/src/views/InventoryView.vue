<template>
  <div style="max-width:1000px;margin:30px auto;font-family:sans-serif">
    <h2>Inventory (Branch ↔ Product)</h2>

    <div style="border:1px solid #ddd;padding:12px;margin:12px 0">
      <h3>Upsert Inventory</h3>

      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
        <div>
          <div><small>Branch</small></div>
          <select v-model="form.branch_id" style="min-width:360px">
            <option value="">-- اختر فرع --</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">
              {{ b.name || "Branch" }} | {{ b.id }}
            </option>
          </select>
        </div>

        <div>
          <div><small>Product</small></div>
          <select v-model="form.product_id" style="min-width:360px">
            <option value="">-- اختر منتج --</option>
            <option v-for="p in products" :key="p.id" :value="p.id">
              {{ p.name || p.title || "Product" }} | {{ p.id }}
            </option>
          </select>
        </div>

        <div>
          <div><small>Quantity</small></div>
          <input v-model.number="form.quantity" type="number" min="0" style="width:120px" />
        </div>

        <div>
          <div><small>Price Override</small></div>
          <input v-model.number="form.price_override" type="number" min="0" style="width:140px" />
        </div>

        <div style="display:flex;gap:6px;align-items:center;margin-top:18px">
          <input id="avail" type="checkbox" v-model="form.is_available" />
          <label for="avail">Available</label>
        </div>

        <button @click="save" :disabled="loading" style="padding:8px 12px;margin-top:18px">
          Save
        </button>
      </div>

      <p v-if="msg" style="color:green;margin-top:10px">{{ msg }}</p>
      <p v-if="err" style="color:#b00020;margin-top:10px">{{ err }}</p>
    </div>

    <div style="display:flex;gap:10px;align-items:center;margin:10px 0">
      <button @click="loadAll" :disabled="loading">Reload Lists</button>
      <small>لو ما ظهرت البيانات، تأكد حسابك role = admin/merchant</small>
    </div>

    <hr />

    <h3>Quick Test</h3>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <input v-model="testBranchId" placeholder="branch_id للتجربة" style="min-width:380px" />
      <button @click="testProducts" :disabled="loading">Test /v1/products?branch_id=...</button>
    </div>

    <pre v-if="testOut" style="background:#f7f7f7;padding:10px;margin-top:10px;max-height:280px;overflow:auto">
{{ testOut }}
    </pre>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const branches = ref([]);
const products = ref([]);
const loading = ref(false);
const err = ref("");
const msg = ref("");

const form = ref({
  branch_id: "",
  product_id: "",
  quantity: 0,
  price_override: 0,
  is_available: true,
});

const testBranchId = ref("");
const testOut = ref("");

async function loadAll() {
  loading.value = true;
  err.value = "";
  msg.value = "";
  try {
    // فروعك
    const b = await api.get("/v1/vendor-admin/branches");
    branches.value = b.data || [];

    // منتجاتك
    const p = await api.get("/v1/vendor-admin/products");
    products.value = p.data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to load branches/products";
  } finally {
    loading.value = false;
  }
}

async function save() {
  err.value = "";
  msg.value = "";

  if (!form.value.branch_id) return (err.value = "branch_id is required");
  if (!form.value.product_id) return (err.value = "product_id is required");

  loading.value = true;
  try {
    const payload = {
      branch_id: form.value.branch_id,
      product_id: form.value.product_id,
      quantity: Number(form.value.quantity || 0),
      price_override: Number(form.value.price_override || 0),
      is_available: !!form.value.is_available,
    };

    const res = await api.put("/v1/vendor-admin/inventory", payload);
    msg.value = `Saved ✅ (${res.data?.mode || "ok"})`;
  } catch (e) {
    err.value = e?.response?.data?.detail || "Failed to save inventory";
  } finally {
    loading.value = false;
  }
}

async function testProducts() {
  testOut.value = "";
  err.value = "";
  const bid = testBranchId.value.trim();
  if (!bid) return (err.value = "اكتب branch_id للتجربة");

  loading.value = true;
  try {
    // endpoint public
    const res = await api.get(`/v1/products?branch_id=${encodeURIComponent(bid)}`);
    testOut.value = JSON.stringify(res.data, null, 2);
  } catch (e) {
    err.value = e?.response?.data?.detail || "Test failed";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);
</script>
