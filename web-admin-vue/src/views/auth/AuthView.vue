<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin:0 auto;">
        <h1 class="h1">تسجيل الدخول</h1>
        <div class="muted">OTP عبر Supabase</div>

        <div class="row" style="margin-top:14px;">
          <button class="btn" :class="{ 'btn-primary': mode==='phone' }" @click="mode='phone'">هاتف</button>
          <button class="btn" :class="{ 'btn-primary': mode==='email' }" @click="mode='email'">إيميل</button>
        </div>

        <div style="margin-top:12px;">
          <div class="muted" v-if="mode==='phone'">رقم الهاتف (مثال: +9677xxxxxxx)</div>
          <div class="muted" v-else>البريد الإلكتروني</div>

          <input class="input" v-model="value" :placeholder="mode==='phone' ? '+9677...' : 'name@email.com'" />
        </div>

        <div class="row" style="margin-top:12px;">
          <button class="btn btn-primary" :disabled="loading" @click="sendOtp">
            {{ loading ? "جاري الإرسال..." : "إرسال الكود" }}
          </button>
          <router-link class="btn btn-ghost" to="/">الرئيسية</router-link>
        </div>

        <div class="muted" v-if="msg" style="margin-top:10px;">{{ msg }}</div>
        <div class="muted" v-if="err" style="margin-top:10px; color: var(--danger);">{{ err }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../../lib/supabase";

const router = useRouter();

const mode = ref("phone"); // phone | email
const value = ref("");
const loading = ref(false);
const msg = ref("");
const err = ref("");

async function sendOtp(){
  loading.value = true;
  msg.value = "";
  err.value = "";
  try{
    const v = value.value.trim();
    if (!v) throw new Error("أدخل القيمة أولاً");

    if (mode.value === "phone") {
      sessionStorage.setItem("otp_mode", "phone");
      sessionStorage.setItem("otp_value", v);
      const { error } = await supabase.auth.signInWithOtp({ phone: v });
      if (error) throw error;
    } else {
      sessionStorage.setItem("otp_mode", "email");
      sessionStorage.setItem("otp_value", v);
      const { error } = await supabase.auth.signInWithOtp({ email: v });
      if (error) throw error;
    }

    msg.value = "تم إرسال الكود ✅";
    router.push("/auth/verify");
  }catch(e){
    err.value = e?.message || "فشل إرسال الكود";
  }finally{
    loading.value = false;
  }
}
</script>
