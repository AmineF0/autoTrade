import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Loader2, Maximize2, Minimize2 } from 'lucide-react';
import { Role } from '../types';
import { queryAssistant } from '../utils/api';
import toast from 'react-hot-toast';
import { MarkdownMessage } from './MarkdownMessage';

interface ChatProps {
  role: Role;
}

export function Chat({ role }: ChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    const { response, error } = await queryAssistant(userMessage, role);
    
    if (error) {
      toast.error(error);
    } else {
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    }
    
    setIsLoading(false);
  };

  return (
    <>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(true)}
        className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
      >
        <MessageCircle className="w-6 h-6" />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className={`fixed ${
              isMaximized 
                ? 'inset-4 max-w-none'
                : 'bottom-20 right-6 w-[40rem]'
            } bg-white dark:bg-gray-800 rounded-lg shadow-xl transition-all duration-300 flex flex-col`}
          >
            <div className="flex justify-between items-center p-4 border-b dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">EcoSense Assistant</h3>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => setIsMaximized(!isMaximized)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 p-1"
                >
                  {isMaximized ? (
                    <Minimize2 className="w-5 h-5" />
                  ) : (
                    <Maximize2 className="w-5 h-5" />
                  )}
                </button>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 p-1"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className={`${
              isMaximized ? 'flex-1' : 'h-[40rem]'
            } overflow-y-auto p-4 space-y-4`}>
              {messages.length === 0 && (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <p>Welcome! How can I assist you today?</p>
                  <p className="text-sm mt-2">Ask me anything about the sensor data or departments.</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={i}
                  className={`p-4 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-100 dark:bg-blue-900 ml-12'
                      : 'bg-gray-100 dark:bg-gray-700 mr-12'
                  }`}
                >
                  <div className="flex items-start">
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold mr-2">
                        AI
                      </div>
                    )}
                    <div className={`flex-1 ${
                      msg.role === 'user' ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-gray-100'
                    }`}>
                      <MarkdownMessage content={msg.content} />
                    </div>
                  </div>
                </motion.div>
              ))}
              {isLoading && (
                <div className="flex justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-blue-600 dark:text-blue-400" />
                </div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="p-4 border-t dark:border-gray-700">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question..."
                  className="flex-1 px-4 py-2 border dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  disabled={isLoading}
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  type="submit"
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </motion.button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}