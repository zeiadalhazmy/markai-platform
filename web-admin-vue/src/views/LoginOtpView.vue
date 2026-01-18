<template>
  <div class="container" style="max-width:520px;">
    <div class="card" style="padding:18px;">
      <h2 style="margin:0 0 6px;">تسجيل الدخول</h2>
      <p style="margin:0 0 16px; color:var(--muted);">
        أدخل رقم الجوال لإرسال كود OTP
      </p>

      <label style="display:block; font-weight:700; margin:10px 0 6px;">رقم الجوال</label>
      <input class="input" v-model="phone" placeholder="+9677XXXXXXXX" />

      <button class="btn btn-primary" style="width:100%; margin-top:12px;" @click="sendOtp" :disabled="loading">
        {{ loading ? "جار الإرسال..." : "إرسال الكود" }}
      </button>

      <p v-if="msg" style="margin:12px 0 0; color:var(--muted);">{{ msg }}</p>
      <p v-if="err" style="margin:12px 0 0; color:#b91c1c;">{{ err }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../lib/supabase";

const router = useRouter();
const phone = ref("");
const loading = ref(false);
const msg = ref("");
const err = ref("");

async function sendOtp(){
  err.value = ""; msg.value = "";
  loading.value = true;
  try{
    const { error } = await supabase.auth.signInWithOtp({ phone: phone.value });
    if(error) throw error;
    msg.value = "تم إرسال الكود ✅";
    router.push({ path: "/verify-otp", query: { phone: phone.value } });
  }catch(e){
    err.value = e?.message || "فشل الإرسال";
  }finally{
    loading.value = false;
  }
}
</script>
