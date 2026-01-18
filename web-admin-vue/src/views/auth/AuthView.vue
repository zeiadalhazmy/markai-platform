<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin: 0 auto;">
        <h1 class="h1">تسجيل الدخول</h1>
        <div class="muted">أدخل رقمك أو إيميلك — بنرسل لك كود OTP</div>

        <div style="margin-top:14px;">
          <input class="input" v-model="identity" placeholder="رقم هاتف أو بريد إلكتروني" />
        </div>

        <div class="row" style="margin-top:12px;">
          <button class="btn btn-primary" :disabled="loading || !identity" @click="sendOtp">
            {{ loading ? "جاري الإرسال..." : "إرسال الكود" }}
          </button>
          <span class="muted" v-if="msg">{{ msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../../lib/supabase";

const router = useRouter();
const identity = ref("");
const loading = ref(false);
const msg = ref("");

function isEmail(v){ return /\S+@\S+\.\S+/.test(v); }

async function sendOtp(){
  loading.value = true;
  msg.value = "";
  try{
    const v = identity.value.trim();

    const payload = isEmail(v)
      ? { email: v, options: { shouldCreateUser: true } }
      : { phone: v, options: { shouldCreateUser: true, channel: "sms" } };

    const { error } = await supabase.auth.signInWithOtp(payload);
    if (error) throw error;

    sessionStorage.setItem("otp_identity", v);
    msg.value = "تم إرسال الكود ✅";
    router.push("/auth/verify");
  }catch(e){
    msg.value = e?.message || "حصل خطأ";
  }finally{
    loading.value = false;
  }
}
</script>
