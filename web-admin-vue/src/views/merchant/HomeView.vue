<template>
  <div class="section">
    <div class="container">
      <div class="grid2">
        <div class="card" style="padding:18px;">
          <h2 class="h2">لوحة التاجر</h2>
          <div class="muted">إدارة المنتجات والطلبات</div>

          <div class="row" style="margin-top:12px; flex-wrap:wrap;">
            <router-link class="btn btn-primary" to="/merchant/products">المنتجات</router-link>
            <router-link class="btn" to="/merchant/orders">الطلبات</router-link>
          </div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">مؤشرات</h2>
          <div class="grid2" style="margin-top:12px;">
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">طلبات جديدة</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.new }}</div>
            </div>
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">قيد التجهيز</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.processing }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="padding:18px; margin-top:14px;">
        <h2 class="h2">آخر الطلبات</h2>
        <div class="muted">عرض سريع</div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div v-if="!loading && orders.length===0" class="muted" style="margin-top:10px;">لا توجد طلبات.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="o in orders" :key="o.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">طلب #{{ o.id }}</div>
                <div class="muted" style="font-size:12px;">{{ formatDate(o.created_at) }}</div>
              </div>
              <span class="badge">{{ o.status || "—" }}</span>
            </div>
          </div>
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
const kpi = ref({ new: 0, processing: 0 });

function formatDate(v){ try { return new Date(v).toLocaleString("ar"); } catch { return v; } }

async function load(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/merchant/orders?limit=5");
    orders.value = res.data?.items || res.data || [];
    const all = orders.value;
    kpi.value.new = all.filter(x => x.status === "pending").length;
    kpi.value.processing = all.filter(x => x.status === "processing").length;
  }catch(e){
    err.value = e?.message || "تعذر جلب البيانات (API غير جاهز؟)";
    orders.value = [];
    kpi.value = { new: 0, processing: 0 };
  }finally{
    loading.value = false;
  }
}

onMounted(load);
</script>
