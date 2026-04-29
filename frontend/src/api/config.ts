import api from './index'
import type { ConfigResponse, LLMTestResponse, ComfyUITestResponse } from '@/types'

export const configApi = {
  get: () =>
    api.get<ConfigResponse>('/api/config'),

  saveLLM: (data: { api_key?: string; base_url?: string; model?: string }) =>
    api.post('/api/config/llm', data),

  saveComfyUI: (data: {
    comfyui_url?: string
    comfyui_api_key?: string
    runninghub_api_key?: string
    runninghub_concurrent_limit?: number
    runninghub_instance_type?: string
  }) =>
    api.post('/api/config/comfyui', data),

  reset: () =>
    api.post('/api/config/reset'),

  testLLM: (data?: { api_key?: string; base_url?: string; model?: string }) =>
    api.post<LLMTestResponse>('/api/llm/test-connection', data || {}),

  testComfyUI: (data?: { comfyui_url?: string; comfyui_api_key?: string }) =>
    api.post<ComfyUITestResponse>('/api/comfyui/test-connection', data || {}),

  listModels: () =>
    api.get('/api/llm/models'),
}
