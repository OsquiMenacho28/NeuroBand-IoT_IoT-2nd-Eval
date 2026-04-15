<template>
  <div class="shell">
    <!-- ── Sidebar ─────────────────────────────────────────── -->
    <aside class="sidebar">
      <!-- Brand -->
      <div class="brand">
        <div class="brand-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="13" stroke="#38bdf8" stroke-width="1.5" />
            <path
              d="M5 14 Q8 8 11 14 Q14 20 17 14 Q20 8 23 14"
              stroke="#38bdf8"
              stroke-width="1.8"
              fill="none"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <div>
          <div class="brand-name">NeuroBand</div>
          <div class="brand-tag">Monitor de Sueño IoT</div>
        </div>
      </div>

      <!-- Connection status -->
      <div class="sse-badge" :class="store.sseConnected ? 'sse-live' : 'sse-off'">
        <span :class="store.sseConnected ? 'dot-live' : 'dot-off'"></span>
        {{ store.sseConnected ? 'En vivo · SSE' : 'Desconectado' }}
      </div>

      <!-- Sleep Score pill -->
      <div v-if="store.sleepScore !== null" class="score-pill">
        <div class="score-label">Calidad del sueño</div>
        <div class="score-ring">
          <svg width="64" height="64" viewBox="0 0 64 64">
            <circle
              cx="32"
              cy="32"
              r="26"
              stroke="rgba(255,255,255,0.06)"
              stroke-width="6"
              fill="none"
            />
            <circle
              cx="32"
              cy="32"
              r="26"
              :stroke="scoreColor"
              stroke-width="6"
              fill="none"
              stroke-linecap="round"
              :stroke-dasharray="`${(store.sleepScore / 100) * 163.4} 163.4`"
              transform="rotate(-90 32 32)"
              style="transition: stroke-dasharray 0.8s ease"
            />
          </svg>
          <div class="score-number" :style="{ color: scoreColor }">{{ store.sleepScore }}</div>
        </div>
        <div class="score-quality" :class="`${store.sleepQuality?.level}-col`">
          {{ store.sleepQuality?.label }}
        </div>
      </div>

      <!-- Nav -->
      <nav class="nav">
        <RouterLink to="/" class="nav-link"><span class="ni">⬡</span> Dashboard</RouterLink>
        <RouterLink to="/MPU6050" class="nav-link mpu-link"
          ><span class="ni">◈</span> Movimiento</RouterLink
        >
        <RouterLink to="/MAX30102" class="nav-link hr-link"
          ><span class="ni">♥</span> Ritmo Cardíaco</RouterLink
        >
        <RouterLink to="/LDR" class="nav-link ldr-link"
          ><span class="ni">◎</span> Luz Ambiental</RouterLink
        >
        <RouterLink to="/TableView" class="nav-link"
          ><span class="ni">▦</span> Registros</RouterLink
        >
      </nav>

      <!-- Sensor counts -->
      <div class="sensor-counts">
        <div class="sc-item">
          <span class="sc-val mpu-col">{{ store.countMpu }}</span
          ><span class="sc-lbl">MPU</span>
        </div>
        <div class="sc-item">
          <span class="sc-val hr-col">{{ store.countMax }}</span
          ><span class="sc-lbl">MAX</span>
        </div>
        <div class="sc-item">
          <span class="sc-val ldr-col">{{ store.countLdr }}</span
          ><span class="sc-lbl">LDR</span>
        </div>
      </div>
    </aside>

    <!-- ── Main content ─────────────────────────────────────── -->
    <main class="main">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useNeuroBandStore } from '@/stores/neuroBandStore'

const store = useNeuroBandStore()

const scoreColor = computed(() => {
  const s = store.sleepScore
  if (s === null) return '#3d5470'
  if (s >= 75) return '#34d399'
  if (s >= 45) return '#f59e0b'
  return '#f87171'
})

onMounted(async () => {
  await store.loadHistorical()
  store.connectSSE()
})
onUnmounted(() => store.disconnectSSE())
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 230px;
  min-height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0;
  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.1rem 1.1rem;
  border-bottom: 1px solid var(--border);
}
.brand-icon {
  flex-shrink: 0;
}
.brand-name {
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.01em;
  color: var(--text);
}
.brand-tag {
  font-size: 0.62rem;
  color: var(--text-dim);
  letter-spacing: 0.04em;
}

.sse-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.7rem;
  letter-spacing: 0.04em;
  padding: 0.45rem 1.1rem;
  border-bottom: 1px solid var(--border);
}
.sse-live {
  color: var(--c-good);
}
.sse-off {
  color: var(--text-dim);
}

.score-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}
.score-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--text-dim);
  margin-bottom: 0.6rem;
}
.score-ring {
  position: relative;
  width: 64px;
  height: 64px;
}
.score-number {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 500;
}
.score-quality {
  font-size: 0.72rem;
  font-weight: 600;
  margin-top: 0.45rem;
}

.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.75rem 0.6rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.58rem 0.8rem;
  border-radius: var(--radius-sm);
  color: var(--text-sub);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition);
}
.ni {
  width: 18px;
  text-align: center;
  font-size: 0.95rem;
}
.nav-link:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.04);
}
.nav-link.router-link-active {
  color: var(--c-mpu);
  background: rgba(56, 189, 248, 0.09);
}
.mpu-link.router-link-active {
  color: var(--c-mpu);
  background: rgba(56, 189, 248, 0.09);
}
.hr-link.router-link-active {
  color: var(--c-max-hr);
  background: rgba(244, 114, 182, 0.09);
}
.ldr-link.router-link-active {
  color: var(--c-ldr);
  background: rgba(251, 191, 36, 0.09);
}

.sensor-counts {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border);
  gap: 0.25rem;
}
.sc-item {
  text-align: center;
}
.sc-val {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 500;
  display: block;
}
.sc-lbl {
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
}

/* ── Main ── */
.main {
  margin-left: 230px;
  flex: 1;
  padding: 1.75rem 2rem;
  min-height: 100vh;
}

/* ── Page transitions ── */
.page-enter-active,
.page-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
