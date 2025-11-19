/**
 * UploadProgress component - Shows progress for a single file upload.
 */
import { useEffect, useState } from 'react'
import { getTaskStatus, TaskStatusResponse } from '../api/endpoints'

interface UploadProgressProps {
  taskId: string
  filename: string
  onComplete?: (documentId: string | null) => void
  onError?: (error: string) => void
  onDismiss?: () => void
}

const UploadProgress: React.FC<UploadProgressProps> = ({
  taskId,
  filename,
  onComplete,
  onError,
  onDismiss,
}) => {
  const [status, setStatus] = useState<TaskStatusResponse | null>(null)
  const [isPolling, setIsPolling] = useState(true)

  useEffect(() => {
    let pollInterval: NodeJS.Timeout | null = null
    let autoRemoveTimeout: NodeJS.Timeout | null = null

    const pollStatus = async () => {
      try {
        const taskStatus = await getTaskStatus(taskId)
        setStatus(taskStatus)

        // Stop polling if completed or failed
        if (taskStatus.status === 'completed' || taskStatus.status === 'failed') {
          setIsPolling(false)
          if (taskStatus.status === 'completed' && onComplete) {
            onComplete(taskStatus.document_id || null)
            // Auto-remove successful uploads after 3 seconds
            autoRemoveTimeout = setTimeout(() => {
              if (onDismiss) {
                onDismiss()
              }
            }, 3000)
          }
          if (taskStatus.status === 'failed' && onError) {
            onError(taskStatus.error || 'Processing failed')
            // Auto-remove failed uploads after 10 seconds
            autoRemoveTimeout = setTimeout(() => {
              if (onDismiss) {
                onDismiss()
              }
            }, 10000)
          }
        }
      } catch (error) {
        console.error('Error polling task status:', error)
        setIsPolling(false)
        if (onError) {
          onError(error instanceof Error ? error.message : 'Failed to get status')
        }
        // Auto-remove on error after 10 seconds
        autoRemoveTimeout = setTimeout(() => {
          if (onDismiss) {
            onDismiss()
          }
        }, 10000)
      }
    }

    // Initial poll
    pollStatus()

    // Poll every 1 second if still processing
    if (isPolling) {
      pollInterval = setInterval(pollStatus, 1000)
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
      if (autoRemoveTimeout) {
        clearTimeout(autoRemoveTimeout)
      }
    }
  }, [taskId, isPolling, onComplete, onError, onDismiss])

  if (!status) {
    return (
      <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">{filename}</span>
          <span className="text-xs text-gray-500">Initializing...</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-gray-300 h-2 rounded-full" style={{ width: '10%' }}></div>
        </div>
      </div>
    )
  }

  const progressPercent = Math.round(status.progress * 100)
  const isCompleted = status.status === 'completed'
  const isFailed = status.status === 'failed'
  const isProcessing = status.status === 'processing' || status.status === 'queued'

  return (
    <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700 truncate flex-1 mr-2">
          {filename}
        </span>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs font-medium ${
              isCompleted
                ? 'text-green-600'
                : isFailed
                ? 'text-red-600'
                : 'text-blue-600'
            }`}
          >
            {isCompleted
              ? '✓ Completed'
              : isFailed
              ? '✗ Failed'
              : isProcessing
              ? `${progressPercent}%`
              : status.status}
          </span>
          {/* Dismiss button for completed or failed uploads */}
          {(isCompleted || isFailed) && onDismiss && (
            <button
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Dismiss"
              aria-label="Dismiss"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            isCompleted
              ? 'bg-green-500'
              : isFailed
              ? 'bg-red-500'
              : 'bg-blue-500'
          }`}
          style={{ width: `${progressPercent}%` }}
        ></div>
      </div>

      {/* Status Message */}
      <p
        className={`text-xs ${
          isCompleted
            ? 'text-green-700'
            : isFailed
            ? 'text-red-700'
            : 'text-gray-600'
        }`}
      >
        {status.message || status.status}
      </p>

      {/* Error Message */}
      {isFailed && status.error && (
        <p className="text-xs text-red-600 mt-1">{status.error}</p>
      )}

      {/* Loading Indicator */}
      {isProcessing && (
        <div className="flex items-center gap-1 mt-1">
          <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse"></div>
          <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
        </div>
      )}
    </div>
  )
}

export default UploadProgress

