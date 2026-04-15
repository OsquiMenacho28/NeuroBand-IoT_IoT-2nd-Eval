<template>
  <div class="sensor-page fade-up">
    <div class="page-header">
      <div>
        <span class="badge badge-dim" style="color: var(--c-max-hr); border-color: var(--c-max-hr)"
          >MAX30102</span
        >
        <h1 class="page-title hr-col">Ritmo Cardíaco y SpO₂</h1>
        <p class="page-sub mono">
          Sensor óptico de pulso y oxígeno en sangre · Monitoreo de fases del sueño
        </p>
      </div>
      <div class="page-stats">
        <div class="stat">
          <div class="sv hr-col mono">{{ avgHr }}</div>
          <div class="sl">FC promedio</div>
        </div>
        <div class="stat">
          <div class="sv spo2-col mono">{{ avgSpo2 }}</div>
          <div class="sl">SpO₂ promedio</div>
        </div>
        <div class="stat">
          <div class="sv mono">{{ store.countMax }}</div>
          <div class="sl">registros</div>
        </div>
      </div>
    </div>

    <!-- Threshold explanation cards -->
    <div class="g3 threshold-cards">
      <div class="card th-card" style="border-color: rgba(52, 211, 153, 0.3)">
        <div class="th-icon">🌙</div>
        <div class="th-name" style="color: var(--c-good)">SUEÑO PROFUNDO</div>
        <div class="th-range mono">FC: 40–60 bpm · SpO₂: ≥ 95%</div>
        <div class="th-desc">
          Bradicardia normal durante sueño profundo · Máxima recuperación corporal
        </div>
      </div>
      <div class="card th-card" style="border-color: rgba(245, 158, 11, 0.3)">
        <div class="th-icon">💤</div>
        <div class="th-name" style="color: var(--c-warn)">EN REPOSO</div>
        <div class="th-range mono">FC: 60–80 bpm · SpO₂: 90–94%</div>
        <div class="th-desc">Sueño ligero o estado de relajación · Monitorear SpO₂</div>
      </div>
      <div class="card th-card" style="border-color: rgba(248, 113, 113, 0.3)">
        <div class="th-icon">🚨</div>
        <div class="th-name" style="color: var(--c-danger)">ALERTA</div>
        <div class="th-range mono">FC: &gt; 80 bpm · SpO₂: &lt; 90%</div>
        <div class="th-desc">Usuario despierto o hipoxia severa · Activar alerta en la banda</div>
      </div>
    </div>

    <!-- Combined HR + SpO2 chart -->
    <div class="card">
      <SensorChart
        :data="store.max"
        value-key="heartRate"
        value-key2="spo2"
        title="Ritmo Cardíaco y Saturación de Oxígeno"
        subtitle="FC (bpm) y SpO₂ (%) · Eje Y compartido"
        line-color="#f472b6"
        line-color2="#a78bfa"
        label2="SpO₂ (%)"
        unit=""
        :height="300"
        :thresholds="combinedThresholds"
      />
    </div>

    <!-- Individual charts -->
    <div class="g2">
      <div class="card">
        <SensorChart
          :data="store.max"
          value-key="heartRate"
          title="Frecuencia Cardíaca"
          subtitle="Latidos por minuto"
          line-color="#f472b6"
          unit="bpm"
          :height="220"
          :thresholds="hrThresholds"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.max"
          value-key="spo2"
          title="Saturación de Oxígeno (SpO₂)"
          subtitle="% saturación en sangre"
          line-color="#a78bfa"
          unit="%"
          :height="220"
          :thresholds="spo2Thresholds"
        />
      </div>
    </div>

    <!-- Raw IR/Red signal -->
    <div class="g2">
      <div class="card">
        <SensorChart
          :data="store.max"
          value-key="irValue"
          title="Señal IR (Infrarroja)"
          subtitle="Valor ADC crudo del LED infrarrojo"
          line-color="#c4b5fd"
          unit=""
          :height="180"
        />
      </div>
      <div class="card">
        <SensorChart
          :data="store.max"
          value-key="redValue"
          title="Señal Red (Roja)"
          subtitle="Valor ADC crudo del LED rojo"
          line-color="#fca5a5"
          unit=""
          :height="180"
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

const avgHr = computed(() => {
  if (!store.max.length) return '—'
  const avg = store.max.reduce((a, d) => a + d.heartRate, 0) / store.max.length
  return avg.toFixed(1) + ' bpm'
})
const avgSpo2 = computed(() => {
  if (!store.max.length) return '—'
  const avg = store.max.reduce((a, d) => a + d.spo2, 0) / store.max.length
  return avg.toFixed(1) + '%'
})

const combinedThresholds = [
  { label: 'DESPIERTO', max: 200, min: 80, color: '#f87171', range: 'FC > 80 bpm' },
  { label: 'SUEÑO PROF.', max: 60, min: 40, color: '#34d399', range: 'FC 40–60 bpm' },
  { label: 'SpO₂ MÍNIMO', max: 90, color: '#f87171', range: 'SpO₂ < 90%' },
  { label: 'SpO₂ SALUDABLE', max: 95, color: '#34d399', range: 'SpO₂ ≥ 95%' },
]
const hrThresholds = [
  { label: 'DESPIERTO', max: 200, min: 80, color: '#f87171', range: '> 80 bpm' },
  { label: 'SUEÑO PROF.', max: 60, min: 40, color: '#34d399', range: '40–60 bpm' },
]
const spo2Thresholds = [
  { label: 'CRÍTICO', max: 90, color: '#f87171', range: '< 90%' },
  { label: 'HIPOXIA', max: 95, min: 90, color: '#f59e0b', range: '90–94%' },
  { label: 'SALUDABLE', max: 100, min: 95, color: '#34d399', range: '≥ 95%' },
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
.g2 {
  gap: 1rem;
  margin-bottom: 1.25rem;
}
</style>
