<template>
  <div class="dashboard fade-up">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard de Sueño</h1>
        <p class="page-sub">Monitoreo biométrico en tiempo real · NeuroBand IoT</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-ghost" @click="reload">↺ Recargar</button>
        <button class="btn btn-ghost" @click="store.clearData()">✕ Limpiar</button>
      </div>
    </div>

    <!-- Sleep quality banner -->
    <div
      v-if="store.sleepQuality"
      class="sleep-banner"
      :class="`banner-${store.sleepQuality.level}`"
    >
      <div class="banner-left">
        <div class="banner-icon">{{ bannerIcon }}</div>
        <div>
          <div class="banner-title">{{ store.sleepQuality.label }}</div>
          <div class="banner-sub">Puntuación compuesta basada en los 3 sensores</div>
        </div>
      </div>
      <div class="banner-score mono">
        {{ store.sleepScore }}<span class="banner-unit">/100</span>
      </div>
    </div>

    <!-- KPI row -->
    <div class="g4 kpi-row">
      <div class="card kpi mpu-border">
        <div class="kpi-label">Movimiento</div>
        <div class="kpi-val mpu-col mono">
          {{ store.latestMpu?.accelMagnitude?.toFixed(3) ?? '—' }}
          <span class="kpi-unit">g</span>
        </div>
        <div class="kpi-status">
          <span class="badge" :class="movBadge">{{ store.latestMpu?.movementLevel ?? '—' }}</span>
        </div>
      </div>

      <div class="card kpi hr-border">
        <div class="kpi-label">Ritmo Cardíaco</div>
        <div class="kpi-val hr-col mono">
          {{ store.latestMax?.heartRate?.toFixed(1) ?? '—' }}
          <span class="kpi-unit">bpm</span>
        </div>
        <div class="kpi-status">
          <span class="badge" :class="hrBadge">{{ hrLabel }}</span>
        </div>
      </div>

      <div class="card kpi spo2-border">
        <div class="kpi-label">SpO₂</div>
        <div class="kpi-val spo2-col mono">
          {{ store.latestMax?.spo2?.toFixed(1) ?? '—' }}
          <span class="kpi-unit">%</span>
        </div>
        <div class="kpi-status">
          <span class="badge" :class="spo2Badge">{{ spo2Label }}</span>
        </div>
      </div>

      <div class="card kpi ldr-border">
        <div class="kpi-label">Luz Ambiental</div>
        <div class="kpi-val ldr-col mono">
          {{ store.latestLdr?.luxPercent?.toFixed(1) ?? '—' }}
          <span class="kpi-unit">%</span>
        </div>
        <div class="kpi-status">
          <span class="badge" :class="lightBadge">{{ lightLabel }}</span>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-col">
      <div class="card chart-card">
        <SensorChart
          :data="store.mpu"
          value-key="accelMagnitude"
          title="Movimiento — Magnitud de Aceleración"
          subtitle="Umbral de sueño: < 0.15g quieto · 0.15–0.50g leve · > 0.50g activo"
          line-color="#38bdf8"
          unit="g"
          :height="260"
          :thresholds="mpuThresholds"
        />
      </div>

      <div class="g2">
        <div class="card chart-card">
          <SensorChart
            :data="store.max"
            value-key="heartRate"
            value-key2="spo2"
            title="Ritmo Cardíaco y SpO₂"
            subtitle="FC normal sueño: 40–60 bpm · SpO₂ saludable: ≥ 95%"
            line-color="#f472b6"
            line-color2="#a78bfa"
            label2="SpO₂ (%)"
            unit=""
            :height="240"
            :thresholds="hrThresholds"
          />
        </div>
        <div class="card chart-card">
          <SensorChart
            :data="store.ldr"
            value-key="luxPercent"
            title="Luz Ambiental"
            subtitle="Umbral ideal sueño: < 5% · > 30% interrumpe melatonina"
            line-color="#fbbf24"
            unit="%"
            :height="240"
            :thresholds="ldrThresholds"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNeuroBandStore } from '@/stores/neuroBandStore'
import SensorChart from '@/components/SensorChart.vue'

const store = useNeuroBandStore()

async function reload() {
  store.clearData()
  await store.loadHistorical()
}

// ── Threshold definitions ─────────────────────────────────────
const mpuThresholds = [
  { label: 'ACTIVO', max: 0.5, color: '#f87171', range: '> 0.50g' },
  { label: 'LEVE', max: 0.15, color: '#f59e0b', range: '0.15–0.50g', min: 0 },
  { label: 'QUIETO', max: 0, color: '#34d399', range: '< 0.15g' },
]
const hrThresholds = [
  { label: 'DESPIERTO', max: 200, min: 80, color: '#f87171', range: '> 80 bpm' },
  { label: 'SUEÑO PROF.', max: 60, min: 40, color: '#34d399', range: '40–60 bpm' },
  { label: 'SpO₂ CRÍTICO', max: 90, color: '#f87171', range: '< 90%' },
  { label: 'SpO₂ SANO', max: 95, color: '#34d399', range: '≥ 95%' },
]
const ldrThresholds = [
  { label: 'BRILLANTE', max: 100, min: 30, color: '#f87171', range: '> 30%' },
  { label: 'TENUE', max: 30, min: 5, color: '#f59e0b', range: '5–30%' },
  { label: 'IDEAL', max: 5, color: '#34d399', range: '< 5%' },
]

// ── Badge helpers ─────────────────────────────────────────────
const movBadge = computed(() => {
  const m = store.latestMpu?.movementLevel
  if (m === 'STILL') return 'badge-good'
  if (m === 'LIGHT') return 'badge-warn'
  if (m === 'ACTIVE') return 'badge-danger'
  return 'badge-dim'
})

const hrLabel = computed(() => {
  const m = { DEEP_SLEEP: 'Sueño prof.', RESTING: 'En reposo', AWAKE: 'Despierto' }
  return m[store.latestMax?.hrStatus] ?? '—'
})
const hrBadge = computed(() => {
  const m = store.latestMax?.hrStatus
  if (m === 'DEEP_SLEEP') return 'badge-good'
  if (m === 'RESTING') return 'badge-warn'
  if (m === 'AWAKE') return 'badge-danger'
  return 'badge-dim'
})

const spo2Label = computed(() => {
  const m = { HEALTHY: 'Saludable', MILD_HYPOXIA: 'Hipoxia leve', CRITICAL: 'Crítico' }
  return m[store.latestMax?.spo2Status] ?? '—'
})
const spo2Badge = computed(() => {
  const m = store.latestMax?.spo2Status
  if (m === 'HEALTHY') return 'badge-good'
  if (m === 'MILD_HYPOXIA') return 'badge-warn'
  if (m === 'CRITICAL') return 'badge-danger'
  return 'badge-dim'
})

const lightLabel = computed(() => {
  const m = { IDEAL: 'Oscuridad ideal', DIM: 'Luz tenue', BRIGHT: 'Muy iluminado' }
  return m[store.latestLdr?.lightStatus] ?? '—'
})
const lightBadge = computed(() => {
  const m = store.latestLdr?.lightStatus
  if (m === 'IDEAL') return 'badge-good'
  if (m === 'DIM') return 'badge-warn'
  if (m === 'BRIGHT') return 'badge-danger'
  return 'badge-dim'
})

const bannerIcon = computed(() => {
  const l = store.sleepQuality?.level
  if (l === 'good') return '🌙'
  if (l === 'warn') return '😴'
  return '⚠️'
})
</script>

<style scoped>
.dashboard {
  max-width: 1240px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text);
}
.page-sub {
  font-size: 0.875rem;
  color: var(--text-sub);
  margin-top: 0.2rem;
}
.header-actions {
  display: flex;
  gap: 0.6rem;
}

/* Sleep quality banner */
.sleep-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.4rem;
  border-radius: var(--radius);
  margin-bottom: 1.5rem;
  border: 1px solid;
}
.banner-good {
  background: rgba(52, 211, 153, 0.06);
  border-color: rgba(52, 211, 153, 0.25);
}
.banner-warn {
  background: rgba(245, 158, 11, 0.06);
  border-color: rgba(245, 158, 11, 0.25);
}
.banner-danger {
  background: rgba(248, 113, 113, 0.06);
  border-color: rgba(248, 113, 113, 0.25);
}
.banner-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.banner-icon {
  font-size: 2rem;
}
.banner-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}
.banner-sub {
  font-size: 0.78rem;
  color: var(--text-sub);
  margin-top: 0.15rem;
}
.banner-score {
  font-size: 2.2rem;
  font-weight: 500;
  color: var(--text);
}
.banner-unit {
  font-size: 1rem;
  color: var(--text-sub);
}

/* KPI row */
.kpi-row {
  margin-bottom: 1.5rem;
}
.kpi {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.kpi-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
}
.kpi-val {
  font-size: 1.7rem;
  font-weight: 500;
}
.kpi-unit {
  font-size: 0.85rem;
  color: var(--text-sub);
  margin-left: 0.2rem;
}
.kpi-status {
  margin-top: 0.25rem;
}

/* Charts */
.charts-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.chart-card {
  padding: 1rem;
}
</style>
