<template>
  <div class="section">
    <div class="container">
      <div class="grid2">
        <div class="card" style="padding:18px;">
          <h2 class="h2">مرحبا 👋</h2>
          <div class="muted">تصفح المنتجات واطلب بسهولة.</div>

          <div class="row" style="margin-top:12px; flex-wrap:wrap;">
            <router-link class="btn btn-primary" to="/client/products">تصفح المنتجات</router-link>
            <router-link class="btn" to="/client/orders">طلباتي</router-link>
          </div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">ملخص سريع</h2>
          <div class="muted">آخر التحديثات والطلبات.</div>

          <div class="grid2" style="margin-top:12px;">
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">طلبات قيد المعالجة</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.processing }}</div>
            </div>
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">طلبات مكتملة</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.done }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="padding:18px; margin-top:14px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">أحدث الطلبات</h2>
            <div class="muted">عرض آخر 5 طلبات</div>
          </div>
          <router-link class="btn btn-ghost" to="/client/orders">عرض الكل</router-link>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-else-if="orders.length===0" class="muted" style="margin-top:10px;">لا توجد طلبات بعد.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="o in orders" :key="o.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">طلب #{{ o.id }}</div>
                <div class="muted" style="font-size:12px;">{{ formatDate(o.created_at) }}</div>
              </div>
              <span class="badge">{{ statusLabel(o.status) }}</span>
            </div>
          </div>
        </div>

        <div v-if="err" style="margin-top:10px; color: var(--danger); font-weight:800;">
          {{ err }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { api } from "../../lib/api";

const loading = ref(false);
const err = ref("");
const orders = ref([]);
const kpi = ref({ processing: 0, done: 0 });

function statusLabel(s){
  if (s === "pending") return "قيد الانتظار";
  if (s === "processing") return "قيد المعالجة";
  if (s === "shipped") return "تم الشحن";
  if (s === "done") return "مكتمل";
  if (s === "canceled") return "ملغي";
  return s || "—";
}

function formatDate(v){
  try { return new Date(v).toLocaleString("ar"); } catch { return v; }
}

async function load(){
  loading.value = true;
  err.value = "";
  try{
    // لو API موجود
    const res = await api.get("/orders?limit=5");
    orders.value = res.data?.items || res.data || [];

    // KPI بسيط من نفس الداتا (إن ما فيه endpoint خاص)
    const all = orders.value;
    kpi.value.processing = all.filter(x => ["pending","processing","shipped"].includes(x.status)).length;
    kpi.value.done = all.filter(x => x.status === "done").length;
  }catch(e){
    // لو ما عندك API للطلبات الآن لا يكسر الصفحة
    err.value = e?.message || "تعذر جلب البيانات (API غير جاهز؟)";
    orders.value = [];
    kpi.value = { processing: 0, done: 0 };
  }finally{
    loading.value = false;
  }
}

onMounted(load);
</script>
