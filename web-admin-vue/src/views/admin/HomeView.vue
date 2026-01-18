<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <h2 class="h2">لوحة الإدارة</h2>
        <div class="muted">إدارة عامة (ستكمل لاحقًا: مستخدمين/تجار/طلبات)</div>

        <div class="grid3" style="margin-top:14px;">
          <div class="card" style="padding:14px; background: var(--panel2);">
            <div class="muted">إجمالي الطلبات</div>
            <div style="font-size:26px; font-weight:900;">{{ kpi.orders }}</div>
          </div>
          <div class="card" style="padding:14px; background: var(--panel2);">
            <div class="muted">إجمالي التجار</div>
            <div style="font-size:26px; font-weight:900;">{{ kpi.merchants }}</div>
          </div>
          <div class="card" style="padding:14px; background: var(--panel2);">
            <div class="muted">إجمالي المندوبين</div>
            <div style="font-size:26px; font-weight:900;">{{ kpi.couriers }}</div>
          </div>
        </div>

        <div class="row" style="margin-top:12px; flex-wrap:wrap;">
          <button class="btn" @click="reload" :disabled="loading">تحديث</button>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { api } from "../../lib/api";

const loading = ref(false);
const err = ref("");
const kpi = ref({ orders: 0, merchants: 0, couriers: 0 });

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    // إذا عندك endpoint واحد للـ KPI استخدمه
    const res = await api.get("/admin/kpi");
    const d = res.data || {};
    kpi.value.orders = d.orders || 0;
    kpi.value.merchants = d.merchants || 0;
    kpi.value.couriers = d.couriers || 0;
  }catch(e){
    // fallback لو ما فيه endpoint الآن
    err.value = e?.message || "لا يوجد KPI endpoint بعد";
    kpi.value = { orders: 0, merchants: 0, couriers: 0 };
  }finally{
    loading.value = false;
  }
}

onMounted(reload);
</script>
