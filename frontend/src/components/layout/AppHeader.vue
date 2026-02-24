<template>
  <header class="topbar">
    <div class="topbar-inner">
      <router-link
        to="/"
        class="topbar-brand"
      >
        <span class="brand-mark">&#9670;</span>
        <span class="brand-text">SPACEX</span>
      </router-link>

      <!-- Desktop nav -->
      <nav class="topbar-nav desktop-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: isActive(item.to) }"
        >
          {{ item.label }}
        </router-link>

        <div
          class="nav-dropdown"
          @mouseenter="dropdownOpen = true"
          @mouseleave="dropdownOpen = false"
        >
          <button
            class="nav-link dropdown-trigger"
            :class="{ active: isMoreActive }"
            aria-haspopup="true"
            :aria-expanded="dropdownOpen ? 'true' : 'false'"
            aria-label="Explore more sections"
          >
            Explore <span class="dropdown-arrow">&#9662;</span>
          </button>
          <Transition name="dropdown">
            <div
              v-show="dropdownOpen"
              class="dropdown-menu"
            >
              <router-link
                v-for="item in moreItems"
                :key="item.to"
                :to="item.to"
                class="dropdown-item"
                :class="{ active: isActive(item.to) }"
                @click="dropdownOpen = false"
              >
                <span
                  class="dropdown-icon"
                  aria-hidden="true"
                >{{ item.icon }}</span>
                {{ item.label }}
              </router-link>
            </div>
          </Transition>
        </div>
      </nav>

      <div class="topbar-actions">
        <button
          class="theme-toggle"
          :title="themeStore.theme === 'dark' ? 'Light mode' : 'Dark mode'"
          :aria-pressed="themeStore.theme === 'dark' ? 'true' : 'false'"
          aria-label="Toggle theme"
          @click="themeStore.toggle()"
        >
          <span v-if="themeStore.theme === 'dark'">&#9788;</span>
          <span v-else>&#9790;</span>
        </button>
        <span class="topbar-credit">Juan Alberto Toledo Tello</span>

        <!-- Mobile hamburger -->
        <button
          class="hamburger"
          :class="{ open: mobileOpen }"
          aria-label="Menu"
          @click="mobileOpen = !mobileOpen"
        >
          <span class="hamburger-line" />
          <span class="hamburger-line" />
          <span class="hamburger-line" />
        </button>
      </div>
    </div>

    <!-- Mobile drawer overlay -->
    <Transition name="fade">
      <div
        v-if="mobileOpen"
        class="drawer-overlay"
        @click="mobileOpen = false"
      />
    </Transition>

    <!-- Mobile drawer -->
    <Transition name="slide">
      <nav
        v-if="mobileOpen"
        class="mobile-drawer"
      >
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="mobile-link"
          :class="{ active: isActive(item.to) }"
          @click="mobileOpen = false"
        >
          {{ item.label }}
        </router-link>

        <!-- Explore accordion -->
        <button
          class="mobile-link mobile-accordion-trigger"
          :class="{ active: isMoreActive }"
          aria-label="Explore more sections"
          :aria-expanded="exploreOpen ? 'true' : 'false'"
          @click="exploreOpen = !exploreOpen"
        >
          Explore
          <span
            class="accordion-arrow"
            :class="{ rotated: exploreOpen }"
          >&#9662;</span>
        </button>
        <div
          class="accordion-body"
          :class="{ expanded: exploreOpen }"
        >
          <router-link
            v-for="item in moreItems"
            :key="item.to"
            :to="item.to"
            class="mobile-link mobile-sub-link"
            :class="{ active: isActive(item.to) }"
            @click="mobileOpen = false"
          >
            <span
              class="dropdown-icon"
              aria-hidden="true"
            >{{ item.icon }}</span>
            {{ item.label }}
          </router-link>
        </div>
      </nav>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import type { NavItem } from '@/types'

const route = useRoute()
const themeStore = useThemeStore()
const dropdownOpen = ref(false)
const mobileOpen = ref(false)
const exploreOpen = ref(false)

watch(() => route.path, () => {
  dropdownOpen.value = false
  mobileOpen.value = false
})

const navItems: Omit<NavItem, 'icon'>[] = [
  { to: '/', label: 'Overview' },
  { to: '/launches', label: 'Launches' },
  { to: '/fleet', label: 'Fleet' },
  { to: '/starlink', label: 'Starlink' },
  { to: '/economics', label: 'Economics' },
  { to: '/emissions', label: 'Emissions' },
]

const moreItems: NavItem[] = [
  { to: '/history', label: 'History', icon: '◈' },
  { to: '/landing', label: 'Landing', icon: '▽' },
  { to: '/starman', label: 'Starman', icon: '✦' },
]

const isMoreActive = computed(() => moreItems.some((item) => isActive(item.to)))

function isActive(to: string): boolean {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<style scoped>
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 52px;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border);
  z-index: 100;
  isolation: isolate;
  display: flex;
  align-items: center;
}

.topbar-inner {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text);
  flex-shrink: 0;
}

.brand-mark {
  font-size: 12px;
  color: var(--accent);
}

.brand-text {
  font-family: var(--font-display);
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text);
}

.topbar-nav {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  font-family: var(--font-body);
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--text-muted);
  text-decoration: none;
  padding: 4px 0;
  border-bottom: 1.5px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.nav-link:hover {
  color: var(--text-secondary);
}

.nav-link.active {
  color: var(--text);
  border-bottom-color: var(--accent);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.theme-toggle {
  background: none;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  line-height: 1;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text);
  border-color: var(--text-muted);
}

.topbar-credit {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  opacity: 0.5;
}

/* Desktop dropdown */
.nav-dropdown {
  position: relative;
}

.dropdown-trigger {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.dropdown-arrow {
  font-size: 0.6em;
  transition: transform 0.2s;
}

.nav-dropdown:hover .dropdown-arrow {
  transform: translateY(1px);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px;
  min-width: 170px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  z-index: 200;
}

.dropdown-menu::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 10px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-family: var(--font-body);
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: calc(var(--radius) - 2px);
  transition: background 0.12s, color 0.12s;
}

.dropdown-item:hover {
  background: var(--bg-hover);
  color: var(--text);
}

.dropdown-item.active {
  color: var(--accent);
}

.dropdown-icon {
  font-size: 0.75rem;
  width: 16px;
  text-align: center;
  color: var(--accent);
  opacity: 0.7;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-4px);
}

.dropdown-enter-to,
.dropdown-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* Hamburger button — hidden on desktop */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  padding: 10px;
  background: none;
  border: none;
  cursor: pointer;
}

.hamburger-line {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text);
  border-radius: 1px;
  transition: transform 0.25s, opacity 0.25s;
}

.hamburger.open .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger.open .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger.open .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile drawer overlay */
.drawer-overlay {
  position: fixed;
  inset: 0;
  top: 52px;
  background: rgba(0, 0, 0, 0.45);
  z-index: 150;
}

/* Mobile drawer */
.mobile-drawer {
  position: fixed;
  top: 52px;
  right: 0;
  bottom: 0;
  width: 280px;
  max-width: 85vw;
  background: var(--bg-base);
  border-left: 1px solid var(--border);
  z-index: 200;
  padding: 16px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  font-family: var(--font-body);
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  min-height: 48px;
}

.mobile-link:hover,
.mobile-link:active {
  background: var(--bg-hover);
  color: var(--text);
}

.mobile-link.active {
  color: var(--accent);
}

.mobile-accordion-trigger {
  justify-content: space-between;
}

.accordion-arrow {
  font-size: 0.65em;
  transition: transform 0.25s;
}

.accordion-arrow.rotated {
  transform: rotate(180deg);
}

.accordion-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.accordion-body.expanded {
  max-height: 200px;
}

.mobile-sub-link {
  padding-left: 40px;
  font-size: 0.92rem;
  min-height: 44px;
}

/* Drawer transitions */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile: show hamburger, hide desktop nav */
@media (max-width: 768px) {
  .desktop-nav { display: none; }
  .hamburger { display: flex; }
  .topbar-credit { display: none; }
  .topbar-inner { padding: 0 16px; }
}
</style>
