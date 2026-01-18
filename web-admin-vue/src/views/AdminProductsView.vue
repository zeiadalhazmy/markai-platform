<template>
  <div style="max-width:1100px;margin:30px auto;font-family:sans-serif">
    <h2>Admin - Products</h2>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>1) Choose Vendor</h3>

      <select v-model="vendorId" @change="onVendorChange" style="padding:6px;min-width:360px">
        <option disabled value="">-- choose vendor --</option>
        <option v-for="v in vendors" :key="v.id" :value="String(v.id)">
          {{ v.name || v.title || "Vendor" }} — {{ v.id }}
        </option>
      </select>

      <button @click="loadVendors" style="padding:6px 10px;margin-left:10px">Reload Vendors</button>
      <p v-if="err" style="color:red;margin-top:10px">{{ err }}</p>
      <p v-if="ok" style="color:green;margin-top:10px">{{ ok }}</p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>2) Choose Branch (for inventory)</h3>

      <select v-model="branchId" style="padding:6px;min-width:360px" :disabled="!vendorId">
        <option disabled value="">-- choose branch --</option>
        <option v-for="b in branches" :key="b.id" :value="String(b.id)">
          {{ b.name || "Branch" }} — {{ b.id }}
        </option>
      </select>

      <button @click="loadBranches" style="padding:6px 10px;margin-left:10px" :disabled="!vendorId">
        Reload Branches
      </button>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>3) Create Product</h3>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <input v-model="pName" placeholder="name" style="padding:6px;width:220px" />
        <input v-model.number="pPrice" type="number" placeholder="price" style="padding:6px;width:140px" />
        <input v-model="pCategoryId" placeholder="category_id (optional)" style="padding:6px;width:220px" />
        <button @click="createProduct" style="padding:8px 12px" :disabled="!vendorId">Create</button>
      </div>

      <p style="margin-top:10px;color:#666">
        ملاحظة: المنتج ينربط تلقائيًا بـ vendor_id المختار (بدون كتابة يدوي).
      </p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>4) Add Image (URL)</h3>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <input v-model="imgProductId" placeholder="product_id" style="padding:6px;width:220px" />
        <input v-model="imgUrl" placeholder="image url" style="padding:6px;width:520px" />
        <button @click="addImage" style="padding:8px 12px">Add</button>
      </div>

      <p style="margin-top:10px;color:#666">
        تقدر تلصق product_id من قائمة المنتجات تحت.
      </p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>5) Upsert Inventory (Branch + Product)</h3>

      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <input v-model="invProductId" placeholder="product_id" style="padding:6px;width:220px" />
        <input v-model.number="invQty" type="number" placeholder="quantity" style="padding:6px;width:140px" />
        <input v-model.number="invPrice" type="number" placeholder="price_override (optional)" style="padding:6px;width:200px" />
        <label style="display:flex;align-items:center;gap:6px">
          <input type="checkbox" v-model="invAvailable" />
          available
        </label>

        <button @click="upsertInventory" style="padding:8px 12px" :disabled="!branchId">
          Save Inventory
        </button>
      </div>

      <p style="margin-top:10px;color:#666">
        لازم تختار Branch أولًا. branch_id سيتم استخدامه تلقائيًا.
      </p>
    </div>

    <div style="border:1px solid #ddd;padding:15px;margin:15px 0">
      <h3>6) My Products</h3>

      <button @click="loadProducts" style="padding:6px 10px" :disabled="!vendorId">Reload Products</button>

      <ul style="margin-top:10px">
        <li v-for="p in products" :key="p.id" style="margin:6px 0">
          <b>{{ p.name || p.title || "Product" }}</b>
          — id: {{ p.id }}
          <span v-if="p.price != null"> — price: {{ p.price }}</span>
          <span v-if="p.vendor_id"> — vendor_id: {{ p.vendor_id }}</span>
        </li>
      </ul>

      <p v-if="vendorId && !products.length" style="color:#666;margin-top:10px">No products for this vendor.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../lib/api";

const vendors = ref([]);
const branches = ref([]);
const products = ref([]);

const vendorId = ref("");
const branchId = ref("");

const pName = ref("");
const pPrice = ref(null);
const pCategoryId = ref("");

const imgProductId = ref("");
const imgUrl = ref("");

const invProductId = ref("");
const invQty = ref(1);
const invPrice = ref(null);
const invAvailable = ref(true);

const err = ref("");
const ok = ref("");

function resetMsgs() {
  err.value = "";
  ok.value = "";
}

async function loadVendors() {
  resetMsgs();
  try {
    const { data } = await api.get("/v1/vendor-admin/vendors");
    vendors.value = data || [];
    if (!vendorId.value && vendors.value.length) {
      vendorId.value = String(vendors.value[0].id);
      await onVendorChange();
    }
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load vendors";
  }
}

async function loadBranches() {
  resetMsgs();
  branches.value = [];
  if (!vendorId.value) return;
  try {
    const { data } = await api.get("/v1/vendor-admin/branches", {
      params: { vendor_id: vendorId.value },
    });
    branches.value = data || [];
    if (!branchId.value && branches.value.length) {
      branchId.value = String(branches.value[0].id);
    }
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load branches";
  }
}

async function loadProducts() {
  resetMsgs();
  products.value = [];
  if (!vendorId.value) return;

  try {
    const { data } = await api.get("/v1/vendor-admin/products", {
      params: { vendor_id: vendorId.value },
    });
    products.value = data || [];
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Failed to load products";
  }
}

async function onVendorChange() {
  branchId.value = "";
  await loadBranches();
  await loadProducts();
}

async function createProduct() {
  resetMsgs();
  if (!vendorId.value) {
    err.value = "Choose vendor first";
    return;
  }
  if (!pName.value.trim()) {
    err.value = "name is required";
    return;
  }

  try {
    const payload = {
      vendor_id: vendorId.value,
      name: pName.value.trim(),
      price: pPrice.value ?? undefined,
      category_id: pCategoryId.value.trim() || undefined,
    };

    const { data } = await api.post("/v1/vendor-admin/products", payload);
    ok.value = `Created product id: ${data?.id}`;

    // autofill for next steps
    imgProductId.value = String(data?.id || "");
    invProductId.value = String(data?.id || "");

    pName.value = "";
    pPrice.value = null;
    pCategoryId.value = "";

    await loadProducts();
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Create product failed";
  }
}

async function addImage() {
  resetMsgs();
  if (!imgProductId.value.trim()) {
    err.value = "product_id is required";
    return;
  }
  if (!imgUrl.value.trim()) {
    err.value = "image url is required";
    return;
  }

  try {
    const payload = { url: imgUrl.value.trim() };
    const { data } = await api.post(`/v1/vendor-admin/products/${imgProductId.value.trim()}/images`, payload);
    ok.value = `Added image id: ${data?.id}`;
    imgUrl.value = "";
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Add image failed";
  }
}

async function upsertInventory() {
  resetMsgs();
  if (!branchId.value) {
    err.value = "Choose branch first";
    return;
  }
  if (!invProductId.value.trim()) {
    err.value = "product_id is required";
    return;
  }

  try {
    const payload = {
      branch_id: branchId.value,
      product_id: invProductId.value.trim(),
      quantity: Number(invQty.value || 0),
      price_override: invPrice.value == null ? undefined : Number(invPrice.value),
      is_available: Boolean(invAvailable.value),
    };

    const { data } = await api.put("/v1/vendor-admin/inventory", payload);
    ok.value = `Inventory saved (${data?.mode || "ok"})`;
  } catch (e) {
    err.value = e?.response?.data?.detail || e.message || "Inventory failed";
  }
}

onMounted(loadVendors);
</script>
