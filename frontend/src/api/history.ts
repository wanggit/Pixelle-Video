import api from './index'
import type { HistoryListResponse, HistoryTaskDetail, HistoryStatistics } from '@/types'

export const historyApi = {
  list: (page = 1, pageSize = 20, status?: string, sortBy = 'created_at', sortOrder = 'desc') =>
    api.get<HistoryListResponse>('/api/history/tasks', {
      params: { page, page_size: pageSize, status, sort_by: sortBy, sort_order: sortOrder },
    }),

  detail: (taskId: string) =>
    api.get<HistoryTaskDetail>(`/api/history/tasks/${taskId}`),

  remove: (taskId: string) =>
    api.delete(`/api/history/tasks/${taskId}`),

  duplicate: (taskId: string) =>
    api.post(`/api/history/tasks/${taskId}/duplicate`),

  statistics: () =>
    api.get<HistoryStatistics>('/api/history/statistics'),
}
