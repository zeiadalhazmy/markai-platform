<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin:0 auto;">
        <h1 class="h1">تأكيد الكود</h1>
        <div class="muted">ادخل الكود المرسل إلى: <b>{{ email }}</b></div>

        <div style="margin-top:16px;">
          <label class="muted">كود OTP</label>
          <input class="input" v-model.trim="token" placeholder="مثال: 123456" inputmode="numeric" />
        </div>

        <div v-if="err" style="margin-top:12px; color:#b00020; font-weight:700;">
          {{ err }}
        </div>

        <div style="display:flex; gap:12px; margin-top:16px;">
          <button class="btn btn-primary" :disabled="loading" @click="verify" style="flex:1;">
            {{ loading ? "جاري التحقق..." : "دخول" }}
          </button>
          <button class="btn btn-ghost" @click="back">رجوع</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { supabase } from "../../lib/supabase";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref("");
const token = ref("");
const loading = ref(false);
const err = ref("");

onMounted(() => {
  email.value = localStorage.getItem("markai_email") || "";
  if(!email.value) router.push("/auth");
});

async function verify(){
  err.value = "";
  if(token.value.length < 6){
    err.value = "الكود لازم 6 أرقام.";
    return;
  }

  loading.value = true;
  try{
    const { error } = await supabase.auth.verifyOtp({
      email: email.value,
      token: token.value,
      type: "email"
    });
    if(error) throw error;

    // بعد الدخول: روح لاختيار الدور أو للداشبورد حسب الموجود
    router.push("/role");
  }catch(ex){
    err.value = ex?.message || "الكود غير صحيح.";
  }finally{
    loading.value = false;
  }
}

function back(){ router.push("/auth"); }
</script>
