<template>
  <div class="container" style="max-width:520px;">
    <div class="card" style="padding:18px;">
      <h2 style="margin:0 0 6px;">تحقق OTP</h2>
      <p style="margin:0 0 16px; color:var(--muted);">
        أدخل الكود المرسل إلى: <b>{{ phone }}</b>
      </p>

      <label style="display:block; font-weight:700; margin:10px 0 6px;">الكود</label>
      <input class="input" v-model="token" placeholder="123456" />

      <button class="btn btn-teal" style="width:100%; margin-top:12px;" @click="verify" :disabled="loading">
        {{ loading ? "جار التحقق..." : "دخول" }}
      </button>

      <p v-if="err" style="margin:12px 0 0; color:#b91c1c;">{{ err }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { supabase } from "../lib/supabase";

const route = useRoute();
const router = useRouter();
const phone = ref(route.query.phone || "");
const token = ref("");
const loading = ref(false);
const err = ref("");

async function verify(){
  err.value = "";
  loading.value = true;
  try{
    const { error } = await supabase.auth.verifyOtp({
      phone: phone.value,
      token: token.value,
      type: "sms",
    });
    if(error) throw error;

    router.push("/"); // بنعمل ريداركت حسب Role بعد قليل
  }catch(e){
    err.value = e?.message || "فشل التحقق";
  }finally{
    loading.value = false;
  }
}
</script>
