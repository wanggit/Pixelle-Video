import api from './index'
import type { Task } from '@/types'

export const taskApi = {
  list: (status?: string, limit = 100) =>
    api.get<Task[]>('/api/tasks', { params: { status, limit } }),

  detail: (taskId: string) =>
    api.get<Task>(`/api/tasks/${taskId}`),

  cancel: (taskId: string) =>
    api.delete(`/api/tasks/${taskId}`),

  // SSE progress streaming
  stream: (taskId: string) => {
    const url = `/api/tasks/${taskId}/stream`
    return new EventSource(url)
  },
}
