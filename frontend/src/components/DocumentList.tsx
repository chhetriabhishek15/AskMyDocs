import { useQuery } from '@tanstack/react-query'
import { listDocuments, Document } from '../api/endpoints'

const DocumentList: React.FC = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: () => listDocuments(1, 20),
    retry: false, // Don't retry on error to avoid blocking the UI
  })

  // Debug: log the data structure
  if (data) {
    console.log('DocumentList data:', data)
  }

  if (isLoading) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading documents...
      </div>
    )
  }

  if (error) {
    console.error('DocumentList error:', error)
    return (
      <div className="p-4 bg-red-50 rounded-lg">
        <p className="text-red-700">
          Error loading documents: {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    )
  }

  if (!data || !data.items || data.items.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        No documents uploaded yet. Upload your first document to get started!
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Uploaded Documents ({data.total || 0})
      </h3>
      <div className="space-y-2">
        {data.items.map((doc: Document) => (
          <div
            key={doc.id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(doc.created_at).toLocaleDateString()} • {doc.chunk_count} chunks
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DocumentList

