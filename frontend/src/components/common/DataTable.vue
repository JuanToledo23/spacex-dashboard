<template>
  <div class="table-wrap">
    <div class="table-scroll">
      <table class="data-table">
        <thead class="dt-head">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in rows"
            :key="row.id || row[columns[0]?.key]"
            :class="{ 'row-clickable': clickable }"
            @click="clickable && $emit('row-click', row)"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              :data-label="col.label"
            >
              <slot
                :name="col.key"
                :row="row"
                :value="row[col.key]"
              >
                {{ row[col.key] ?? '—' }}
              </slot>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td
              :colspan="columns.length"
              class="empty-row"
            >
              <span class="empty-text">NO DATA</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <nav
      v-if="totalPages > 1"
      class="pagination"
      aria-label="Table pagination"
    >
      <button
        :disabled="page <= 1"
        aria-label="Previous page"
        @click="$emit('page-change', page - 1)"
      >
        PREV
      </button>
      <span
        class="page-info"
        aria-live="polite"
      >
        <span class="page-current">{{ page }}</span> / {{ totalPages }}
      </span>
      <button
        :disabled="page >= totalPages"
        aria-label="Next page"
        @click="$emit('page-change', page + 1)"
      >
        NEXT
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TableColumn } from '@/types'

const props = withDefaults(defineProps<{
  columns: TableColumn[]
  rows: Record<string, unknown>[]
  total?: number
  page?: number
  limit?: number
  clickable?: boolean
}>(), {
  total: 0,
  page: 1,
  limit: 20,
  clickable: false,
})

defineEmits<{
  'page-change': [page: number]
  'row-click': [row: Record<string, unknown>]
}>()

const totalPages = computed(() => Math.ceil(props.total / props.limit))
</script>

<style scoped>
.table-wrap {
  overflow: hidden;
}

.table-scroll {
  overflow-x: auto;
}

.empty-row {
  text-align: center;
  padding: 36px 16px !important;
}

.empty-text {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.page-info {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

.page-current {
  color: var(--accent);
  font-weight: 500;
}

.pagination {
  padding: 10px 14px;
}

.row-clickable {
  cursor: pointer;
  transition: background 0.12s;
}

.row-clickable:hover {
  background: var(--bg-hover);
}

@media (max-width: 768px) {
  .pagination button { min-height: 44px; min-width: 44px; padding: 8px 16px; }
  .data-table th { font-size: 0.68rem; padding: 6px 8px; }
  .data-table td { padding: 8px; font-size: 0.82rem; }
}

@media (max-width: 640px) {
  .dt-head { display: none; }

  .data-table,
  .data-table tbody,
  .data-table tr,
  .data-table td {
    display: block;
    width: 100%;
  }

  .data-table tr {
    background: var(--bg-surface);
    border-radius: var(--radius);
    padding: 12px 14px;
    margin-bottom: 8px;
    border: 1px solid var(--border);
  }

  .data-table tr:last-child {
    margin-bottom: 0;
  }

  .data-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: none;
    font-size: 0.85rem;
  }

  .data-table td::before {
    content: attr(data-label);
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    flex-shrink: 0;
    margin-right: 12px;
  }

  .data-table td:first-child {
    font-weight: 600;
    color: var(--text);
    font-size: 0.9rem;
  }

  .table-scroll {
    overflow-x: visible;
  }
}
</style>
