import { ref, onUnmounted } from 'vue'
import type { ProgressEvent } from '@/types'

export function useProgress(taskId: string) {
  const progress = ref(0)
  const statusText = ref('')
  const isRunning = ref(false)
  const isComplete = ref(false)
  const error = ref<string | null>(null)
  const eventLog = ref<ProgressEvent[]>([])

  let eventSource: EventSource | null = null

  function start() {
    if (!taskId) return

    isRunning.value = true
    isComplete.value = false
    error.value = null
    progress.value = 0
    statusText.value = '任务已提交...'
    eventLog.value = []

    eventSource = new EventSource(`/api/tasks/${taskId}/stream`)

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data)
        eventLog.value.push(data)

        if (data.progress !== undefined) {
          progress.value = data.progress
        }

        // Build status text from event data
        const parts: string[] = []
        if (data.step) parts.push(data.step)
        if (data.action) parts.push(data.action)
        if (data.extra_info) parts.push(data.extra_info)
        if (data.frame_current && data.frame_total) {
          parts.push(`${data.frame_current}/${data.frame_total}`)
        }
        statusText.value = parts.length > 0 ? parts.join(' - ') : statusText.value

        if (data.event_type === 'completed' || data.event_type === 'success') {
          isComplete.value = true
          isRunning.value = false
          progress.value = 100
          statusText.value = '完成！'
          eventSource?.close()
        }

        if (data.event_type === 'error' || data.event_type === 'failed') {
          error.value = data.extra_info || '任务失败'
          isRunning.value = false
          eventSource?.close()
        }
      } catch {
        // Ignore parse errors
      }
    }

    eventSource.onerror = () => {
      // Don't set error on close, only on actual connection failure
      if (eventSource?.readyState === EventSource.CLOSED) return
      error.value = '连接中断'
      isRunning.value = false
      eventSource?.close()
    }
  }

  function stop() {
    eventSource?.close()
    eventSource = null
    isRunning.value = false
  }

  onUnmounted(() => {
    stop()
  })

  return {
    progress,
    statusText,
    isRunning,
    isComplete,
    error,
    eventLog,
    start,
    stop,
  }
}
