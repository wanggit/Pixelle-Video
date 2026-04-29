import { defineStore } from 'pinia'
import { ref } from 'vue'
import { configApi } from '@/api/config'
import type { LLMConfig, ComfyUIConfig } from '@/types'

export const useConfigStore = defineStore('config', () => {
  const llmConfig = ref<LLMConfig>({ api_key: '', base_url: '', model: '' })
  const comfyuiConfig = ref<ComfyUIConfig>({
    comfyui_url: 'http://127.0.0.1:8188',
    comfyui_api_key: '',
    runninghub_api_key: '',
    runninghub_concurrent_limit: 1,
    runninghub_instance_type: '24G',
  })
  const loading = ref(false)
  const lastSaved = ref<string | null>(null)

  async function loadConfig() {
    loading.value = true
    try {
      const data = await configApi.get()
      llmConfig.value = data.llm
      comfyuiConfig.value = data.comfyui
    } finally {
      loading.value = false
    }
  }

  async function saveLLMConfig() {
    loading.value = true
    try {
      await configApi.saveLLM(llmConfig.value)
      lastSaved.value = new Date().toISOString()
    } finally {
      loading.value = false
    }
  }

  async function saveComfyUIConfig() {
    loading.value = true
    try {
      await configApi.saveComfyUI(comfyuiConfig.value)
      lastSaved.value = new Date().toISOString()
    } finally {
      loading.value = false
    }
  }

  async function testLLM() {
    return await configApi.testLLM(llmConfig.value)
  }

  async function testComfyUI() {
    return await configApi.testComfyUI(comfyuiConfig.value)
  }

  async function listModels() {
    const resp = await configApi.listModels()
    return resp.models || []
  }

  return {
    llmConfig,
    comfyuiConfig,
    loading,
    lastSaved,
    loadConfig,
    saveLLMConfig,
    saveComfyUIConfig,
    testLLM,
    testComfyUI,
    listModels,
  }
})
