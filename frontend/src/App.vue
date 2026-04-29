<template>
  <div class="app-container">
    <AppHeader />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #F0F9FF;
}

.main-content {
  padding-top: 72px;
  max-width: 1440px;
  margin: 0 auto;
  padding-left: 24px;
  padding-right: 24px;
}
</style>
