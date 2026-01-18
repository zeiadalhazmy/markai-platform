<template>
  <div style="max-width:1000px;margin:30px auto;font-family:sans-serif">
    <h2>Checkout (Create Order)</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>1) Choose Branch</h3>

      <select v-model="branchId" @change="loadProducts" style="padding:6px;min-width:420px">
        <option disabled value="">-- choose vendor branch --</option>
        <option v-for="b in branches" :key="b.id" :value="String(b.id)">
          {{ b.name || "Branch" }} — {{ b.id }}
        </option>
      </select>

      <button @click="loadBranches" style="padding:6px 10px;margin-left:10px">Reload</button>

      <p style="margin-top:10px;color:#666">
        address_id (saved): <b>{{ addressId || "NOT SET" }}</b>
        <span v-if="!addressId" style="color:red"> — create one first in Addresses</span>
      </p>

      <p v-if="err" style="color:red">{{ err }}</p>
      <p v-if="ok" style="color:green">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0" v-if="branchId">
      <h3>2) Products (from this branch)</h3>

      <button @click="loadProducts" style="padding:6px 10px">Reload Products</button>

      <div style="margin-top:10px">
        <div v-for="p in products" :key="p.id" style="border:1px solid #eee;padding:10px;margin:8px 0">
          <div style="display:flex;justify-content:space-between;gap:12px;align-items:center">
            <div>
              <b>{{ p.name || p.title || "Product" }}</b>
              <div style="color:#666">id: {{ p.id }}</div>
              <div style="color:#666">
                price: {{ displayPrice(p) }}
                <span v-if="p.branch_quantity != null"> — qty: {{ p.branch_quantity }}</span>
              </div>
            </div>

            <div style="display:flex;gap:8px;align-items:center">
              <input type="number" min="1" v-model.number="qtyMap[p.id]" style="padding:6px;width:90px" />
              <button @click="addToCart(p)" style="padding:8px 12px">Add</button>
            </div>
          </div>
        </div>

        <p v-if="!products.length" style="color:#666">No products found.</p>
      </div>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>3) Cart</h3>

      <ul>
        <li v-for="c in cart" :key="c.product_id" style="margin:6px 0">
          <b>{{ c.name }}</b> — qty: {{ c.quantity }}
          <button @click="removeFromCart(c.product_id)" style="margin-left:10px">Remove</button>
        </li>
      </ul>

      <p v-if="!cart.length" style="color:#666">Cart is empty.</p>

      <button
        @click="createOrder"
        style="padding:10px 14px;margin-top:10px"
        :disabled="!cart.length || !branchId || !addressId"
      >
        Create Order
      </button>

      <div v-if="createdOrderId" style="margin-top:10px">
        ✅ Order created: <b>{{ createdOrderId }}</b>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../lib/api";

const branches = ref([]);
const products = ref([]);

const branchId = ref("");
const addressId = ref("");

const qtyMap = reactive({});
const cart = ref([]);
const createdOrderId = ref("");

const err = ref("");
const ok = ref("");

function resetMsgs() {
  err.value = "";
  ok.value = "";
}

function loadSavedAddress() {
  addressId.value = localStorage.getItem("markai_address_id") || "";
}

function displayPrice(p) {
  // إذا رجعت branch_price_override استخدمها وإلا price
  const v = p.branch_price_override ?? p.price ?? 0;
  return Number(v);
}

async function loadBranches() {
  resetMsgs();
  try {
    const { data } = await api.get("/v1/vendor-branches");
    branches.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load branches";
  }
}

async function loadProducts() {
  resetMsgs();
  products.value = [];
  if (!branchId.value) return;

  try {
    const { data } = await api.get("/v1/products", { params: { branch_id: branchId.value, limit: 200 } });
    products.value = data || [];

    // init qtyMap
    for (const p of products.value) {
      if (qtyMap[p.id] == null) qtyMap[p.id] = 1;
    }
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load products";
  }
}

function addToCart(p) {
  const q = Math.max(1, Number(qtyMap[p.id] || 1));
  const existing = cart.value.find((x) => x.product_id === String(p.id));
  if (existing) {
    existing.quantity += q;
  } else {
    cart.value.push({
      product_id: String(p.id),
      quantity: q,
      name: p.name || p.title || "Product",
    });
  }
  ok.value = "Added to cart";
}

function removeFromCart(pid) {
  cart.value = cart.value.filter((x) => x.product_id !== String(pid));
}

async function createOrder() {
  resetMsgs();
  createdOrderId.value = "";

  try {
    const payload = {
      vendor_branch_id: branchId.value,
      address_id: addressId.value,
      items: cart.value.map((x) => ({ product_id: x.product_id, quantity: x.quantity })),
      type: "water_truck",
      notes: "created from web-admin-vue checkout",
    };

    const { data } = await api.post("/v1/orders", payload);
    createdOrderId.value = String(data?.id || "");
    ok.value = `Order created. total: ${data?.total ?? ""}`;

    cart.value = [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create order failed";
  }
}

onMounted(async () => {
  loadSavedAddress();
  await loadBranches();
});
</script>
