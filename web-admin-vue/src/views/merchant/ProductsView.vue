<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:18px;">
        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:end;">
          <div>
            <h2 class="h2">منتجاتي</h2>
            <div class="muted">إضافة/تعديل/حذف</div>
          </div>

          <div class="row" style="flex-wrap:wrap;">
            <button class="btn btn-primary" @click="openCreate">إضافة منتج</button>
            <button class="btn" @click="reload" :disabled="loading">تحديث</button>
          </div>
        </div>

        <div v-if="loading" class="muted" style="margin-top:10px;">جاري التحميل...</div>
        <div v-if="err" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ err }}</div>

        <div style="margin-top:14px; display:grid; gap:10px;">
          <div v-for="p in items" :key="p.id" class="card" style="padding:14px;">
            <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:center;">
              <div>
                <div style="font-weight:900;">{{ p.name }}</div>
                <div class="muted" style="font-size:12px;">{{ money(p.price) }}</div>
              </div>
              <div class="row" style="flex-wrap:wrap;">
                <button class="btn" @click="openEdit(p)">تعديل</button>
                <button class="btn btn-ghost" style="border-color: rgba(255,77,109,.4);" @click="del(p.id)">حذف</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!loading && items.length===0" class="muted" style="margin-top:12px;">لا توجد منتجات.</div>
      </div>

      <!-- Modal -->
      <div v-if="modal" class="overlay" @click.self="close">
        <div class="card modal">
          <h2 class="h2">{{ form.id ? "تعديل منتج" : "إضافة منتج" }}</h2>
          <div class="muted">املأ البيانات</div>

          <div style="margin-top:12px; display:grid; gap:10px;">
            <div>
              <div class="muted">اسم المنتج</div>
              <input class="input" v-model="form.name" />
            </div>
            <div>
              <div class="muted">السعر</div>
              <input class="input" v-model="form.price" type="number" />
            </div>
          </div>

          <div class="row" style="margin-top:12px; justify-content:space-between;">
            <button class="btn btn-ghost" @click="close">إلغاء</button>
            <button class="btn btn-primary" :disabled="saving" @click="save">
              {{ saving ? "جاري الحفظ..." : "حفظ" }}
            </button>
          </div>

          <div v-if="merr" style="margin-top:10px; color:var(--danger); font-weight:800;">{{ merr }}</div>
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

const modal = ref(false);
const saving = ref(false);
const merr = ref("");
const form = ref({ id: null, name: "", price: 0 });

function money(v){
  const n = Number(v || 0);
  return `${n.toLocaleString("ar")} ر.ي`;
}

function openCreate(){
  form.value = { id: null, name: "", price: 0 };
  merr.value = "";
  modal.value = true;
}
function openEdit(p){
  form.value = { id: p.id, name: p.name, price: p.price };
  merr.value = "";
  modal.value = true;
}
function close(){ modal.value = false; }

async function reload(){
  loading.value = true;
  err.value = "";
  try{
    const res = await api.get("/merchant/products");
    items.value = res.data?.items || res.data || [];
    if (!Array.isArray(items.value)) items.value = [];
  }catch(e){
    err.value = e?.message || "تعذر جلب المنتجات";
    items.value = [];
  }finally{
    loading.value = false;
  }
}

async function save(){
  saving.value = true;
  merr.value = "";
  try{
    const payload = { name: form.value.name, price: Number(form.value.price || 0) };
    if (!payload.name) throw new Error("اسم المنتج مطلوب");

    if (form.value.id) {
      await api.put(`/merchant/products/${form.value.id}`, payload);
    } else {
      await api.post("/merchant/products", payload);
    }
    modal.value = false;
    await reload();
  }catch(e){
    merr.value = e?.message || "فشل الحفظ";
  }finally{
    saving.value = false;
  }
}

async function del(id){
  if (!confirm("حذف المنتج؟")) return;
  try{
    await api.del(`/merchant/products/${id}`);
    await reload();
  }catch(e){
    alert(e?.message || "فشل الحذف");
  }
}

onMounted(reload);
</script>

<style scoped>
.overlay{
  position:fixed; inset:0;
  background: rgba(0,0,0,.55);
  display:flex; align-items:center; justify-content:center;
  padding: 18px;
  z-index: 50;
}
.modal{
  width: min(560px, 100%);
  padding: 18px;
}
</style>
