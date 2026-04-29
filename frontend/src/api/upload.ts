import api from './index'
import type { FileUploadResponse } from '@/types'

export const uploadApi = {
  upload: (file: File, fileType: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    return api.upload<FileUploadResponse>('/api/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
