import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const client: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout for AI-heavy requests
})

// Request interceptor
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
client.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    // Log errors for debugging (no redirect to nonexistent /login)
    if (error.response?.status === 401) {
      console.warn('Received 401 Unauthorized — auth not yet implemented')
    }
    return Promise.reject(error)
  }
)

export default client
