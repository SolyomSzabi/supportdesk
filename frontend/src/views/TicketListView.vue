<script setup lang="ts">
import { onMounted, reactive, ref, watch } from "vue";

import { fetchTickets } from "../api/client";
import type { Page, Ticket } from "../api/types";
import { STATUS_LABELS } from "../api/types";
import TicketBadge from "../components/TicketBadge.vue";
import { useSession } from "../session";

const { isAgent } = useSession();

const filters = reactive({
  status: "",
  priority: "",
  category: "",
  search: "",
  ordering: "-priority_rank,created_at",
});
const page = ref(1);
const data = ref<Page<Ticket> | null>(null);
const loading = ref(false);
const error = ref("");

const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    data.value = await fetchTickets({ ...filters, page: String(page.value) });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Could not load tickets.";
  } finally {
    loading.value = false;
  }
};

// Typing in the search box shouldn't fire a request per keystroke.
let searchTimer: ReturnType<typeof setTimeout> | undefined;
watch(
  () => ({ ...filters }),
  (current, previous) => {
    page.value = 1;
    clearTimeout(searchTimer);
    const delay = current.search !== previous.search ? 300 : 0;
    searchTimer = setTimeout(load, delay);
  },
);
watch(page, load);
onMounted(load);

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
</script>

<template>
  <div class="header">
    <h1>{{ isAgent ? "All tickets" : "Your tickets" }}</h1>
    <RouterLink v-if="!isAgent" to="/tickets/new"><button type="button">New ticket</button></RouterLink>
  </div>

  <div class="filters card">
    <input v-model="filters.search" type="search" placeholder="Search title or description" aria-label="Search" />
    <select v-model="filters.status" aria-label="Status">
      <option value="">Any status</option>
      <option v-for="(label, value) in STATUS_LABELS" :key="value" :value="value">{{ label }}</option>
    </select>
    <select v-model="filters.priority" aria-label="Priority">
      <option value="">Any priority</option>
      <option value="urgent">Urgent</option>
      <option value="high">High</option>
      <option value="medium">Medium</option>
      <option value="low">Low</option>
    </select>
    <select v-model="filters.category" aria-label="Category">
      <option value="">Any category</option>
      <option value="billing">Billing</option>
      <option value="technical">Technical</option>
      <option value="account">Account</option>
      <option value="other">Other</option>
    </select>
    <select v-model="filters.ordering" aria-label="Sort by">
      <option value="-priority_rank,created_at">Most urgent</option>
      <option value="-created_at">Newest</option>
      <option value="created_at">Oldest</option>
    </select>
  </div>

  <p v-if="error" class="error">{{ error }}</p>
  <p v-else-if="data && data.count === 0" class="muted empty">No tickets match these filters.</p>

  <ul v-if="data" class="list" :class="{ dim: loading }">
    <li v-for="ticket in data.results" :key="ticket.id">
      <RouterLink :to="`/tickets/${ticket.id}`" class="row card">
        <div class="main">
          <div class="title">
            <span class="id">#{{ ticket.id }}</span> {{ ticket.title }}
          </div>
          <p v-if="ticket.ai_summary" class="summary">
            <span class="ai-tag">AI</span> {{ ticket.ai_summary }}
          </p>
          <div class="meta muted">
            {{ ticket.company }} · {{ ticket.created_by }} · {{ formatDate(ticket.created_at) }}
            <span v-if="ticket.replies.length">
              · {{ ticket.replies.length }} {{ ticket.replies.length === 1 ? "reply" : "replies" }}</span
            >
          </div>
        </div>
        <div class="badges">
          <TicketBadge kind="priority" :value="ticket.priority" />
          <TicketBadge kind="status" :value="ticket.status" :label="STATUS_LABELS[ticket.status]" />
          <TicketBadge kind="category" :value="ticket.category" />
        </div>
      </RouterLink>
    </li>
  </ul>

  <div v-if="data && (data.next || data.previous)" class="pager">
    <button class="ghost" type="button" :disabled="!data.previous" @click="page--">Previous</button>
    <span class="muted">Page {{ page }}</span>
    <button class="ghost" type="button" :disabled="!data.next" @click="page++">Next</button>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.header h1 {
  margin: 0;
}
.filters {
  display: grid;
  grid-template-columns: 2fr repeat(4, 1fr);
  gap: 8px;
  padding: 12px;
  margin-bottom: 16px;
}
@media (max-width: 760px) {
  .filters {
    grid-template-columns: 1fr 1fr;
  }
  .filters input {
    grid-column: 1 / -1;
  }
}
.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
  transition: opacity 0.15s;
}
.list.dim {
  opacity: 0.6;
}
.row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  color: inherit;
  text-decoration: none;
}
.row:hover {
  border-color: var(--accent);
}
.main {
  min-width: 0;
}
.title {
  font-weight: 600;
}
.id {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.summary {
  margin: 6px 0;
  font-size: 14px;
}
.ai-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--ai-bg);
  color: var(--ai);
}
.meta {
  font-size: 13px;
  margin-top: 4px;
}
.badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}
.empty {
  text-align: center;
  padding: 32px 0;
}
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}
</style>
