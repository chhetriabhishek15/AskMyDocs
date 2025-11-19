/**
 * API endpoint definitions.
 */
import apiClient from './client'

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

// Upload
export interface UploadResponse {
  task_id: string
  status: string
  message: string
}

export interface TaskStatusResponse {
  task_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  error?: string | null
  document_id?: string | null
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await apiClient.get<TaskStatusResponse>(`/upload/${taskId}/status`)
  return response.data
}

// Chat
export interface ChatRequest {
  query: string
  session_id: string
  top_k?: number
  min_score?: number
  document_id?: string | null
}

export interface SourceInfo {
  chunk_id: string
  document_id: string
  document_filename: string
  similarity_score: number
  preview: string
}

export interface ChatResponse {
  answer: string
  sources: SourceInfo[]
  session_id: string
  usage: {
    prompt_tokens?: number
    completion_tokens?: number
    total_tokens?: number
  }
}

export const sendChatMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>('/chat', data)
  return response.data
}

// Documents
export interface Document {
  id: string
  filename: string
  created_at: string
  chunk_count: number
}

export interface DocumentListResponse {
  items: Document[]
  total: number
  page: number
  page_size: number
}

export const listDocuments = async (page = 1, pageSize = 20): Promise<DocumentListResponse> => {
  const response = await apiClient.get<DocumentListResponse>('/documents', {
    params: { page, page_size: pageSize },
  })
  return response.data
}

export const getDocument = async (documentId: string) => {
  const response = await apiClient.get(`/documents/${documentId}`)
  return response.data
}

// Conversations
export interface ConversationMessage {
  id: string
  user_message: string
  bot_message: string
  timestamp: string
}

export interface ConversationHistoryResponse {
  session_id: string
  messages: ConversationMessage[]
  total: number
}

export const getConversationHistory = async (
  sessionId: string,
  limit = 50
): Promise<ConversationHistoryResponse> => {
  const response = await apiClient.get<ConversationHistoryResponse>(
    `/conversations/${sessionId}`,
    {
      params: { limit },
    }
  )
  return response.data
}


