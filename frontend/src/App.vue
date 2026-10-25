<script setup lang="ts">
import { useRouter } from "vue-router";

import { useSession } from "./session";

const { me, isAgent, logout } = useSession();
const router = useRouter();

const signOut = () => {
  logout();
  router.push({ name: "login" });
};
</script>

<template>
  <header v-if="me" class="topbar">
    <RouterLink to="/" class="brand">SupportDesk <span>AI</span></RouterLink>
    <div class="who">
      <span>{{ me.first_name || me.username }}</span>
      <span class="role">{{ isAgent ? "Support agent" : me.company }}</span>
      <button class="ghost" type="button" @click="signOut">Log out</button>
    </div>
  </header>
  <main class="page">
    <RouterView />
  </main>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.brand {
  font-weight: 700;
  font-size: 18px;
  color: var(--text);
  text-decoration: none;
}
.brand span {
  color: var(--accent);
}
.who {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}
.role {
  color: var(--text-muted);
}
@media (max-width: 600px) {
  .role {
    display: none;
  }
}
</style>
