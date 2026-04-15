<template>
  <div class="sensor-page fade-up">
    <div class="page-header">
      <div>
        <span class="badge badge-dim" style="color: var(--c-mpu); border-color: var(--c-mpu)"
          >MPU6050</span
        >
        <h1 class="page-title mpu-col">Sensor de Movimiento</h1>
        <p class="page-sub mono">
          Acelerómetro y giroscopio 6 ejes · Detección de agitación durante el sueño
        </p>
      </div>
      <div class="page-stats">
        <div class="stat">
          <div class="sv mpu-col mono">{{ store.countMpu }}</div>
          <div class="sl">registros</div>
        </div>
        <div class="stat">
          <div class="sv mono">{{ avgMag }}</div>
          <div class="sl">mag. prom.</div>
        </div>
        <div class="stat">
          <div class="sv mono" :class="dominantMovColor">{{ dominantMov }}</div>
          <div class="sl">estado dominante</div>
        </div>
      </div>
    </div>

    <!-- Threshold explanation cards -->
    <div class="g3 threshold-cards">
      <div class="card th-card th-good">
        <div class="th-icon">😴</div>
        <div class="th-name">QUIETO</div>
        <div class="th-range mono">mag &lt; 0.15 g</div>
        <div class="th-desc">
          Sueño profundo · Sin movimiento · Estado ideal para la recuperación
        </div>
      </div>
      <div class="card th-card th-warn">
        <div class="th-icon">🌀</div>
        <div class="th-name">LEVE</div>
        <div class="th-range mono">0.15 – 0.50 g</div>
        <div class="th-desc">Movimiento leve · Posible fase REM · Sueño ligero</div>
      </div>
      <div class="card th-card th-danger">
        <div class="th-icon">🚨</div>
        <div class="th-name">ACTIVO</div>
        <div class="th-range mono">mag &gt; 0.50 g</div>
        <div class="th-desc">Agitación severa · Usuario posiblemente despierto</div>
      </div>
    </div>

    <!-- Main magnitude chart -->
    <div class="card">
      <SensorChart
        :data="store.mpu"
        value-key="accelMagnitude"
        title="Magnitud de Aceleración en el tiempo"
        subtitle="Eje Y = |accel| en g-force · Eje X = registro"
        line-color="#38bdf8"
        unit="g"
        :height="300"
        :thresholds="mpuThresholds"
      />
    </div>

    <!-- Axis charts -->
    <div class="g3">
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="accelX"
          title="Aceleración X"
          subtitle="eje lateral"
          line-color="#38bdf8"
          unit="g"
          :height="180"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="accelY"
          title="Aceleración Y"
          subtitle="eje longitudinal"
          line-color="#67e8f9"
          unit="g"
          :height="180"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="accelZ"
          title="Aceleración Z"
          subtitle="eje vertical"
          line-color="#a5f3fc"
          unit="g"
          :height="180"
        />
      </div>
    </div>

    <!-- Gyroscope charts -->
    <div class="g3">
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="gyroX"
          title="Giro X"
          subtitle="°/s"
          line-color="#7dd3fc"
          unit="°/s"
          :height="160"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="gyroY"
          title="Giro Y"
          subtitle="°/s"
          line-color="#bae6fd"
          unit="°/s"
          :height="160"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.mpu"
          value-key="gyroZ"
          title="Giro Z"
          subtitle="°/s"
          line-color="#e0f2fe"
          unit="°/s"
          :height="160"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNeuroBandStore } from '@/stores/neuroBandStore'
import SensorChart from '@/components/SensorChart.vue'

const store = useNeuroBandStore()

const avgMag = computed(() => {
  if (!store.mpu.length) return '—'
  const avg = store.mpu.reduce((a, d) => a + d.accelMagnitude, 0) / store.mpu.length
  return avg.toFixed(4) + ' g'
})

const movCounts = computed(() => {
  const c = { STILL: 0, LIGHT: 0, ACTIVE: 0 }
  store.mpu.forEach((d) => {
    if (c[d.movementLevel] !== undefined) c[d.movementLevel]++
  })
  return c
})

const dominantMov = computed(() => {
  const c = movCounts.value
  return Object.entries(c).sort((a, b) => b[1] - a[1])[0]?.[0] ?? '—'
})

const dominantMovColor = computed(() => {
  if (dominantMov.value === 'STILL') return 'good-col'
  if (dominantMov.value === 'LIGHT') return 'warn-col'
  if (dominantMov.value === 'ACTIVE') return 'danger-col'
  return ''
})

const mpuThresholds = [
  { label: 'ACTIVO', max: 0.5, color: '#f87171', range: '> 0.50g' },
  { label: 'LEVE', max: 0.15, min: 0, color: '#f59e0b', range: '0.15–0.50g' },
]
</script>

<style scoped>
.sensor-page {
  max-width: 1200px;
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
  margin: 0.3rem 0;
}
.page-sub {
  font-size: 0.8rem;
  color: var(--text-sub);
}
.page-stats {
  display: flex;
  gap: 1.5rem;
}
.stat {
  text-align: center;
}
.sv {
  font-size: 1.4rem;
  font-weight: 600;
}
.sl {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
}

.threshold-cards {
  margin-bottom: 1.25rem;
}
.th-card {
  text-align: center;
  padding: 1.25rem;
  border-width: 1px;
}
.th-good {
  border-color: rgba(52, 211, 153, 0.3) !important;
}
.th-warn {
  border-color: rgba(245, 158, 11, 0.3) !important;
}
.th-danger {
  border-color: rgba(248, 113, 113, 0.3) !important;
}
.th-icon {
  font-size: 1.8rem;
  margin-bottom: 0.4rem;
}
.th-name {
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.th-good .th-name {
  color: var(--c-good);
}
.th-warn .th-name {
  color: var(--c-warn);
}
.th-danger .th-name {
  color: var(--c-danger);
}
.th-range {
  font-size: 0.78rem;
  color: var(--text-sub);
  margin-bottom: 0.5rem;
}
.th-desc {
  font-size: 0.75rem;
  color: var(--text-dim);
  line-height: 1.5;
}

.card {
  margin-bottom: 1.25rem;
}
.g3 {
  gap: 1rem;
  margin-bottom: 1.25rem;
}
</style>
