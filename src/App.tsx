import React, { useState } from 'react';
import { Conversation } from './types';
import { ChatInterface } from './components/ChatInterface';
import { ConversationList } from './components/ConversationList';
import { websocketService } from './services/websocket';

function App() {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  React.useEffect(() => {
    // Set up WebSocket connection status monitoring
    websocketService.onConnection((connected) => {
      setIsConnected(connected);
    });

    // Connect to WebSocket
    websocketService.connect().catch(console.error);

    // Start periodic ping to keep connection alive
    websocketService.startPeriodicPing();

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const handleConversationSelect = (conversation: Conversation) => {
    setSelectedConversation(conversation);
  };

  const handleConversationChange = (conversation: Conversation) => {
    setSelectedConversation(conversation);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">增强多模态LLM Agent</h1>
            <span className="text-sm text-gray-500">Enhanced Multimodal LLM Assistant</span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Connection status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Model selector */}
            <select className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-vision-preview">GPT-4 Vision</option>
            </select>

            {/* Settings button */}
            <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors">
              ⚙️
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <ConversationList
          selectedConversationId={selectedConversation?.id}
          onConversationSelect={handleConversationSelect}
          onConversationCreate={() => {
            // This could trigger a refresh or other action
          }}
        />

        {/* Chat area */}
        <div className="flex-1 p-4">
          <ChatInterface
            conversationId={selectedConversation?.id}
            onConversationChange={handleConversationChange}
          />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>
            增强多模态LLM Agent v2.0.0 | Memory, RAG, Multi-Agent, Text, Images, Voice
          </div>
          <div className="flex items-center space-x-4">
            <span>Client ID: {websocketService.getClientId()}</span>
            <span>© 2024 LLM Agent</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
