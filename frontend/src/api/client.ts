/**
 * API client configuration using Axios.
 */
import axios, { AxiosInstance, AxiosError } from 'axios'

// In Docker, use the Vite proxy (/api). Otherwise use VITE_API_URL or fallback to localhost
// The proxy in vite.config.ts forwards /api to http://backend:8000
const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data as any

      if (status === 401) {
        // Handle unauthorized
        console.error('Unauthorized')
      } else if (status === 404) {
        // Handle not found
        console.error('Resource not found')
      } else if (status >= 500) {
        // Handle server errors
        console.error('Server error')
      }

      return Promise.reject(data?.error || error)
    } else if (error.request) {
      // Request made but no response
      console.error('Network error')
      return Promise.reject(new Error('Network error. Please check your connection.'))
    } else {
      // Something else happened
      return Promise.reject(error)
    }
  }
)

export default apiClient


