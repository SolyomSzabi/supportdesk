<script setup lang="ts">
// Small colored pill for status, priority and category values.
defineProps<{ kind: "status" | "priority" | "category"; value: string; label?: string }>();
</script>

<template>
  <span v-if="value" class="badge" :class="`${kind}-${value}`">{{ label ?? value.replace("_", " ") }}</span>
  <span v-else class="badge badge-empty">—</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
  background: var(--surface-2);
  color: var(--text-muted);
}
.badge-empty {
  background: transparent;
}
.priority-urgent { background: #fde2e1; color: #a1251c; }
.priority-high { background: #fdebd3; color: #8a4b08; }
.priority-medium { background: #e3eefc; color: #1d4f91; }
.priority-low { background: #e6f4ea; color: #1e6b37; }
.status-open { background: #e3eefc; color: #1d4f91; }
.status-in_progress { background: #fdf3cf; color: #7a5a00; }
.status-resolved { background: #e6f4ea; color: #1e6b37; }
.status-closed { background: var(--surface-2); color: var(--text-muted); }
</style>
