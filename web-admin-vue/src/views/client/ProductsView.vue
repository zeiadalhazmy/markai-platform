<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">المنتجات</h2>
            <div class="muted">ابحث واختر واضف للسلة</div>
          </div>

          <div class="row" style="flex-wrap:wrap;">
            <input class="input" style="width:260px;" v-model="q" placeholder="بحث..." @input="filter" />
            <button class="btn" @click="reload" :disabled="loading">تحديث</button>
          </div>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div style="margin-top:14px;" class="grid3">
          <div v-for="p in view" :key="p.id" class="card" style="padding:14px;">
            <div class="card" style="height:120px; border-radius:14px; background: rgba(0,0,0,.25); border:1px solid var(--border);"></div>

            <div style="margin-top:10px; display:flex; justify-content:space-between; gap:10px;">
              <div>
                <div style="font-weight:900;">{{ p.name }}</div>
                <div class="muted" style="font-size:12px;">{{ p.vendor_name || "متجر" }}</div>
              </div>
              <div style="font-weight:900;">{{ money(p.price) }}</div>
            </div>

            <div class="row" style="margin-top:10px; justify-content:space-between;">
              <button class="btn btn-primary" @click="add(p)">إضافة</button>
              <span class="badge">متاح</span>
            </div>
          </div>
        </div>

        <div v-if="!loading && view.length===0" class="muted" style="margin-top:12px;">
          لا توجد منتجات.
        </div>
      </div>

      <div class="card" style="padding:18px; margin-top:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
          <div>
            <h2 class="h2">السلة</h2>
            <div class="muted">{{ cart.length }} عنصر</div>
          </div>
          <button class="btn btn-primary" :disabled="cart.length===0 || ordering" @click="checkout">
            {{ ordering ? "جاري إنشاء الطلب..." : "إتمام الطلب" }}
          </button>
        </div>

        <div v-if="cart.length===0" class="muted" style="margin-top:10px;">السلة فارغة.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="c in cart" :key="c.id" class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:center;">
              <div>
                <div style="font-weight:900;">{{ c.name }}</div>
                <div class="muted" style="font-size:12px;">{{ money(c.price) }}</div>
              </div>

              <div class="row">
                <button class="btn" @click="dec(c)">-</button>
                <span class="badge">{{ c.qty }}</span>
                <button class="btn" @click="inc(c)">+</button>
                <button class="btn btn-ghost" style="border-color: rgba(255,77,109,.4);" @click="remove(c)">حذف</button>
              </div>
            </div>
          </div>

          <div class="row" style="justify-content:space-between; margin-top:6px;">
            <div class="muted">الإجمالي</div>
            <div style="font-size:20px; font-weight:900;">{{ money(total) }}</div>
          </div>

          <div v-if="msg" class="muted" style="margin-top:8px;">{{ msg }}</div>
          <div v-if="orderErr" style="margin-top:8px; color:var(--danger); font-weight:800;">{{ orderErr }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../../lib/api";

const loading = ref(false);
const err = ref("");
const items = ref([]);
const view = ref([]);

const q = ref("");
const cart = ref([]);

const ordering = ref(false);
const msg = ref("");
const orderErr = ref("");

function money(v){
  const n = Number(v || 0);
  return `${n.toLocaleString("ar")} ر.ي`;
}

function filter(){
  const s = q.value.trim().toLowerCase();
  view.value = !s ? items.value : items.value.filter(p =>
    (p.name || "").toLowerCase().includes(s) ||
    (p.vendor_name || "").toLowerCase().includes(s)
  );
}

function add(p){
  const found = cart.value.find(x => x.id === p.id);
  if (found) found.qty += 1;
  else cart.value.push({ id: p.id, name: p.name, price: p.price, qty: 1 });
}

function inc(c){ c.qty += 1; }
function dec(c){ c.qty = Math.max(1, c.qty - 1); }
function remove(c){ cart.value = cart.value.filter(x => x.id !== c.id); }

const total = computed(() => cart.value.reduce((a,x)=> a + (Number(x.price||0)*x.qty), 0));

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/products");
    items.value = res.data?.items || res.data || [];

    // fallback لو API ما رجع شي
    if (!Array.isArray(items.value)) items.value = [];
    filter();
  }catch(e){
    err.value = e?.message || "تعذر جلب المنتجات (API غير جاهز؟)";
    items.value = [];
    view.value = [];
  }finally{
    loading.value = false;
  }
}

async function checkout(){
  ordering.value = true;
  msg.value = "";
  orderErr.value = "";
  try{
    // payload عام (عدله لاحقًا حسب endpoint الحقيقي)
    const payload = {
      items: cart.value.map(x => ({ product_id: x.id, qty: x.qty })),
    };
    const res = await api.post("/orders", payload);
    msg.value = "تم إنشاء الطلب ✅";
    cart.value = [];
  }catch(e){
    orderErr.value = e?.message || "فشل إنشاء الطلب";
  }finally{
    ordering.value = false;
  }
}

onMounted(reload);
</script>
