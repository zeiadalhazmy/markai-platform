<template>
  <div class="section">
    <div class="container">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
        <div>
          <h1 class="h1">الرئيسية (مندوب)</h1>
          <div class="muted">المهام — الاستلام — التسليم — تحديث الحالة</div>
        </div>
        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>

      <div class="grid2" style="margin-top:16px;">
        <div class="card" style="padding:18px;">
          <h2 class="h2">مهامي اليوم</h2>
          <div class="muted">قائمة التوصيلات الموكلة لك.</div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">تحديث حالة الطلب</h2>
          <div class="muted">picked / on_the_way / delivered ...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { supabase } from "../../lib/supabase";
import { useRouter } from "vue-router";
const router = useRouter();

async function logout(){
  await supabase.auth.signOut();
  router.push("/auth");
}
</script>
