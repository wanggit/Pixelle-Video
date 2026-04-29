import api from './index'
import type { WorkflowListResponse, TemplateListResponse, BGMListResponse, Capabilities } from '@/types'

export const resourceApi = {
  workflows: {
    tts: () => api.get<WorkflowListResponse>('/api/resources/workflows/tts'),
    media: () => api.get<WorkflowListResponse>('/api/resources/workflows/media'),
    image: () => api.get<WorkflowListResponse>('/api/resources/workflows/image'),
  },

  templates: () =>
    api.get<TemplateListResponse>('/api/resources/templates'),

  bgm: () =>
    api.get<BGMListResponse>('/api/resources/bgm'),

  templateParams: (template: string) =>
    api.get('/api/frame/template/params', { params: { template } }),

  capabilities: () =>
    api.get<Capabilities>('/api/capabilities'),

  frameRender: (data: { template: string; title: string; text: string; image?: string }) =>
    api.post('/api/frame/render', data),
}
