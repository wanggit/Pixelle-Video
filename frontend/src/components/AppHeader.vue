<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Brand -->
      <router-link to="/" class="brand">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="23 7 16 12 23 17 23 7"></polygon>
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
        </svg>
        <span class="brand-text">Pixelle-Video</span>
      </router-link>

      <!-- Nav Links -->
      <nav class="nav-links">
        <router-link to="/" class="nav-link" active-class="active">
          <ElIcon><HomeFilled /></ElIcon>
          <span>{{ t('nav.home') }}</span>
        </router-link>
        <router-link to="/history" class="nav-link" active-class="active">
          <ElIcon><Collection /></ElIcon>
          <span>{{ t('nav.history') }}</span>
        </router-link>
      </nav>

      <!-- Language Selector -->
      <div class="nav-actions">
        <el-select
          v-model="currentLang"
          class="lang-selector"
          @change="handleLangChange"
        >
          <el-option label="中文" value="zh-CN" />
          <el-option label="English" value="en-US" />
        </el-select>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled, Collection } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const router = useRouter()
const currentLang = ref(appStore.language)

function t(key: string): string {
  const translations: Record<string, Record<string, string>> = {
    'nav.home': { 'zh-CN': '首页', 'en-US': 'Home' },
    'nav.history': { 'zh-CN': '历史记录', 'en-US': 'History' },
  }
  const obj = translations[key]
  return obj?.[appStore.language] || key
}

function handleLangChange(lang: string) {
  appStore.setLanguage(lang)
  router.go(0)
}

watch(() => appStore.language, (val) => {
  currentLang.value = val
})
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #BAE6FD;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 32px;
  max-width: 1440px;
  margin: 0 auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #0C4A6E;
}

.brand-icon {
  width: 28px;
  height: 28px;
  color: #0EA5E9;
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748B;
  text-decoration: none;
  transition: all 200ms ease-out;
  cursor: pointer;
}

.nav-link:hover {
  background: #E0F2FE;
  color: #0EA5E9;
}

.nav-link.active {
  background: #E0F2FE;
  color: #0EA5E9;
  font-weight: 600;
}

.nav-actions {
  display: flex;
  align-items: center;
}

.lang-selector {
  width: 140px;
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 12px;
  }
  .nav-link {
    padding: 6px 10px;
    font-size: 13px;
  }
  .brand-text {
    font-size: 16px;
  }
}
</style>
