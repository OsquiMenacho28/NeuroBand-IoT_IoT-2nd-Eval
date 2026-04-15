<template>
  <div class="sensor-page fade-up">
    <div class="page-header">
      <div>
        <span class="badge badge-dim" style="color: var(--c-ldr); border-color: var(--c-ldr)"
          >LDR</span
        >
        <h1 class="page-title ldr-col">Luz Ambiental</h1>
        <p class="page-sub mono">
          Foto-resistor · Monitoreo de condiciones lumínicas para la producción de melatonina
        </p>
      </div>
      <div class="page-stats">
        <div class="stat">
          <div class="sv ldr-col mono">{{ avgLux }}</div>
          <div class="sl">lux promedio</div>
        </div>
        <div class="stat">
          <div class="sv mono">{{ avgVoltage }}</div>
          <div class="sl">voltaje prom.</div>
        </div>
        <div class="stat">
          <div class="sv mono">{{ store.countLdr }}</div>
          <div class="sl">registros</div>
        </div>
      </div>
    </div>

    <!-- Melatonin science cards -->
    <div class="g3 threshold-cards">
      <div class="card th-card" style="border-color: rgba(52, 211, 153, 0.3)">
        <div class="th-icon">🌑</div>
        <div class="th-name" style="color: var(--c-good)">OSCURIDAD IDEAL</div>
        <div class="th-range mono">Luz &lt; 5%</div>
        <div class="th-desc">
          Producción óptima de melatonina · Las condiciones perfectas para conciliar el sueño y
          mantener el ritmo circadiano
        </div>
      </div>
      <div class="card th-card" style="border-color: rgba(245, 158, 11, 0.3)">
        <div class="th-icon">🌒</div>
        <div class="th-name" style="color: var(--c-warn)">LUZ TENUE</div>
        <div class="th-range mono">5% – 30%</div>
        <div class="th-desc">
          Aceptable pero no ideal · Puede reducir ligeramente la producción de melatonina
        </div>
      </div>
      <div class="card th-card" style="border-color: rgba(248, 113, 113, 0.3)">
        <div class="th-icon">☀️</div>
        <div class="th-name" style="color: var(--c-danger)">MUY ILUMINADO</div>
        <div class="th-range mono">Luz &gt; 30%</div>
        <div class="th-desc">
          Supresión de melatonina · Interrumpe el ritmo circadiano · Calidad de sueño comprometida
        </div>
      </div>
    </div>

    <!-- Main light chart -->
    <div class="card">
      <SensorChart
        :data="store.ldr"
        value-key="luxPercent"
        title="Nivel de Luz Ambiental en el tiempo"
        subtitle="Eje Y = % de luz (0=oscuro, 100=máxima luz) · Impacto en melatonina"
        line-color="#fbbf24"
        unit="%"
        :height="300"
        :thresholds="ldrThresholds"
      />
    </div>

    <!-- Voltage chart -->
    <div class="card">
      <SensorChart
        :data="store.ldr"
        value-key="voltage"
        title="Voltaje del ADC"
        subtitle="Voltaje leído en el pin ADC del ESP32 (0–3.3V)"
        line-color="#fde68a"
        unit="V"
        :height="200"
      />
    </div>

    <!-- Science note -->
    <div class="card science-note">
      <div class="sn-title">🔬 ¿Por qué importa la luz para el sueño?</div>
      <p class="sn-text">
        La exposición a la luz — especialmente la luz azul — suprime la producción de melatonina en
        la glándula pineal. La melatonina es la hormona que regula el ciclo sueño-vigilia (ritmo
        circadiano). Una habitación oscura (&lt;5%) favorece la producción natural de melatonina, lo
        que facilita conciliar el sueño y mantener fases de sueño profundo más largas, fundamentales
        para la recuperación cognitiva y física.
      </p>
      <div class="sn-thresholds">
        <div class="snt-item good"><strong>&lt;5%</strong> — Producción de melatonina óptima</div>
        <div class="snt-item warn">
          <strong>5–30%</strong> — Ligera supresión de melatonina (~30%)
        </div>
        <div class="snt-item danger">
          <strong>&gt;30%</strong> — Supresión severa de melatonina (hasta 85%)
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

const avgLux = computed(() => {
  if (!store.ldr.length) return '—'
  const avg = store.ldr.reduce((a, d) => a + d.luxPercent, 0) / store.ldr.length
  return avg.toFixed(1) + '%'
})
const avgVoltage = computed(() => {
  if (!store.ldr.length) return '—'
  const avg = store.ldr.reduce((a, d) => a + d.voltage, 0) / store.ldr.length
  return avg.toFixed(3) + 'V'
})

const ldrThresholds = [
  { label: 'MUY ILUMINADO', max: 100, min: 30, color: '#f87171', range: '> 30%' },
  { label: 'LUZ TENUE', max: 30, min: 5, color: '#f59e0b', range: '5–30%' },
  { label: 'IDEAL', max: 5, color: '#34d399', range: '< 5%' },
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

.science-note {
  padding: 1.25rem 1.5rem;
}
.sn-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--text);
}
.sn-text {
  font-size: 0.82rem;
  color: var(--text-sub);
  line-height: 1.7;
  margin-bottom: 1rem;
}
.sn-thresholds {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.snt-item {
  font-size: 0.8rem;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
}
.snt-item.good {
  background: rgba(52, 211, 153, 0.08);
  color: var(--c-good);
}
.snt-item.warn {
  background: rgba(245, 158, 11, 0.08);
  color: var(--c-warn);
}
.snt-item.danger {
  background: rgba(248, 113, 113, 0.08);
  color: var(--c-danger);
}
</style>
