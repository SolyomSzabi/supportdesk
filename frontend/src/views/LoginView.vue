<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { ApiError } from "../api/client";
import { useSession } from "../session";

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const { login } = useSession();
const router = useRouter();

const submit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await login(username.value, password.value);
    router.push({ name: "tickets" });
  } catch (err) {
    error.value =
      err instanceof ApiError && err.status === 401
        ? "Wrong username or password."
        : "Login failed. Is the backend running?";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login">
    <h1>SupportDesk <span>AI</span></h1>
    <p class="muted">B2B support portal with AI ticket triage.</p>
    <form class="card" @submit.prevent="submit">
      <div class="field">
        <label for="username">Username</label>
        <input id="username" v-model="username" autocomplete="username" required />
      </div>
      <div class="field">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>
      <button type="submit" :disabled="loading">{{ loading ? "Logging in…" : "Log in" }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<style scoped>
.login {
  max-width: 380px;
  margin: 64px auto 0;
}
h1 span {
  color: var(--accent);
}
.field {
  margin-bottom: 14px;
}
button {
  width: 100%;
}
</style>
