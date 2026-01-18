<template>
  <div class="section">
    <div class="container">
      <div class="card" style="padding:22px; max-width:520px; margin: 0 auto;">
        <h1 class="h1">تأكيد الكود</h1>
        <div class="muted">أدخل كود OTP</div>

        <div style="margin-top:14px;">
          <input class="input" v-model="code" placeholder="مثال: 123456" />
        </div>

        <div class="row" style="margin-top:12px;">
          <button class="btn btn-primary" :disabled="loading || code.length < 4" @click="verify">
            {{ loading ? "جاري التحقق..." : "تأكيد" }}
          </button>
          <button class="btn" @click="back">رجوع</button>
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
import { getUserRole, ensureProfileDefaultRole } from "../../lib/profile";

const router = useRouter();
const code = ref("");
const loading = ref(false);
const msg = ref("");

function isEmail(v){ return /\S+@\S+\.\S+/.test(v); }

async function verify(){
  loading.value = true; msg.value = "";
  try{
    const identity = sessionStorage.getItem("otp_identity");
    if (!identity) throw new Error("ارجع أرسل الكود من جديد");

    const payload = isEmail(identity)
      ? { email: identity, token: code.value.trim(), type: "email" }
      : { phone: identity, token: code.value.trim(), type: "sms" };

    const { error } = await supabase.auth.verifyOtp(payload);
    if (error) throw error;

    await ensureProfileDefaultRole();
    const role = await getUserRole();

    // لو تبغاه يختار الدور أول مرة: ودّه لـ /auth/role
    // حالياً: نوجّه مباشرة حسب الدور الموجود
    if (role === "merchant") return router.replace("/merchant");
    if (role === "courier") return router.replace("/courier");
    if (role === "admin") return router.replace("/admin");
    return router.replace("/client");
  }catch(e){
    msg.value = e?.message || "حصل خطأ";
  }finally{
    loading.value = false;
  }
}

function back(){ router.push("/auth"); }
</script>
