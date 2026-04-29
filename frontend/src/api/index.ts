import axios, { AxiosInstance, AxiosError } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 600000, // 10 minutes for video generation
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError) => {
    const message = error.response?.data
      ? (error.response.data as { detail?: string }).detail || error.message
      : error.message
    console.error(`API Error [${error.response?.status}]:`, message)
    return Promise.reject(new Error(message))
  }
)

export default apiClient
