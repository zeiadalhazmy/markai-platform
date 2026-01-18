<template>
  <div class="section">
    <div class="container">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
        <div>
          <h1 class="h1">لوحة الإدارة (Admin)</h1>
          <div class="muted">إدارة المستخدمين — المنتجات — الطلبات — التقارير</div>
        </div>
        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>

      <div class="grid2" style="margin-top:16px;">
        <div class="card" style="padding:18px;">
          <h2 class="h2">التحكم بالمنتجات</h2>
          <div class="muted">إضافة/حذف/مراجعة.</div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">الطلبات</h2>
          <div class="muted">عرض/تحديث الحالات/المشاكل.</div>
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
