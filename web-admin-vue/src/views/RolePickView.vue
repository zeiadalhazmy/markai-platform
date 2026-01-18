<template>
  <div class="section">
    <div class="container">
      <div class="grid2">
        <div class="card" style="padding:22px;">
          <h2 class="h2">اختَر دورك</h2>
          <div class="muted">هذا يحدد الصلاحيات والواجهات اللي بتظهر لك.</div>

          <div style="display:grid; gap:12px; margin-top:16px;">
            <button class="btn btn-dark" @click="pick('client')">عميل</button>
            <button class="btn btn-primary" @click="pick('merchant')">تاجر</button>
            <button class="btn btn-ghost" @click="pick('courier')">مندوب</button>
            <button class="btn btn-ghost" @click="pick('admin')">إدارة (Admin)</button>
          </div>

          <div v-if="err" style="margin-top:12px; color:#b00020; font-weight:700;">
            {{ err }}
          </div>
        </div>

        <div class="card" style="padding:22px;">
          <h2 class="h2">ملاحظات مهمة</h2>
          <ul class="muted" style="line-height:1.9; padding-right:18px;">
            <li>التحقق الحقيقي للصلاحيات لازم يكون في الـ Backend كمان.</li>
            <li>هنا بنحفظ الدور في Supabase (جدول profiles) لتحديد الواجهات.</li>
          </ul>
          <button class="btn btn-ghost" style="margin-top:10px;" @click="logout">تسجيل خروج</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { supabase } from "../lib/supabase";
import { useRouter } from "vue-router";

const router = useRouter();
const err = ref("");

async function pick(role){
  err.value = "";
  const { data } = await supabase.auth.getUser();
  const user = data?.user;
  if(!user){
    router.push("/auth");
    return;
  }

  // نحفظ الدور في جدول profiles (لازم يكون موجود في Supabase)
  const { error } = await supabase
    .from("profiles")
    .upsert({ id: user.id, role }, { onConflict: "id" });

  if(error){
    err.value = "تأكد من وجود جدول profiles في Supabase + صلاحيات RLS.";
    return;
  }

  // توجيه حسب الدور
  if(role === "client") router.push("/client");
  else if(role === "merchant") router.push("/merchant");
  else if(role === "courier") router.push("/courier");
  else router.push("/admin");
}

async function logout(){
  await supabase.auth.signOut();
  router.push("/auth");
}
</script>
