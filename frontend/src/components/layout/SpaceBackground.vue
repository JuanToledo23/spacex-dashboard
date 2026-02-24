<template>
  <canvas
    ref="canvasRef"
    class="space-bg"
    aria-hidden="true"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Star {
  x: number
  y: number
  r: number
  baseAlpha: number
  speed: number
  phase: number
}

interface ShootingStar {
  x: number
  y: number
  dx: number
  dy: number
  length: number
  life: number
  maxLife: number
}

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number | null = null
let stars: Star[] = []
let shootingStar: ShootingStar | null = null
let lastShootingTime = 0
let resizeObserver: ResizeObserver | null = null

const STAR_COUNT = 180
const SHOOTING_INTERVAL_MIN = 8000
const SHOOTING_INTERVAL_MAX = 14000
const SHOOTING_DURATION = 800

function isDark() {
  return document.documentElement.getAttribute('data-theme') !== 'light'
}

function createStars(w: number, h: number): void {
  stars = []
  for (let i = 0; i < STAR_COUNT; i++) {
    stars.push({
      x: Math.random() * w,
      y: Math.random() * h,
      r: 0.4 + Math.random() * 1.4,
      baseAlpha: 0.15 + Math.random() * 0.45,
      speed: 0.3 + Math.random() * 1.2,
      phase: Math.random() * Math.PI * 2,
    })
  }
}

function spawnShootingStar(w: number, h: number): void {
  const edge = Math.random()
  let x: number, y: number
  if (edge < 0.5) {
    x = Math.random() * w
    y = -10
  } else {
    x = w + 10
    y = Math.random() * h * 0.5
  }

  const angle = Math.PI * 0.6 + Math.random() * 0.5
  const speed = 0.6 + Math.random() * 0.4

  shootingStar = {
    x,
    y,
    dx: Math.cos(angle) * speed,
    dy: Math.sin(angle) * speed,
    length: 60 + Math.random() * 80,
    life: 0,
    maxLife: SHOOTING_DURATION,
  }
}

function draw(ctx: CanvasRenderingContext2D, w: number, h: number, time: number): void {
  ctx.clearRect(0, 0, w, h)

  const dark = isDark()
  const starColor = dark ? '255,255,255' : '80,80,100'
  const alphaScale = dark ? 1.0 : 0.25

  for (const star of stars) {
    const twinkle = Math.sin(time * 0.001 * star.speed + star.phase)
    const alpha = star.baseAlpha + twinkle * 0.2
    const finalAlpha = Math.max(0.04, Math.min(1, alpha)) * alphaScale

    ctx.beginPath()
    ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${starColor},${finalAlpha.toFixed(3)})`
    ctx.fill()
  }

  if (shootingStar) {
    shootingStar.life += 16
    const progress = shootingStar.life / shootingStar.maxLife

    if (progress >= 1) {
      shootingStar = null
    } else {
      const dist = progress * shootingStar.length * 8
      const headX = shootingStar.x + shootingStar.dx * dist
      const headY = shootingStar.y + shootingStar.dy * dist

      const tailDist = Math.max(0, dist - shootingStar.length)
      const tailX = shootingStar.x + shootingStar.dx * tailDist
      const tailY = shootingStar.y + shootingStar.dy * tailDist

      const fadeIn = Math.min(1, progress * 4)
      const fadeOut = Math.max(0, 1 - (progress - 0.6) / 0.4)
      const intensity = Math.min(fadeIn, fadeOut)

      const shootAlpha = (dark ? 0.7 : 0.15) * intensity

      const grad = ctx.createLinearGradient(tailX, tailY, headX, headY)
      grad.addColorStop(0, `rgba(${starColor},0)`)
      grad.addColorStop(0.7, `rgba(${starColor},${(shootAlpha * 0.5).toFixed(3)})`)
      grad.addColorStop(1, `rgba(${starColor},${shootAlpha.toFixed(3)})`)

      ctx.beginPath()
      ctx.moveTo(tailX, tailY)
      ctx.lineTo(headX, headY)
      ctx.strokeStyle = grad
      ctx.lineWidth = dark ? 1.5 : 1
      ctx.lineCap = 'round'
      ctx.stroke()

      if (dark) {
        ctx.beginPath()
        ctx.arc(headX, headY, 1.5, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,255,255,${(shootAlpha * 0.8).toFixed(3)})`
        ctx.fill()
      }
    }
  }

  if (!shootingStar && time - lastShootingTime > SHOOTING_INTERVAL_MIN + Math.random() * (SHOOTING_INTERVAL_MAX - SHOOTING_INTERVAL_MIN)) {
    spawnShootingStar(w, h)
    lastShootingTime = time
  }
}

function loop(time: number): void {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  draw(ctx, canvas.width, canvas.height, time)
  animationId = requestAnimationFrame(loop)
}

function resize(): void {
  const canvas = canvasRef.value
  if (!canvas) return
  const dpr = window.devicePixelRatio || 1
  const w = window.innerWidth
  const h = window.innerHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.scale(dpr, dpr)
  createStars(w, h)
}

function startAnimation(): void {
  resize()
  animationId = requestAnimationFrame(loop)
  resizeObserver = new ResizeObserver(() => resize())
  resizeObserver.observe(document.body)
}

onMounted(() => {
  if ('requestIdleCallback' in window) {
    (window as any).requestIdleCallback(startAnimation, { timeout: 200 })
  } else {
    setTimeout(startAnimation, 100)
  }
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resizeObserver) resizeObserver.disconnect()
})
</script>

<style scoped>
.space-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  width: 100vw;
  height: 100vh;
}
</style>
