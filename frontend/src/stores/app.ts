import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const language = ref('zh-CN')
  const sidebarCollapsed = ref(false)

  const isChinese = computed(() => language.value === 'zh-CN')

  function setLanguage(lang: string) {
    language.value = lang
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    language,
    sidebarCollapsed,
    isChinese,
    setLanguage,
    toggleSidebar,
  }
})
