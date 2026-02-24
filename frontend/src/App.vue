<template>
  <div class="app-layout">
    <RouteProgressBar />
    <a
      href="#main-content"
      class="skip-to-content"
    >Skip to content</a>
    <SpaceBackground />
    <AppHeader />
    <main
      id="main-content"
      class="main-content"
    >
      <router-view v-slot="{ Component }">
        <Transition
          name="view-fade"
          mode="out-in"
        >
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
    <AppFooter />
    <AiChat />
    <FunFact />
    <NotificationToast />
    <ErrorLabPanel />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import RouteProgressBar from '@/components/layout/RouteProgressBar.vue'
import ErrorLabPanel from '@/components/common/ErrorLabPanel.vue'
import { useNotificationStore } from '@/stores/notifications'

const SpaceBackground = defineAsyncComponent(() => import('@/components/layout/SpaceBackground.vue'))
const AiChat = defineAsyncComponent(() => import('@/components/common/AiChat.vue'))
const FunFact = defineAsyncComponent(() => import('@/components/common/FunFact.vue'))
const NotificationToast = defineAsyncComponent(() => import('@/components/common/NotificationToast.vue'))

onMounted(() => {
  useNotificationStore().connect()
})
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-top: 52px;
  position: relative;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 32px;
  position: relative;
  z-index: 1;
}

.skip-to-content {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  background: var(--accent);
  color: #fff;
  padding: 8px 16px;
  border-radius: 0 0 var(--radius) var(--radius);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  text-decoration: none;
  transition: top 0.2s;
}

.skip-to-content:focus {
  top: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px 16px;
  }
}
</style>
