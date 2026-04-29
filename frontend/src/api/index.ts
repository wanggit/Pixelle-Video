import axios, { AxiosInstance, AxiosError } from 'axios'

const baseClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor - unwrap .data so callers get typed response directly
baseClient.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    const message = error.response?.data
      ? (error.response.data as { detail?: string }).detail || error.message
      : error.message
    console.error(`API Error [${error.response?.status}]:`, message)
    return Promise.reject(new Error(message))
  }
)

// Typed wrapper that matches the unwrapped return behavior
const api = baseClient as unknown as {
  get<T>(url: string, config?: Record<string, unknown>): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<T>
  delete<T = unknown>(url: string, config?: Record<string, unknown>): Promise<T>
  patch<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<T>
}

export default api
