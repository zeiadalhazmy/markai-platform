<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">طلباتي</h2>
            <div class="muted">تابع الحالة والتحديثات</div>
          </div>

          <div class="row" style="flex-wrap:wrap;">
            <select class="input" style="width:220px;" v-model="status" @change="apply">
              <option value="">كل الحالات</option>
              <option value="pending">قيد الانتظار</option>
              <option value="processing">قيد المعالجة</option>
              <option value="shipped">تم الشحن</option>
              <option value="done">مكتمل</option>
              <option value="canceled">ملغي</option>
            </select>
            <button class="btn" @click="reload" :disabled="loading">تحديث</button>
          </div>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div v-if="!loading && view.length===0" class="muted" style="margin-top:12px;">لا توجد طلبات.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="o in view" :key="o.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">طلب #{{ o.id }}</div>
                <div class="muted" style="font-size:12px;">{{ formatDate(o.created_at) }}</div>
              </div>
              <span class="badge">{{ statusLabel(o.status) }}</span>
            </div>

            <div class="row" style="justify-content:space-between; margin-top:10px; flex-wrap:wrap;">
              <div class="muted">الإجمالي: <b>{{ money(o.total) }}</b></div>
              <button class="btn btn-ghost" @click="toggle(o.id)">تفاصيل</button>
            </div>

            <div v-if="openId === o.id" class="card" style="padding:12px; margin-top:10px; background: var(--panel2);">
              <div class="muted" v-if="!o.items || o.items.length===0">لا يوجد عناصر مفصلة.</div>
              <div v-else style="display:grid; gap:8px;">
                <div v-for="it in o.items" :key="it.product_id" class="row" style="justify-content:space-between;">
                  <div class="muted">{{ it.name || ("منتج " + it.product_id) }}</div>
                  <div class="badge">x{{ it.qty }}</div>
                </div>
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
const view = ref([]);
const status = ref("");
const openId = ref(null);

function toggle(id){ openId.value = (openId.value === id ? null : id); }

function statusLabel(s){
  if (s === "pending") return "قيد الانتظار";
  if (s === "processing") return "قيد المعالجة";
  if (s === "shipped") return "تم الشحن";
  if (s === "done") return "مكتمل";
  if (s === "canceled") return "ملغي";
  return s || "—";
}
function formatDate(v){ try { return new Date(v).toLocaleString("ar"); } catch { return v; } }
function money(v){
  const n = Number(v || 0);
  return `${n.toLocaleString("ar")} ر.ي`;
}

function apply(){
  view.value = status.value ? items.value.filter(o => o.status === status.value) : items.value;
}

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/orders");
    items.value = res.data?.items || res.data || [];
    if (!Array.isArray(items.value)) items.value = [];
    apply();
  }catch(e){
    err.value = e?.message || "تعذر جلب الطلبات (API غير جاهز؟)";
    items.value = [];
    view.value = [];
  }finally{
    loading.value = false;
  }
}

onMounted(reload);
</script>
