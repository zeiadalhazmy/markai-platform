<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin:0 auto;">
        <h1 class="h1">التحقق من الكود</h1>
        <div class="muted">أدخل OTP ثم متابعة</div>

        <div class="muted" style="margin-top:10px;">
          الإرسال إلى: <b>{{ target }}</b>
        </div>

        <div style="margin-top:12px;">
          <div class="muted">الكود</div>
          <input class="input" v-model="token" placeholder="123456" />
        </div>

        <div class="row" style="margin-top:12px;">
          <button class="btn btn-primary" :disabled="loading" @click="verify">
            {{ loading ? "جاري التحقق..." : "تأكيد" }}
          </button>
          <router-link class="btn btn-ghost" to="/auth">رجوع</router-link>
        </div>

        <div class="muted" v-if="err" style="margin-top:10px; color: var(--danger);">{{ err }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../../lib/supabase";
import { ensureProfileDefaultRole } from "../../lib/profile";

const router = useRouter();
const token = ref("");
const loading = ref(false);
const err = ref("");

const mode = sessionStorage.getItem("otp_mode") || "phone";
const value = sessionStorage.getItem("otp_value") || "";

const target = computed(() => value || "—");

async function verify(){
  loading.value = true;
  err.value = "";
  try{
    const t = token.value.trim();
    if (!t) throw new Error("أدخل الكود");

    if (mode === "phone") {
      const { error } = await supabase.auth.verifyOtp({
        phone: value,
        token: t,
        type: "sms",
      });
      if (error) throw error;
    } else {
      const { error } = await supabase.auth.verifyOtp({
        email: value,
        token: t,
        type: "email",
      });
      if (error) throw error;
    }

    await ensureProfileDefaultRole(); // يضمن role=customer لأول مرة
    router.replace("/auth/role");
  }catch(e){
    err.value = e?.message || "فشل التحقق";
  }finally{
    loading.value = false;
  }
}
</script>
