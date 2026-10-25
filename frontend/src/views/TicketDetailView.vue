<script setup lang="ts">
import { onMounted, ref } from "vue";

import { ApiError, fetchTicket, sendReply, suggestReply, updateStatus } from "../api/client";
import type { Status, Ticket } from "../api/types";
import { STATUS_LABELS } from "../api/types";
import TicketBadge from "../components/TicketBadge.vue";
import { useSession } from "../session";

const props = defineProps<{ id: string }>();
const { isAgent } = useSession();

const ticket = ref<Ticket | null>(null);
const loadError = ref("");
const replyBody = ref("");
const sending = ref(false);
const suggesting = ref(false);
const replyError = ref("");
const draftIsFromAi = ref(false);

const load = async () => {
  try {
    ticket.value = await fetchTicket(Number(props.id));
  } catch (err) {
    loadError.value =
      err instanceof ApiError && err.status === 404
        ? "This ticket does not exist or belongs to another company."
        : "Could not load the ticket.";
  }
};
onMounted(load);

const changeStatus = async (event: Event) => {
  if (!ticket.value) return;
  const status = (event.target as HTMLSelectElement).value as Status;
  ticket.value = await updateStatus(ticket.value.id, status);
};

// The AI draft only fills the textarea. The agent reviews and edits it, then sends.
const askAi = async () => {
  if (!ticket.value) return;
  suggesting.value = true;
  replyError.value = "";
  try {
    const { draft } = await suggestReply(ticket.value.id);
    replyBody.value = draft;
    draftIsFromAi.value = true;
  } catch (err) {
    replyError.value = err instanceof Error ? err.message : "AI suggestion failed.";
  } finally {
    suggesting.value = false;
  }
};

const submitReply = async () => {
  if (!ticket.value || !replyBody.value.trim()) return;
  sending.value = true;
  replyError.value = "";
  try {
    const reply = await sendReply(ticket.value.id, replyBody.value);
    ticket.value.replies.push(reply);
    replyBody.value = "";
    draftIsFromAi.value = false;
  } catch (err) {
    replyError.value = err instanceof Error ? err.message : "Could not send the reply.";
  } finally {
    sending.value = false;
  }
};

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
</script>

<template>
  <RouterLink to="/" class="back">← Back to tickets</RouterLink>

  <p v-if="loadError" class="error">{{ loadError }}</p>

  <template v-else-if="ticket">
    <div class="head">
      <h1><span class="id">#{{ ticket.id }}</span> {{ ticket.title }}</h1>
      <div class="badges">
        <TicketBadge kind="priority" :value="ticket.priority" />
        <TicketBadge kind="category" :value="ticket.category" />
        <select v-if="isAgent" :value="ticket.status" aria-label="Status" class="status" @change="changeStatus">
          <option v-for="(label, value) in STATUS_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
        <TicketBadge v-else kind="status" :value="ticket.status" :label="STATUS_LABELS[ticket.status]" />
      </div>
    </div>
    <p class="muted">{{ ticket.company }} · opened by {{ ticket.created_by }} · {{ formatDate(ticket.created_at) }}</p>

    <section v-if="ticket.ai_summary" class="ai-box">
      <strong>AI summary</strong>
      <p>{{ ticket.ai_summary }}</p>
    </section>

    <section class="card message">
      <div class="author">{{ ticket.created_by }}</div>
      <p class="body">{{ ticket.description }}</p>
    </section>

    <section v-for="reply in ticket.replies" :key="reply.id" class="card message">
      <div class="author">
        {{ reply.author }} <span class="muted">· {{ formatDate(reply.created_at) }}</span>
      </div>
      <p class="body">{{ reply.body }}</p>
    </section>

    <form class="card reply" @submit.prevent="submitReply">
      <div class="reply-head">
        <label for="reply">Your reply</label>
        <button v-if="isAgent" type="button" class="ai" :disabled="suggesting" @click="askAi">
          {{ suggesting ? "Writing draft…" : "✨ Suggest reply with AI" }}
        </button>
      </div>
      <textarea id="reply" v-model="replyBody" rows="6" @input="draftIsFromAi = false" />
      <p v-if="draftIsFromAi" class="muted">AI draft. Check the facts and edit it before sending.</p>
      <button type="submit" :disabled="sending || !replyBody.trim()">
        {{ sending ? "Sending…" : "Send reply" }}
      </button>
      <p v-if="replyError" class="error">{{ replyError }}</p>
    </form>
  </template>
</template>

<style scoped>
.back {
  display: inline-block;
  margin-bottom: 12px;
  font-size: 14px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.head h1 {
  margin: 0;
}
.id {
  color: var(--text-muted);
}
.badges {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status {
  width: auto;
  padding: 4px 8px;
}
.ai-box {
  background: var(--ai-bg);
  border: 1px solid #ddd2fc;
  border-radius: 10px;
  padding: 12px 16px;
  margin: 16px 0;
  color: #3b2a7a;
}
.ai-box p {
  margin: 4px 0 0;
}
.message {
  margin-bottom: 8px;
  padding: 14px 16px;
}
.author {
  font-weight: 600;
  font-size: 14px;
}
.body {
  white-space: pre-wrap;
  margin: 6px 0 0;
}
.reply {
  margin-top: 16px;
}
.reply-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.reply textarea {
  margin-bottom: 8px;
}
</style>
