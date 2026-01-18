<template>
  <div class="section">
    <div class="container">
      <div class="grid2">
        <div class="card" style="padding:18px;">
          <h2 class="h2">لوحة المندوب</h2>
          <div class="muted">استلام المهام وتتبع التسليم</div>

          <div class="row" style="margin-top:12px; flex-wrap:wrap;">
            <router-link class="btn btn-primary" to="/courier/tasks">المهام</router-link>
          </div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">مؤشرات</h2>
          <div class="grid2" style="margin-top:12px;">
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">قيد التنفيذ</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.active }}</div>
            </div>
            <div class="card" style="padding:14px; background: var(--panel2);">
              <div class="muted">تم التسليم</div>
              <div style="font-size:26px; font-weight:900;">{{ kpi.done }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="padding:18px; margin-top:14px;">
        <h2 class="h2">أحدث المهام</h2>
        <div class="muted">عرض سريع</div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div v-if="!loading && tasks.length===0" class="muted" style="margin-top:10px;">لا توجد مهام.</div>

        <div v-else style="margin-top:12px; display:grid; gap:10px;">
          <div v-for="t in tasks" :key="t.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
              <div>
                <div style="font-weight:900;">مهمة #{{ t.id }}</div>
                <div class="muted" style="font-size:12px;">{{ t.address || "—" }}</div>
              </div>
              <span class="badge">{{ t.status || "—" }}</span>
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
const tasks = ref([]);
const kpi = ref({ active: 0, done: 0 });

async function load(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/courier/tasks?limit=5");
    tasks.value = res.data?.items || res.data || [];
    const all = tasks.value;
    kpi.value.active = all.filter(x => ["assigned","picked","onway"].includes(x.status)).length;
    kpi.value.done = all.filter(x => x.status === "done").length;
  }catch(e){
    err.value = e?.message || "تعذر جلب البيانات";
    tasks.value = [];
    kpi.value = { active: 0, done: 0 };
  }finally{
    loading.value = false;
  }
}

onMounted(load);
</script>
