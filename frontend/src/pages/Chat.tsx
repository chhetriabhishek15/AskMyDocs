import { useState } from 'react'

const Chat: React.FC = () => {
  const [message, setMessage] = useState('')

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Chat</h1>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <p className="text-gray-500">Chat interface - to be implemented</p>
          </div>
          
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat


