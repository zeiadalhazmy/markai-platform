<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">طلبات المتجر</h2>
            <div class="muted">قبول/تجهيز/تسليم للمندوب</div>
          </div>
          <button class="btn" @click="reload" :disabled="loading">تحديث</button>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div v-if="!loading && items.length===0" class="muted" style="margin-top:12px;">لا توجد طلبات.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="o in items" :key="o.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">طلب #{{ o.id }}</div>
                <div class="muted" style="font-size:12px;">{{ formatDate(o.created_at) }}</div>
              </div>
              <span class="badge">{{ statusLabel(o.status) }}</span>
            </div>

            <div class="row" style="margin-top:10px; justify-content:space-between; flex-wrap:wrap;">
              <div class="muted">الإجمالي: <b>{{ money(o.total) }}</b></div>

              <div class="row" style="flex-wrap:wrap;">
                <button class="btn" @click="setStatus(o.id,'processing')">قبول</button>
                <button class="btn" @click="setStatus(o.id,'shipped')">جاهز للمندوب</button>
                <button class="btn btn-ghost" style="border-color: rgba(255,77,109,.4);" @click="setStatus(o.id,'canceled')">إلغاء</button>
              </div>
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
const items = ref([]);

function formatDate(v){ try { return new Date(v).toLocaleString("ar"); } catch { return v; } }
function money(v){ const n = Number(v||0); return `${n.toLocaleString("ar")} ر.ي`; }
function statusLabel(s){
  if (s === "pending") return "جديد";
  if (s === "processing") return "قيد التجهيز";
  if (s === "shipped") return "جاهز للمندوب";
  if (s === "done") return "مكتمل";
  if (s === "canceled") return "ملغي";
  return s || "—";
}

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/merchant/orders");
    items.value = res.data?.items || res.data || [];
    if (!Array.isArray(items.value)) items.value = [];
  }catch(e){
    err.value = e?.message || "تعذر جلب الطلبات";
    items.value = [];
  }finally{
    loading.value = false;
  }
}

async function setStatus(id, status){
  try{
    await api.put(`/merchant/orders/${id}/status`, { status });
    await reload();
  }catch(e){
    alert(e?.message || "فشل تحديث الحالة");
  }
}

onMounted(reload);
</script>
