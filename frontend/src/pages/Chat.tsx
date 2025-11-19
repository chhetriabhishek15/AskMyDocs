/**
 * Chat page - Full chat interface with RAG integration.
 */
import { useState, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import MessageList, { Message } from '../components/MessageList'
import MessageInput from '../components/MessageInput'
import SourceList from '../components/SourceList'
import { sendChatMessage, ChatResponse, SourceInfo } from '../api/endpoints'

// Session management utilities
const SESSION_STORAGE_KEY = 'tiramai_chat_session_id'

const getOrCreateSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY)
  if (!sessionId) {
    // Generate a simple session ID (in production, you might want UUID)
    sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId)
  }
  return sessionId
}

const Chat: React.FC = () => {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId] = useState<string>(() => getOrCreateSessionId())

  // React Query mutation for sending chat messages
  const chatMutation = useMutation({
    mutationFn: (query: string) =>
      sendChatMessage({
        query,
        session_id: sessionId,
        top_k: 5,
        min_score: 0.5,
      }),
    onSuccess: (data: ChatResponse, variables: string) => {
      // Add assistant response (user message was already added in handleSendMessage)
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    },
    onError: (error: any) => {
      console.error('Chat error:', error)
      // Add error message to chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error?.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    },
  })

  const handleSendMessage = useCallback(
    (message: string) => {
      if (!message.trim()) return

      // Add user message immediately for better UX
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])

      // Send to backend
      chatMutation.mutate(message)
    },
    [chatMutation]
  )

  const handleClearSession = () => {
    if (window.confirm('Clear conversation history? This will start a new session.')) {
      localStorage.removeItem(SESSION_STORAGE_KEY)
      setMessages([])
      window.location.reload() // Reload to get new session ID
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="text-gray-600 hover:text-gray-900 transition"
              >
                ← Back to Home
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Chat with Documents</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">
                Session: <span className="font-mono text-xs">{sessionId.slice(0, 20)}...</span>
              </span>
              <button
                onClick={handleClearSession}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg transition"
              >
                New Session
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col container mx-auto w-full max-w-6xl">
        {/* Messages Area */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <MessageList messages={messages} isLoading={chatMutation.isPending} />
        </div>

        {/* Sources Sidebar (if last message has sources) */}
        {messages.length > 0 &&
          messages[messages.length - 1]?.role === 'assistant' &&
          messages[messages.length - 1]?.sources &&
          messages[messages.length - 1].sources!.length > 0 && (
            <div className="border-t border-gray-200 bg-white p-4 max-h-64 overflow-y-auto">
              <SourceList sources={messages[messages.length - 1].sources!} />
            </div>
          )}

        {/* Input Area */}
        <MessageInput
          onSend={handleSendMessage}
          disabled={chatMutation.isPending}
          placeholder="Ask a question about your documents..."
        />
      </div>

      {/* Error Display */}
      {chatMutation.isError && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg max-w-md">
          <p className="font-medium">Error</p>
          <p className="text-sm">
            {chatMutation.error?.message || 'Failed to send message. Please try again.'}
          </p>
        </div>
      )}
    </div>
  )
}

export default Chat
