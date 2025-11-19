import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadFile, UploadResponse } from '../api/endpoints'
import UploadProgress from './UploadProgress'

interface FileUploadProps {
  onUploadSuccess?: (taskId: string) => void
}

interface UploadTask {
  taskId: string
  filename: string
  file: File
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([])
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: uploadFile,
    onSuccess: (data: UploadResponse, file: File) => {
      // Add task to tracking list
      setUploadTasks((prev) => [
        ...prev,
        {
          taskId: data.task_id,
          filename: file.name,
          file: file,
        },
      ])

      if (onUploadSuccess && data.task_id) {
        onUploadSuccess(data.task_id)
      }
    },
  })

  const handleUploadComplete = (taskId: string) => {
    // Refresh documents list when upload completes
    queryClient.invalidateQueries({ queryKey: ['documents'] })
    // Note: Auto-removal is handled by UploadProgress component
  }

  const handleDismissTask = (taskId: string) => {
    setUploadTasks((prev) => prev.filter((task) => task.taskId !== taskId))
  }

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      // Upload each file
      for (const file of acceptedFiles) {
        try {
          await uploadMutation.mutateAsync(file)
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error)
        }
      }
    },
    [uploadMutation]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/zip': ['.zip'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: true,
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center">
          <svg
            className="w-12 h-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          {isDragActive ? (
            <p className="text-blue-600 font-medium">Drop files here...</p>
          ) : (
            <>
              <p className="text-gray-600 mb-2">
                Drag and drop files here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports: PDF, DOCX, DOC, ZIP, TXT, MD
              </p>
            </>
          )}
        </div>
      </div>

      {uploadMutation.isPending && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-blue-700 text-sm">Uploading files...</p>
        </div>
      )}

      {uploadMutation.isError && (
        <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-700 text-sm">
            Upload failed: {uploadMutation.error instanceof Error ? uploadMutation.error.message : 'Unknown error'}
          </p>
        </div>
      )}

      {/* Upload Progress for each file */}
      {uploadTasks.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Processing {uploadTasks.length} file{uploadTasks.length > 1 ? 's' : ''}...
          </h3>
          <div className="space-y-2">
            {uploadTasks.map((task) => (
              <UploadProgress
                key={task.taskId}
                taskId={task.taskId}
                filename={task.filename}
                onComplete={(documentId) => handleUploadComplete(task.taskId)}
                onError={(error) => console.error(`Task ${task.taskId} error:`, error)}
                onDismiss={() => handleDismissTask(task.taskId)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload

