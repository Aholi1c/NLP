import React, { useState, useEffect, useRef } from 'react';
import { Message, Conversation, ChatRequest, FeatureToggle } from '../types';
import { chatAPI, enhancedChatAPI } from '../services/api';
import { websocketService } from '../services/websocket';
import { FeaturePanel } from './FeaturePanel';

interface ChatInterfaceProps {
  conversationId?: number;
  onConversationChange?: (conversation: Conversation) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  onConversationChange,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [features, setFeatures] = useState<FeatureToggle>({
    useMemory: true,
    useRAG: false,
    useAgentCollaboration: false,
    selectedKnowledgeBases: [],
    selectedAgents: [],
    collaborationType: 'sequential'
  });
  const [showFeaturePanel, setShowFeaturePanel] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load conversation messages if conversationId is provided
    if (conversationId) {
      loadConversationMessages(conversationId);
    }

    // Set up WebSocket event handlers
    websocketService.onMessage('chat_start', (data) => {
      setIsTyping(true);
      setCurrentResponse('');
    });

    websocketService.onMessage('chat_chunk', (data) => {
      setCurrentResponse(prev => prev + data.content);
    });

    websocketService.onMessage('chat_complete', (data) => {
      setIsTyping(false);
      setCurrentResponse('');
      if (onConversationChange && data.conversation_id) {
        // Refresh conversation
        loadConversationMessages(data.conversation_id);
      }
    });

    websocketService.onMessage('processing', (data) => {
      setIsLoading(true);
    });

    websocketService.onMessage('error', (data) => {
      setIsLoading(false);
      setIsTyping(false);
      alert(data.message);
    });

    // Connect to WebSocket
    websocketService.connect().catch(console.error);

    return () => {
      // Clean up WebSocket handlers
      websocketService.offMessage('chat_start');
      websocketService.offMessage('chat_chunk');
      websocketService.offMessage('chat_complete');
      websocketService.offMessage('processing');
      websocketService.offMessage('error');
      websocketService.disconnect();
    };
  }, [conversationId, onConversationChange]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  const loadConversationMessages = async (convId: number) => {
    try {
      const conversationMessages = await chatAPI.getConversationMessages(convId);
      setMessages(conversationMessages);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !selectedFile) return;

    // Check if any advanced features are enabled
    const useEnhancedChat = features.useMemory || features.useRAG || features.useAgentCollaboration;

    if (useEnhancedChat) {
      await handleEnhancedSendMessage();
    } else {
      await handleRegularSendMessage();
    }
  };

  const handleRegularSendMessage = async () => {
    const request: ChatRequest = {
      message: inputMessage,
      conversation_id: conversationId,
      message_type: selectedFile ? 'image' : 'text',
      model: 'gpt-3.5-turbo',
    };

    // Add user message to the list
    const userMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 0,
      role: 'user',
      content: inputMessage,
      message_type: selectedFile ? 'image' : 'text',
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    setInputMessage('');
    setSelectedFile(null);

    try {
      if (selectedFile) {
        // Send with file upload
        const formData = new FormData();
        formData.append('message', request.message);
        if (request.conversation_id) {
          formData.append('conversation_id', request.conversation_id.toString());
        }
        formData.append('model', request.model);
        formData.append('file', selectedFile);

        const response = await chatAPI.sendMessageWithFile(formData);

        // Add assistant response
        const assistantMessage: Message = {
          id: response.message_id,
          conversation_id: response.conversation_id,
          role: 'assistant',
          content: response.response,
          message_type: 'text',
          created_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        if (onConversationChange) {
          const conversation = await chatAPI.getConversation(response.conversation_id);
          onConversationChange(conversation);
        }
      } else {
        // Send via WebSocket for streaming
        websocketService.sendChatMessage(
          request.message,
          request.conversation_id,
          request.model
        );
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    }
  };

  const handleEnhancedSendMessage = async () => {
    const enhancedRequest = {
      message: inputMessage,
      conversation_id: conversationId,
      message_type: selectedFile ? 'image' : 'text',
      model: 'gpt-3.5-turbo',
      use_memory: features.useMemory,
      use_rag: features.useRAG,
      knowledge_base_ids: features.selectedKnowledgeBases.length > 0 ? features.selectedKnowledgeBases : undefined,
      agent_collaboration: features.useAgentCollaboration,
      collaboration_type: features.collaborationType,
      agents: features.selectedAgents.length > 0 ? features.selectedAgents : undefined,
    };

    // Add user message to the list
    const userMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 0,
      role: 'user',
      content: inputMessage,
      message_type: selectedFile ? 'image' : 'text',
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    setInputMessage('');
    setSelectedFile(null);
    setIsLoading(true);

    try {
      const response = await enhancedChatAPI.sendEnhancedMessage(enhancedRequest);

      // Add assistant response
      const assistantMessage: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.response,
        message_type: 'text',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      if (onConversationChange) {
        const conversation = await chatAPI.getConversation(response.conversation_id);
        onConversationChange(conversation);
      }
    } catch (error) {
      console.error('Failed to send enhanced message:', error);
      alert('Failed to send enhanced message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeatureChange = (newFeatures: FeatureToggle) => {
    setFeatures(newFeatures);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
        setSelectedFile(audioFile);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Feature panel toggle */}
      <div className="border-b p-2 flex justify-between items-center">
        <button
          onClick={() => setShowFeaturePanel(!showFeaturePanel)}
          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
        >
          {showFeaturePanel ? 'Hide Features' : 'Show Advanced Features'}
        </button>
        <div className="text-xs text-gray-500">
          {features.useMemory && '🧠 Memory '}
          {features.useRAG && '📚 RAG '}
          {features.useAgentCollaboration && '🤖 Agents'}
        </div>
      </div>

      {/* Feature panel */}
      {showFeaturePanel && (
        <div className="border-b">
          <FeaturePanel
            onFeatureChange={handleFeatureChange}
            sessionId={sessionId}
          />
        </div>
      )}

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`message-bubble ${
                message.role === 'user' ? 'message-user' : 'message-assistant'
              } slide-in`}
            >
              {message.message_type === 'image' && message.media_url && (
                <img
                  src={message.media_url}
                  alt="Uploaded content"
                  className="max-w-full h-auto mb-2 rounded"
                />
              )}
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className="text-xs mt-1 opacity-75">
                {new Date(message.created_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="message-bubble message-assistant">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              {currentResponse && (
                <div className="mt-2 whitespace-pre-wrap">{currentResponse}</div>
              )}
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center">
            <div className="text-gray-500">Processing...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t p-4">
        {selectedFile && (
          <div className="mb-2 p-2 bg-gray-100 rounded flex items-center justify-between">
            <span className="text-sm">{selectedFile.name}</span>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}

        <div className="flex items-end space-x-2">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={1}
              disabled={isLoading || recording}
            />
          </div>

          <div className="flex space-x-2">
            {/* File upload button */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*,audio/*"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Upload file"
            >
              📎
            </button>

            {/* Voice recording button */}
            <button
              onClick={recording ? stopRecording : startRecording}
              className={`p-3 rounded-lg transition-colors ${
                recording
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              title={recording ? 'Stop recording' : 'Start recording'}
            >
              {recording ? '⏹️' : '🎤'}
            </button>

            {/* Send button */}
            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!inputMessage.trim() && !selectedFile)}
              className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};