import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, AlertCircle } from 'lucide-react';
import { chatWithAI } from '../services/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant for incident analysis and troubleshooting. Ask me about recent incidents, system metrics, or help with diagnosing issues.',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatWithAI({
        message: inputMessage,
        include_context: true
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        context: response.data.context_used
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.response?.data?.error || 'Failed to get response from AI');
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickQuestions = [
    "What incidents occurred in the last 24 hours?",
    "Show me the most recent high-severity incidents",
    "What remediation actions have been taken recently?",
    "Help me understand the current system status"
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Assistant</h1>
            <p className="text-sm text-gray-400">Powered by Llama 3.2</p>
          </div>
        </div>
      </div>

      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="p-4 bg-gray-800 border-b border-gray-700">
          <p className="text-sm text-gray-400 mb-3">Quick questions to get started:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                className="text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-gray-300 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div className={`flex-shrink-0 ${
              message.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'
            } p-2 rounded-lg`}>
              {message.role === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-white" />
              )}
            </div>
            
            <div className={`flex-1 ${
              message.role === 'user' ? 'text-right' : ''
            }`}>
              <div className={`inline-block max-w-3xl ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.isError
                  ? 'bg-red-900 text-red-200'
                  : 'bg-gray-800 text-gray-200'
              } rounded-lg p-4 shadow-lg`}>
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
                
                {message.context && (
                  <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-gray-400">
                    Context: {message.context.incidents_count} incidents, {message.context.remediations_count} remediations
                  </div>
                )}
              </div>
              
              <p className="text-xs text-gray-500 mt-1">
                {formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="bg-gray-700 p-2 rounded-lg">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-gray-800 rounded-lg p-4 shadow-lg">
              <div className="flex items-center space-x-2">
                <Loader className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-gray-400">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-900 border border-red-700 rounded-lg flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-sm text-red-200">{error}</span>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-700 bg-gray-800 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about incidents, metrics, or troubleshooting..."
            className="flex-1 px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <Send className="w-5 h-5" />
            <span>Send</span>
          </button>
        </form>
        
        <p className="text-xs text-gray-500 mt-2 text-center">
          AI responses are generated based on system context and may not always be accurate
        </p>
      </div>
    </div>
  );
};

export default ChatPage;
