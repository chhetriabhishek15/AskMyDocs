import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import DocumentList from '../components/DocumentList'

const Home: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Tiramai RAG System
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Upload documents and chat with AI-powered retrieval
            </p>
            <button
              onClick={() => navigate('/chat')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-md"
            >
              Go to Chat
            </button>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column: File Upload */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Upload Documents
              </h2>
              <p className="text-gray-600 mb-6">
                Upload PDFs, DOCX files, ZIP archives, or text files. The system will
                automatically process and index them for retrieval.
              </p>
              <FileUpload />
            </div>

            {/* Right Column: Document List */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Your Documents
              </h2>
              <DocumentList />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home


