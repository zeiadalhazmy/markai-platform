<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">المهام</h2>
            <div class="muted">استلام المهمة وتحديث حالتها</div>
          </div>
          <button class="btn" @click="reload" :disabled="loading">تحديث</button>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div v-if="!loading && items.length===0" class="muted" style="margin-top:12px;">لا توجد مهام.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="t in items" :key="t.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">مهمة #{{ t.id }}</div>
                <div class="muted" style="font-size:12px;">{{ t.address || "—" }}</div>
              </div>
              <span class="badge">{{ label(t.status) }}</span>
            </div>

            <div class="row" style="margin-top:10px; justify-content:space-between; flex-wrap:wrap;">
              <div class="muted">هاتف: <b>{{ t.phone || "—" }}</b></div>
              <div class="row" style="flex-wrap:wrap;">
                <button class="btn" @click="setStatus(t.id,'picked')">استلام</button>
                <button class="btn" @click="setStatus(t.id,'onway')">في الطريق</button>
                <button class="btn btn-primary" @click="setStatus(t.id,'done')">تم التسليم</button>
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

function label(s){
  if (s === "assigned") return "مسندة";
  if (s === "picked") return "تم الاستلام";
  if (s === "onway") return "في الطريق";
  if (s === "done") return "تم التسليم";
  return s || "—";
}

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/courier/tasks");
    items.value = res.data?.items || res.data || [];
    if (!Array.isArray(items.value)) items.value = [];
  }catch(e){
    err.value = e?.message || "تعذر جلب المهام";
    items.value = [];
  }finally{
    loading.value = false;
  }
}

async function setStatus(id, status){
  try{
    await api.put(`/courier/tasks/${id}/status`, { status });
    await reload();
  }catch(e){
    alert(e?.message || "فشل تحديث الحالة");
  }
}

onMounted(reload);
</script>

