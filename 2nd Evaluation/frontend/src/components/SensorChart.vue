<template>
  <div class="chart-wrapper">
    <div class="chart-top">
      <div class="chart-meta">
        <span class="chart-title">{{ title }}</span>
        <span class="chart-sub mono">{{ subtitle }}</span>
      </div>
      <div class="chart-stats">
        <span class="cs-item">
          <span class="cs-val mono" :style="{ color: lineColor }">{{ data.length }}</span> registros
        </span>
        <span v-if="latestVal !== null" class="cs-item">
          Último: <span class="cs-val mono" :style="{ color: lineColor }">{{ latestVal }}</span>
        </span>
      </div>
    </div>

    <!-- Threshold legend -->
    <div v-if="thresholds.length" class="threshold-legend">
      <div v-for="t in thresholds" :key="t.label" class="tl-item">
        <span class="tl-dot" :style="{ background: t.color }"></span>
        <span class="tl-label" :style="{ color: t.color }">{{ t.label }}</span>
        <span class="mono tl-range">{{ t.range }}</span>
      </div>
    </div>

    <!-- Chart canvas -->
    <div class="chart-body" :style="{ height: height + 'px' }">
      <canvas ref="canvasRef"></canvas>
      <div v-if="data.length === 0" class="chart-empty">
        <div class="empty-glyph">◉</div>
        <div>Esperando datos del ESP32...</div>
        <div class="empty-sub">
          El sensor <strong>{{ title }}</strong> enviará datos en tiempo real
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
)

const props = defineProps({
  data: { type: Array, default: () => [] },
  valueKey: { type: String, required: true }, // which field to plot
  title: { type: String, default: 'Sensor' },
  subtitle: { type: String, default: '' },
  lineColor: { type: String, default: '#38bdf8' },
  height: { type: Number, default: 300 },
  unit: { type: String, default: '' },
  // Threshold bands: [{ label, min, max, color, range }]
  thresholds: { type: Array, default: () => [] },
  // Second line (e.g., SpO2 alongside HR)
  valueKey2: { type: String, default: null },
  lineColor2: { type: String, default: '#a78bfa' },
  label2: { type: String, default: '' },
})

const canvasRef = ref(null)
let chart = null

const latestVal = computed(() => {
  if (!props.data.length) return null
  const v = props.data.at(-1)?.[props.valueKey]
  return v != null ? `${Number(v).toFixed(2)} ${props.unit}` : null
})

// ── Chart.js threshold lines plugin ─────────────────────────
const thresholdPlugin = {
  id: 'thresholdBands',
  beforeDraw(ch) {
    if (!props.thresholds.length) return
    const { ctx, chartArea, scales } = ch
    const yScale = scales.y
    if (!yScale) return

    ctx.save()
    props.thresholds.forEach((t) => {
      // Horizontal threshold line at t.max (upper bound)
      if (t.max !== undefined) {
        const y = yScale.getPixelForValue(t.max)
        if (y >= chartArea.top && y <= chartArea.bottom) {
          ctx.beginPath()
          ctx.strokeStyle = t.color
          ctx.lineWidth = 1
          ctx.setLineDash([6, 4])
          ctx.globalAlpha = 0.55
          ctx.moveTo(chartArea.left, y)
          ctx.lineTo(chartArea.right, y)
          ctx.stroke()

          // Label on the right
          ctx.globalAlpha = 0.8
          ctx.fillStyle = t.color
          ctx.font = "10px 'DM Mono'"
          ctx.textAlign = 'right'
          ctx.fillText(t.label, chartArea.right - 4, y - 4)
        }
      }
      // Shaded band between min and max
      if (t.min !== undefined && t.max !== undefined) {
        const y1 = yScale.getPixelForValue(t.max)
        const y2 = yScale.getPixelForValue(t.min)
        ctx.globalAlpha = 0.04
        ctx.fillStyle = t.color
        ctx.fillRect(chartArea.left, Math.min(y1, y2), chartArea.width, Math.abs(y2 - y1))
      }
    })
    ctx.restore()
  },
}

function buildChart() {
  if (!canvasRef.value) return
  if (chart) {
    chart.destroy()
    chart = null
  }

  const datasets = [
    {
      label: props.title,
      data: [],
      borderColor: props.lineColor,
      backgroundColor: hexRgba(props.lineColor, 0.07),
      borderWidth: 1.8,
      pointRadius: 0,
      pointHoverRadius: 4,
      fill: true,
      tension: 0.35,
    },
  ]

  if (props.valueKey2) {
    datasets.push({
      label: props.label2 || props.valueKey2,
      data: [],
      borderColor: props.lineColor2,
      backgroundColor: 'transparent',
      borderWidth: 1.4,
      pointRadius: 0,
      fill: false,
      tension: 0.35,
      borderDash: [5, 3],
    })
  }

  const GRID = 'rgba(255,255,255,0.04)'
  const TICKS = '#3d5470'

  chart = new Chart(canvasRef.value.getContext('2d'), {
    type: 'line',
    data: { labels: [], datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: !!props.valueKey2,
          labels: { color: TICKS, font: { family: "'DM Mono'", size: 11 } },
        },
        tooltip: {
          backgroundColor: '#0b1220',
          borderColor: 'rgba(56,189,248,0.2)',
          borderWidth: 1,
          titleColor: '#e2eeff',
          bodyColor: '#7f96b8',
          titleFont: { family: "'DM Mono'" },
          bodyFont: { family: "'DM Mono'" },
          callbacks: {
            label: (item) => ` ${item.dataset.label}: ${Number(item.raw).toFixed(3)} ${props.unit}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: TICKS, font: { family: "'DM Mono'", size: 9 }, maxTicksLimit: 10 },
          grid: { color: GRID },
        },
        y: {
          ticks: { color: TICKS, font: { family: "'DM Mono'", size: 9 } },
          grid: { color: GRID },
        },
      },
    },
    plugins: [thresholdPlugin],
  })
}

function updateChart() {
  if (!chart) return
  const labels = props.data.map((_, i) => i + 1)
  chart.data.labels = labels
  chart.data.datasets[0].data = props.data.map((d) => d[props.valueKey])
  if (props.valueKey2 && chart.data.datasets[1]) {
    chart.data.datasets[1].data = props.data.map((d) => d[props.valueKey2])
  }
  chart.update('none')
}

onMounted(async () => {
  await nextTick()
  buildChart()
  updateChart()
})
watch(
  () => props.data.length,
  () => updateChart(),
)
onUnmounted(() => {
  if (chart) chart.destroy()
})

function hexRgba(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${a})`
}
</script>

<style scoped>
.chart-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chart-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.chart-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text);
  display: block;
}
.chart-sub {
  font-size: 0.7rem;
  color: var(--text-dim);
  display: block;
  margin-top: 2px;
}

.chart-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}
.cs-item {
  font-size: 0.75rem;
  color: var(--text-sub);
}
.cs-val {
  font-size: 0.85rem;
  font-weight: 500;
}

/* Threshold legend */
.threshold-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}
.tl-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.tl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tl-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.tl-range {
  font-size: 0.68rem;
  color: var(--text-dim);
}

.chart-body {
  position: relative;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.chart-body canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-dim);
  font-size: 0.875rem;
}
.empty-glyph {
  font-size: 2.5rem;
  opacity: 0.15;
}
.empty-sub {
  font-size: 0.75rem;
  color: var(--text-dim);
}
</style>
