<template>
  <div
    class="skeleton-group"
    :class="[`skeleton-variant-${variant}`]"
  >
    <!-- RECT (default) -->
    <template v-if="variant === 'rect'">
      <div
        v-for="n in count"
        :key="n"
        class="skeleton"
        :style="{ height, width, borderRadius: rounded }"
      />
    </template>

    <!-- CIRCLE -->
    <template v-else-if="variant === 'circle'">
      <div
        v-for="n in count"
        :key="n"
        class="skeleton skeleton-circle"
        :style="{ width: height, height }"
      />
    </template>

    <!-- TEXT - multiple lines with staggered widths -->
    <template v-else-if="variant === 'text'">
      <div
        v-for="n in count"
        :key="n"
        class="skeleton skeleton-text-line"
        :style="{ width: textLineWidth(n), height: '14px' }"
      />
    </template>

    <!-- CARD - a card-shaped skeleton with header + lines -->
    <template v-else-if="variant === 'card'">
      <div
        v-for="n in count"
        :key="n"
        class="skeleton-card-shell"
      >
        <div
          class="skeleton skeleton-card-header"
          :style="{ height: '140px' }"
        />
        <div class="skeleton-card-body">
          <div
            class="skeleton"
            style="height: 16px; width: 60%"
          />
          <div
            class="skeleton"
            style="height: 12px; width: 90%"
          />
          <div
            class="skeleton"
            style="height: 12px; width: 75%"
          />
        </div>
      </div>
    </template>

    <!-- STAT - mini card with icon circle + value + label -->
    <template v-else-if="variant === 'stat'">
      <div
        v-for="n in count"
        :key="n"
        class="skeleton-stat-shell"
      >
        <div
          class="skeleton skeleton-circle"
          style="width: 40px; height: 40px; flex-shrink: 0"
        />
        <div class="skeleton-stat-lines">
          <div
            class="skeleton"
            style="height: 20px; width: 50%"
          />
          <div
            class="skeleton"
            style="height: 12px; width: 80%"
          />
        </div>
      </div>
    </template>

    <!-- TABLE - table rows with columns -->
    <template v-else-if="variant === 'table'">
      <div class="skeleton-table-shell">
        <div class="skeleton-table-header">
          <div
            v-for="c in 4"
            :key="c"
            class="skeleton"
            :style="{ height: '14px', width: c === 1 ? '30%' : '18%' }"
          />
        </div>
        <div
          v-for="n in count"
          :key="n"
          class="skeleton-table-row"
        >
          <div
            v-for="c in 4"
            :key="c"
            class="skeleton"
            :style="{ height: '12px', width: c === 1 ? '35%' : randomWidth(c + n) }"
          />
        </div>
      </div>
    </template>

    <!-- CHART - chart area with axis hints -->
    <template v-else-if="variant === 'chart'">
      <div
        class="skeleton-chart-shell"
        :style="{ height }"
      >
        <div class="skeleton-chart-y-axis">
          <div
            v-for="n in 4"
            :key="n"
            class="skeleton"
            style="height: 10px; width: 28px"
          />
        </div>
        <div class="skeleton-chart-area">
          <div class="skeleton-chart-bars">
            <div
              v-for="n in 8"
              :key="n"
              class="skeleton skeleton-chart-bar"
              :style="{ height: barHeight(n) }"
            />
          </div>
          <div class="skeleton-chart-x-axis">
            <div
              v-for="n in 8"
              :key="n"
              class="skeleton"
              style="height: 10px; width: 24px"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- HERO - hero image skeleton -->
    <template v-else-if="variant === 'hero'">
      <div
        class="skeleton skeleton-hero"
        :style="{ height: height || '280px' }"
      >
        <div class="skeleton-hero-content">
          <div
            class="skeleton"
            style="height: 12px; width: 100px; border-radius: 10px"
          />
          <div
            class="skeleton"
            style="height: 28px; width: 220px; margin-top: 12px"
          />
          <div
            class="skeleton"
            style="height: 14px; width: 160px; margin-top: 8px"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type Variant = 'rect' | 'circle' | 'text' | 'card' | 'stat' | 'table' | 'chart' | 'hero'

withDefaults(defineProps<{
  count?: number
  height?: string
  width?: string
  variant?: Variant
  rounded?: string
}>(), {
  count: 1,
  height: '20px',
  width: '100%',
  variant: 'rect',
  rounded: undefined,
})

function textLineWidth(n: number): string {
  const widths = ['100%', '85%', '65%', '90%', '70%']
  return widths[(n - 1) % widths.length]
}

function randomWidth(seed: number): string {
  const widths = ['20%', '15%', '22%', '18%']
  return widths[seed % widths.length]
}

function barHeight(n: number): string {
  const heights = [45, 70, 55, 85, 60, 90, 40, 75]
  return heights[(n - 1) % heights.length] + '%'
}
</script>

<style scoped>
.skeleton-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Circle variant */
.skeleton-circle {
  border-radius: 50% !important;
}

/* Text lines */
.skeleton-text-line {
  border-radius: 4px !important;
}

/* Card variant */
.skeleton-card-shell {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border);
}

.skeleton-card-header {
  border-radius: 0 !important;
}

.skeleton-card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}

/* Stat variant */
.skeleton-stat-shell {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: var(--radius);
  background: var(--bg-surface);
  border: 1px solid var(--border);
}

.skeleton-stat-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

/* Table variant */
.skeleton-table-shell {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border);
}

.skeleton-table-header {
  display: flex;
  gap: 16px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
}

.skeleton-table-row {
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
}

.skeleton-table-row:last-child {
  border-bottom: none;
}

/* Chart variant */
.skeleton-chart-shell {
  display: flex;
  gap: 8px;
  padding: 20px;
  border-radius: var(--radius);
  background: var(--bg-surface);
  border: 1px solid var(--border);
}

.skeleton-chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4px 0;
}

.skeleton-chart-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.skeleton-chart-bar {
  flex: 1;
  border-radius: 3px 3px 0 0 !important;
  min-height: 10px;
}

.skeleton-chart-x-axis {
  display: flex;
  justify-content: space-around;
}

/* Hero variant */
.skeleton-hero {
  border-radius: var(--radius);
  position: relative;
  display: flex;
  align-items: flex-end;
}

.skeleton-hero-content {
  padding: 28px 24px;
}

.skeleton-hero-content .skeleton {
  background: rgba(255, 255, 255, 0.08);
}
</style>
