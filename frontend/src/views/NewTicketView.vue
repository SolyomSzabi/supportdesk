<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { createTicket } from "../api/client";

const title = ref("");
const description = ref("");
const saving = ref(false);
const error = ref("");
const router = useRouter();

const submit = async () => {
  saving.value = true;
  error.value = "";
  try {
    const ticket = await createTicket(title.value, description.value);
    router.push(`/tickets/${ticket.id}`);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Could not create the ticket.";
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <RouterLink to="/" class="back">← Back to tickets</RouterLink>
  <h1>New ticket</h1>
  <form class="card" @submit.prevent="submit">
    <div class="field">
      <label for="title">Title</label>
      <input id="title" v-model="title" required minlength="5" maxlength="200" />
    </div>
    <div class="field">
      <label for="description">Describe the problem</label>
      <textarea id="description" v-model="description" rows="6" required />
    </div>
    <p class="muted">Category, priority and a short summary are filled in automatically by AI.</p>
    <button type="submit" :disabled="saving">
      {{ saving ? "Creating and analysing…" : "Create ticket" }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>

<style scoped>
.back {
  display: inline-block;
  margin-bottom: 12px;
  font-size: 14px;
}
.field {
  margin-bottom: 14px;
}
</style>
