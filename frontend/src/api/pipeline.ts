import api from './index'
import type {
  CustomMediaRequest,
  CustomMediaAsyncResponse,
  ImageToVideoRequest,
  ImageToVideoAsyncResponse,
  ActionTransferRequest,
  ActionTransferAsyncResponse,
  DigitalHumanRequest,
  DigitalHumanAsyncResponse,
} from '@/types'

export const pipelineApi = {
  customMedia: (data: CustomMediaRequest) =>
    api.post<CustomMediaAsyncResponse>('/api/pipelines/custom-media/async', data),

  imageToVideo: (data: ImageToVideoRequest) =>
    api.post<ImageToVideoAsyncResponse>('/api/pipelines/image-to-video/async', data),

  actionTransfer: (data: ActionTransferRequest) =>
    api.post<ActionTransferAsyncResponse>('/api/pipelines/action-transfer/async', data),

  digitalHuman: (data: DigitalHumanRequest) =>
    api.post<DigitalHumanAsyncResponse>('/api/pipelines/digital-human/async', data),
}
