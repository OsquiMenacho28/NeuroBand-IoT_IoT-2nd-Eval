import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useNeuroBandStore = defineStore('neuroband', () => {
  // ── Sensor data arrays ────────────────────────────────────
  const mpu = ref([]) // MPU6050 DataPoints
  const max = ref([]) // MAX30102 DataPoints
  const ldr = ref([]) // LDR DataPoints

  // ── SSE state ─────────────────────────────────────────────
  const sseConnected = ref(false)
  let eventSource = null

  // ── Computed: latest readings ─────────────────────────────
  const latestMpu = computed(() => mpu.value.at(-1) ?? null)
  const latestMax = computed(() => max.value.at(-1) ?? null)
  const latestLdr = computed(() => ldr.value.at(-1) ?? null)

  // ── Computed: counts ──────────────────────────────────────
  const countMpu = computed(() => mpu.value.length)
  const countMax = computed(() => max.value.length)
  const countLdr = computed(() => ldr.value.length)

  // ── Computed: sleep quality score (0–100) ─────────────────
  // Aggregates latest readings from all 3 sensors
  const sleepScore = computed(() => {
    let score = 100
    let factors = 0

    if (latestMpu.value) {
      factors++
      const mv = latestMpu.value.movementLevel
      if (mv === 'ACTIVE') score -= 35
      else if (mv === 'LIGHT') score -= 10
    }

    if (latestMax.value) {
      factors++
      // Heart rate contribution
      const hr = latestMax.value.hrStatus
      if (hr === 'AWAKE') score -= 25
      else if (hr === 'RESTING') score -= 5

      // SpO2 contribution
      const sp = latestMax.value.spo2Status
      if (sp === 'CRITICAL') score -= 35
      else if (sp === 'MILD_HYPOXIA') score -= 15
    }

    if (latestLdr.value) {
      factors++
      const ls = latestLdr.value.lightStatus
      if (ls === 'BRIGHT') score -= 20
      else if (ls === 'DIM') score -= 5
    }

    if (factors === 0) return null
    return Math.max(0, score)
  })

  const sleepQuality = computed(() => {
    const s = sleepScore.value
    if (s === null) return null
    if (s >= 75) return { label: 'Sueño óptimo', level: 'good' }
    if (s >= 45) return { label: 'Sueño regular', level: 'warn' }
    return { label: 'Sueño deficiente', level: 'danger' }
  })

  // ── Actions ───────────────────────────────────────────────

  async function loadHistorical() {
    const [r1, r2, r3] = await Promise.all([
      axios.get('/api/mpu6050'),
      axios.get('/api/max30102'),
      axios.get('/api/ldr'),
    ])
    mpu.value = r1.data
    max.value = r2.data
    ldr.value = r3.data
  }

  function connectSSE() {
    if (eventSource) return
    eventSource = new EventSource('/api/stream')

    eventSource.addEventListener('ping', () => {
      sseConnected.value = true
    })

    eventSource.addEventListener('sensor-data', (e) => {
      const dp = JSON.parse(e.data)
      switch (dp.sensor) {
        case 'mpu6050':
          mpu.value.push(dp)
          break
        case 'max30102':
          max.value.push(dp)
          break
        case 'ldr':
          ldr.value.push(dp)
          break
      }
    })

    eventSource.onerror = () => {
      sseConnected.value = false
    }
  }

  function disconnectSSE() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    sseConnected.value = false
  }

  function clearData() {
    mpu.value = []
    max.value = []
    ldr.value = []
  }

  return {
    mpu,
    max,
    ldr,
    sseConnected,
    latestMpu,
    latestMax,
    latestLdr,
    countMpu,
    countMax,
    countLdr,
    sleepScore,
    sleepQuality,
    loadHistorical,
    connectSSE,
    disconnectSSE,
    clearData,
  }
})
