import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadFile } from '../api/endpoints'

interface FileUploadProps {
  onUploadSuccess?: (taskId: string) => void
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: uploadFile,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      if (onUploadSuccess && data.task_id) {
        onUploadSuccess(data.task_id)
      }
    },
  })

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setUploadedFiles((prev) => [...prev, ...acceptedFiles])

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
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-blue-700">Uploading files...</p>
        </div>
      )}

      {uploadMutation.isError && (
        <div className="mt-4 p-4 bg-red-50 rounded-lg">
          <p className="text-red-700">
            Upload failed: {uploadMutation.error instanceof Error ? uploadMutation.error.message : 'Unknown error'}
          </p>
        </div>
      )}

      {uploadMutation.isSuccess && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-green-700">Files uploaded successfully!</p>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h3>
          <ul className="space-y-1">
            {uploadedFiles.map((file, index) => (
              <li key={index} className="text-sm text-gray-600">
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default FileUpload

