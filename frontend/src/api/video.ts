import api from './index'
import type { VideoGenerateRequest, VideoGenerateResponse, VideoGenerateAsyncResponse } from '@/types'

export const videoApi = {
  generateSync: (data: VideoGenerateRequest) =>
    api.post<VideoGenerateResponse>('/api/video/generate/sync', data),

  generateAsync: (data: VideoGenerateRequest) =>
    api.post<VideoGenerateAsyncResponse>('/api/video/generate/async', data),
}
