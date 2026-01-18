<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin:0 auto;">
        <div style="display:flex; gap:14px; align-items:center;">
          <div style="width:44px; height:44px; border-radius:14px; background:var(--ink);"></div>
          <div>
            <h1 class="h1">تسجيل الدخول</h1>
            <div class="muted">ادخل بريدك — بنرسل لك كود OTP</div>
          </div>
        </div>

        <div style="margin-top:18px;">
          <label class="muted">البريد الإلكتروني</label>
          <input class="input" v-model.trim="email" placeholder="name@email.com" inputmode="email" />
        </div>

        <div v-if="err" style="margin-top:12px; color:#b00020; font-weight:700;">
          {{ err }}
        </div>

        <div style="display:flex; gap:12px; margin-top:16px;">
          <button class="btn btn-primary" :disabled="loading" @click="sendOtp" style="flex:1; opacity:1;">
            {{ loading ? "جاري الإرسال..." : "إرسال الكود" }}
          </button>
          <button class="btn btn-ghost" @click="goRolePick">اختيار الدور</button>
        </div>

        <div class="muted" style="margin-top:14px; font-size:13px;">
          بتنفع لنفس الصفحة “تسجيل حساب” تلقائيًا عند أول دخول (Supabase).
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { supabase } from "../../lib/supabase";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref("");
const loading = ref(false);
const err = ref("");

async function sendOtp(){
  err.value = "";
  const e = email.value;
  if(!e || !e.includes("@")){
    err.value = "ادخل بريد صحيح.";
    return;
  }

  loading.value = true;
  try{
    // Email OTP (كود)
    const { error } = await supabase.auth.signInWithOtp({
      email: e,
      options: { shouldCreateUser: true }
    });
    if(error) throw error;

    localStorage.setItem("markai_email", e);
    router.push("/auth/verify");
  }catch(ex){
    err.value = ex?.message || "صار خطأ أثناء الإرسال.";
  }finally{
    loading.value = false;
  }
}

function goRolePick(){
  router.push("/role");
}
</script>
