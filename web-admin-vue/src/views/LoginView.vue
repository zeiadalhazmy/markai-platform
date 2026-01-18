<template>
  <div style="max-width:420px;margin:60px auto;font-family:sans-serif">
    <h2>Login</h2>

    <form @submit.prevent="login">
      <div style="margin:10px 0">
        <input v-model="email" placeholder="Email" style="width:100%;padding:10px" />
      </div>
      <div style="margin:10px 0">
        <input v-model="password" type="password" placeholder="Password" style="width:100%;padding:10px" />
      </div>

      <button style="padding:10px 14px">Sign in</button>
    </form>

    <p v-if="error" style="color:red;margin-top:12px">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { supabase } from "../lib/supabase";

const router = useRouter();
const email = ref("");
const password = ref("");
const error = ref("");

async function login() {
  error.value = "";
  const { error: e } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  });

  if (e) {
    error.value = e.message;
    return;
  }

  router.push("/");
}
</script>
