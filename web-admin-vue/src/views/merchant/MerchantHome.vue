<template>
  <div class="section">
    <div class="container">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
        <div>
          <h1 class="h1">الرئيسية (تاجر)</h1>
          <div class="muted">إدارة المنتجات — متابعة الطلبات — تحديث المخزون</div>
        </div>
        <button class="btn btn-ghost" @click="logout">خروج</button>
      </div>

      <div class="grid2" style="margin-top:16px;">
        <div class="card" style="padding:18px;">
          <h2 class="h2">منتجاتي</h2>
          <div class="muted">هنا بنعرض منتجات التاجر + إضافة/تعديل.</div>
        </div>

        <div class="card" style="padding:18px;">
          <h2 class="h2">طلبات المتجر</h2>
          <div class="muted">هنا بنعرض الطلبات القادمة للمتجر.</div>
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
