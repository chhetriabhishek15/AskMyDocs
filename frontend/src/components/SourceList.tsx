/**
 * SourceList component - Displays source citations with expandable previews.
 */
import { useState } from 'react'
import { SourceInfo } from '../api/endpoints'

interface SourceListProps {
  sources: SourceInfo[]
  className?: string
}

const SourceList: React.FC<SourceListProps> = ({ sources, className = '' }) => {
  const [expandedSource, setExpandedSource] = useState<string | null>(null)

  if (!sources || sources.length === 0) {
    return null
  }

  // Deduplicate sources by document_id - keep only the top chunk per document
  const deduplicatedSources = sources.reduce((acc, source) => {
    const existing = acc.find((s) => s.document_id === source.document_id)
    if (!existing || source.similarity_score > existing.similarity_score) {
      // Replace with this source if it has higher similarity
      if (existing) {
        const index = acc.indexOf(existing)
        acc[index] = source
      } else {
        acc.push(source)
      }
    }
    return acc
  }, [] as SourceInfo[])

  // Sort by similarity score (highest first)
  deduplicatedSources.sort((a, b) => b.similarity_score - a.similarity_score)

  return (
    <div className={`${className}`}>
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Sources ({deduplicatedSources.length} document{deduplicatedSources.length !== 1 ? 's' : ''})
      </h3>
      <div className="space-y-2">
        {deduplicatedSources.map((source, index) => {
          const isExpanded = expandedSource === source.chunk_id
          
          return (
            <div
              key={source.chunk_id}
              className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-500">#{index + 1}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {source.document_filename}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({(source.similarity_score * 100).toFixed(0)}% relevant)
                    </span>
                  </div>
                  {isExpanded ? (
                    <div className="mt-2">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap break-words">
                        {source.preview}
                      </p>
                      <button
                        onClick={() => setExpandedSource(null)}
                        className="text-xs text-blue-600 hover:text-blue-800 mt-2"
                      >
                        Show less
                      </button>
                    </div>
                  ) : (
                    <p className="text-xs text-gray-600 line-clamp-2">{source.preview}</p>
                  )}
                </div>
                {!isExpanded && (
                  <button
                    onClick={() => setExpandedSource(source.chunk_id)}
                    className="text-xs text-blue-600 hover:text-blue-800 ml-2 flex-shrink-0"
                  >
                    Show more
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SourceList

