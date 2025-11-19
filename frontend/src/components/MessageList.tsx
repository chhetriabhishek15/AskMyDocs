/**
 * MessageList component - Displays conversation messages.
 */
import { useEffect, useRef } from 'react'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    chunk_id: string
    document_id: string
    document_filename: string
    similarity_score: number
    preview: string
  }>
  timestamp?: string
}

interface MessageListProps {
  messages: Message[]
  isLoading?: boolean
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">Start a conversation</p>
          <p className="text-sm">Ask questions about your uploaded documents</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-3xl rounded-lg px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-900'
            }`}
          >
            <div className="whitespace-pre-wrap break-words">{message.content}</div>
            
            {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-300">
                <p className="text-xs text-gray-600 mb-2 font-semibold">Sources:</p>
                <div className="space-y-1">
                  {(() => {
                    // Deduplicate sources by document_id - keep only top chunk per document
                    const deduplicated = message.sources.reduce((acc, source) => {
                      const existing = acc.find((s) => s.document_id === source.document_id)
                      if (!existing || source.similarity_score > existing.similarity_score) {
                        if (existing) {
                          const index = acc.indexOf(existing)
                          acc[index] = source
                        } else {
                          acc.push(source)
                        }
                      }
                      return acc
                    }, [] as typeof message.sources)
                    
                    // Sort by similarity and take top 3
                    deduplicated.sort((a, b) => b.similarity_score - a.similarity_score)
                    
                    return deduplicated.slice(0, 3).map((source, idx) => (
                      <div key={source.chunk_id} className="text-xs text-gray-600">
                        <span className="font-medium">{idx + 1}.</span> {source.document_filename}{' '}
                        <span className="text-gray-500">
                          ({(source.similarity_score * 100).toFixed(0)}% relevant)
                        </span>
                      </div>
                    ))
                  })()}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg px-4 py-3">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-sm text-gray-600">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList

