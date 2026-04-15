<template>
  <div class="tabla-view fade-up">
    <div class="page-header">
      <div>
        <h1 class="page-title">Registros de Datos</h1>
        <p class="page-sub">Historial completo de lecturas almacenadas en PostgreSQL</p>
      </div>
      <div class="tab-switcher">
        <button :class="['tab-btn', { active: tab === 'mpu' }]" @click="tab = 'mpu'">
          <span class="mpu-col">◈</span> Movimiento ({{ store.countMpu }})
        </button>
        <button :class="['tab-btn', { active: tab === 'max' }]" @click="tab = 'max'">
          <span class="hr-col">♥</span> Cardíaco ({{ store.countMax }})
        </button>
        <button :class="['tab-btn', { active: tab === 'ldr' }]" @click="tab = 'ldr'">
          <span class="ldr-col">◎</span> Luz ({{ store.countLdr }})
        </button>
      </div>
    </div>

    <!-- Summary stats for active tab -->
    <div class="g4 stats-row">
      <div class="card mini-stat">
        <div class="ms-label">Registros</div>
        <div class="ms-val mono" :style="{ color: activeColor }">{{ activeData.length }}</div>
      </div>
      <div class="card mini-stat">
        <div class="ms-label">Dispositivo</div>
        <div class="ms-val mono" style="font-size: 0.9rem">{{ deviceId }}</div>
      </div>
      <div class="card mini-stat">
        <div class="ms-label">{{ statLabel1 }}</div>
        <div class="ms-val mono" :style="{ color: activeColor }">{{ statVal1 }}</div>
      </div>
      <div class="card mini-stat">
        <div class="ms-label">{{ statLabel2 }}</div>
        <div class="ms-val mono">{{ statVal2 }}</div>
      </div>
    </div>

    <!-- Table -->
    <div class="card table-card">
      <div v-if="activeData.length === 0" class="empty-state">
        <div class="empty-icon">◉</div>
        <div>Sin registros aún para este sensor</div>
        <div class="empty-sub">Inicia el ESP32 para comenzar a recibir datos</div>
      </div>

      <!-- MPU6050 table -->
      <table v-else-if="tab === 'mpu'" class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Estado</th>
            <th>Magnitud (g)</th>
            <th>Accel X</th>
            <th>Accel Y</th>
            <th>Accel Z</th>
            <th>Giro X</th>
            <th>Giro Y</th>
            <th>Giro Z</th>
            <th>Dispositivo</th>
            <th>Registrado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in activeData" :key="row.id">
            <td class="mono accent-col">{{ row.id }}</td>
            <td>
              <span class="badge" :class="movBadge(row.movementLevel)">{{
                movLabel(row.movementLevel)
              }}</span>
            </td>
            <td class="mono" :class="movColor(row.movementLevel)">
              {{ row.accelMagnitude?.toFixed(4) }}
            </td>
            <td class="mono muted">{{ row.accelX?.toFixed(4) }}</td>
            <td class="mono muted">{{ row.accelY?.toFixed(4) }}</td>
            <td class="mono muted">{{ row.accelZ?.toFixed(4) }}</td>
            <td class="mono muted">{{ row.gyroX?.toFixed(3) }}</td>
            <td class="mono muted">{{ row.gyroY?.toFixed(3) }}</td>
            <td class="mono muted">{{ row.gyroZ?.toFixed(3) }}</td>
            <td class="muted small">{{ row.deviceId }}</td>
            <td class="mono muted small">{{ fmtTime(row.recordedAt) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- MAX30102 table -->
      <table v-else-if="tab === 'max'" class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Est. FC</th>
            <th>Est. SpO₂</th>
            <th>Frec. Cardíaca</th>
            <th>SpO₂ (%)</th>
            <th>IR Raw</th>
            <th>Red Raw</th>
            <th>Dispositivo</th>
            <th>Registrado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in activeData" :key="row.id">
            <td class="mono accent-col">{{ row.id }}</td>
            <td>
              <span class="badge" :class="hrBadge(row.hrStatus)">{{ hrLabel(row.hrStatus) }}</span>
            </td>
            <td>
              <span class="badge" :class="spo2Badge(row.spo2Status)">{{
                spo2Label(row.spo2Status)
              }}</span>
            </td>
            <td class="mono hr-col">{{ row.heartRate?.toFixed(1) }} bpm</td>
            <td class="mono spo2-col">{{ row.spo2?.toFixed(1) }}%</td>
            <td class="mono muted small">{{ row.irValue }}</td>
            <td class="mono muted small">{{ row.redValue }}</td>
            <td class="muted small">{{ row.deviceId }}</td>
            <td class="mono muted small">{{ fmtTime(row.recordedAt) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- LDR table -->
      <table v-else-if="tab === 'ldr'" class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Estado</th>
            <th>Luz (%)</th>
            <th>Voltaje (V)</th>
            <th>Dispositivo</th>
            <th>Registrado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in activeData" :key="row.id">
            <td class="mono accent-col">{{ row.id }}</td>
            <td>
              <span class="badge" :class="lightBadge(row.lightStatus)">{{
                lightLabel(row.lightStatus)
              }}</span>
            </td>
            <td class="mono ldr-col">{{ row.luxPercent?.toFixed(2) }}%</td>
            <td class="mono muted">{{ row.voltage?.toFixed(4) }}V</td>
            <td class="muted small">{{ row.deviceId }}</td>
            <td class="mono muted small">{{ fmtTime(row.recordedAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNeuroBandStore } from '@/stores/neuroBandStore'

const store = useNeuroBandStore()
const tab = ref('mpu')

const activeData = computed(() => {
  if (tab.value === 'mpu') return store.mpu
  if (tab.value === 'max') return store.max
  return store.ldr
})

const activeColor = computed(
  () =>
    ({
      mpu: 'var(--c-mpu)',
      max: 'var(--c-max-hr)',
      ldr: 'var(--c-ldr)',
    })[tab.value],
)

const deviceId = computed(() => activeData.value[0]?.deviceId ?? '—')

// Per-tab summary stats
const statLabel1 = computed(
  () => ({ mpu: 'Mag. promedio', max: 'FC promedio', ldr: 'Luz promedio' })[tab.value],
)
const statLabel2 = computed(
  () => ({ mpu: 'Mag. máxima', max: 'SpO₂ promedio', ldr: 'Voltaje promedio' })[tab.value],
)

const statVal1 = computed(() => {
  const d = activeData.value
  if (!d.length) return '—'
  if (tab.value === 'mpu')
    return (d.reduce((a, r) => a + r.accelMagnitude, 0) / d.length).toFixed(4) + ' g'
  if (tab.value === 'max')
    return (d.reduce((a, r) => a + r.heartRate, 0) / d.length).toFixed(1) + ' bpm'
  return (d.reduce((a, r) => a + r.luxPercent, 0) / d.length).toFixed(2) + '%'
})

const statVal2 = computed(() => {
  const d = activeData.value
  if (!d.length) return '—'
  if (tab.value === 'mpu') return Math.max(...d.map((r) => r.accelMagnitude)).toFixed(4) + ' g'
  if (tab.value === 'max') return (d.reduce((a, r) => a + r.spo2, 0) / d.length).toFixed(1) + '%'
  return (d.reduce((a, r) => a + r.voltage, 0) / d.length).toFixed(4) + ' V'
})

// ── Formatters ────────────────────────────────────────────────

function fmtTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString('es-BO', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// MPU
function movLabel(s) {
  return { STILL: 'Quieto', LIGHT: 'Leve', ACTIVE: 'Activo' }[s] ?? s
}
function movBadge(s) {
  return { STILL: 'badge-good', LIGHT: 'badge-warn', ACTIVE: 'badge-danger' }[s] ?? 'badge-dim'
}
function movColor(s) {
  return { STILL: 'good-col', LIGHT: 'warn-col', ACTIVE: 'danger-col' }[s] ?? ''
}

// MAX30102
function hrLabel(s) {
  return { DEEP_SLEEP: 'Sueño prof.', RESTING: 'Reposo', AWAKE: 'Despierto' }[s] ?? s
}
function hrBadge(s) {
  return (
    { DEEP_SLEEP: 'badge-good', RESTING: 'badge-warn', AWAKE: 'badge-danger' }[s] ?? 'badge-dim'
  )
}
function spo2Label(s) {
  return { HEALTHY: 'Saludable', MILD_HYPOXIA: 'Hipoxia leve', CRITICAL: 'Crítico' }[s] ?? s
}
function spo2Badge(s) {
  return (
    { HEALTHY: 'badge-good', MILD_HYPOXIA: 'badge-warn', CRITICAL: 'badge-danger' }[s] ??
    'badge-dim'
  )
}

// LDR
function lightLabel(s) {
  return { IDEAL: 'Ideal', DIM: 'Tenue', BRIGHT: 'Brillante' }[s] ?? s
}
function lightBadge(s) {
  return { IDEAL: 'badge-good', DIM: 'badge-warn', BRIGHT: 'badge-danger' }[s] ?? 'badge-dim'
}
</script>

<style scoped>
.tabla-view {
  max-width: 1300px;
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
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text);
}
.page-sub {
  font-size: 0.875rem;
  color: var(--text-sub);
  margin-top: 0.2rem;
}

.tab-switcher {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 1.1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-sub);
  font-family: var(--font-display);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}
.tab-btn:hover {
  color: var(--text);
  border-color: var(--border-hover);
}
.tab-btn.active {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.4);
  color: var(--text);
}

.stats-row {
  margin-bottom: 1.5rem;
}
.mini-stat {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.ms-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
}
.ms-val {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text);
}

.table-card {
  padding: 0;
  overflow-x: auto;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  color: var(--text-dim);
}
.empty-icon {
  font-size: 2.5rem;
  opacity: 0.15;
}
.empty-sub {
  font-size: 0.78rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th {
  text-align: left;
  padding: 0.65rem 1rem;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-dim);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.data-table td {
  padding: 0.6rem 1rem;
  font-size: 0.82rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  white-space: nowrap;
}
.data-table tr:last-child td {
  border-bottom: none;
}
.data-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.accent-col {
  color: var(--c-mpu);
  font-weight: 600;
}
.muted {
  color: var(--text-sub);
}
.small {
  font-size: 0.75rem;
}
.mono {
  font-family: var(--font-mono);
}
</style>
