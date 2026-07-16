'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Send,
  Loader2,
} from 'lucide-react';
import { sendChatMessage, type ChatMessage } from '../lib/aiApi';
import MarkdownRenderer from './MarkdownRenderer';

interface LearningAssistantProps {
  lessonContext?: string;
  isOpen: boolean;
  onClose: () => void;
}

const QUICK_ACTIONS = [
  { label: 'Explain this', prompt: 'Can you explain this concept to me in a simple way?' },
  { label: 'Give a hint', prompt: 'Give me a hint for this topic without giving away the answer.' },
  { label: 'More examples', prompt: 'Can you give me more examples of this concept?' },
  { label: 'Simplify', prompt: 'Can you simplify this topic? I find it confusing.' },
];

export default function LearningAssistant({
  lessonContext,
  isOpen,
  onClose,
}: LearningAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hi! I'm Atlas, your AI learning assistant. I can help explain concepts, give hints, or provide examples. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      const userMessage: ChatMessage = { role: 'user', content: text.trim() };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);
      setShowQuickActions(false);

      try {
        const history = messages.map((m) => ({
          role: m.role,
          content: m.content,
        }));

        const response = await sendChatMessage(text, history, lessonContext);
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response },
        ]);
      } catch (error) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content:
              "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, isLoading, lessonContext]
  );

  const handleQuickAction = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          className="fixed bottom-4 right-4 z-50 w-[380px] max-w-[calc(100vw-32px)] bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-[#4F46E5] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs">A</span>
              </div>
              <div>
                <p className="text-sm font-bold text-[#1E293B]">Atlas AI</p>
                <p className="text-[10px] text-[#4F46E5]/80">Learning Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-[#4F46E5] rounded-full animate-pulse" />
              <button
                onClick={onClose}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors text-gray-400 hover:text-[#1E293B]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="h-[400px] overflow-y-auto p-4 space-y-3 scrollbar-thin">
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className={`flex items-start gap-2.5 ${
                  msg.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'assistant'
                      ? 'bg-[#EEF2FF] border border-[#C7D2FE]'
                      : 'bg-[#FFFBEB] border border-[#FDE68A]'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <span className="text-[10px] font-bold text-[#4F46E5]">AI</span>
                  ) : (
                    <span className="text-[10px] font-bold">You</span>
                  )}
                </div>

                <div
                  className={`max-w-[85%] px-3.5 py-2.5 rounded-xl text-sm leading-relaxed ${
                    msg.role === 'assistant'
                      ? 'bg-gray-50 border border-gray-100 text-[#1E293B]'
                      : 'bg-[#EEF2FF] border border-[#C7D2FE] text-[#1E293B]'
                  }`}
                >
                  {msg.role === 'user' ? (
                    msg.content
                  ) : (
                    <MarkdownRenderer content={msg.content} compact />
                  )}
                </div>
              </motion.div>
            ))}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-start gap-2.5"
              >
                <div className="w-7 h-7 rounded-lg bg-[#EEF2FF] border border-[#C7D2FE] flex items-center justify-center flex-shrink-0">
                  <span className="text-[10px] font-bold text-[#4F46E5]">AI</span>
                </div>
                <div className="bg-gray-50 border border-gray-100 rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-[#4F46E5] animate-spin" />
                    <span className="text-sm text-gray-400">Thinking...</span>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {showQuickActions && messages.length <= 1 && (
            <div className="px-4 pb-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2 font-medium">
                Quick actions
              </p>
              <div className="grid grid-cols-2 gap-1.5">
                {QUICK_ACTIONS.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleQuickAction(action.prompt)}
                    className="px-2.5 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-xs text-gray-600 hover:text-gray-800 transition-all"
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="p-3 border-t border-gray-100">
            <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2 focus-within:border-[#4F46E5] transition-all shadow-sm">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') sendMessage(input);
                }}
                placeholder="Ask Atlas anything..."
                className="flex-1 bg-transparent text-sm text-[#1E293B] placeholder-gray-400 outline-none"
                disabled={isLoading}
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || isLoading}
                className="p-1.5 bg-[#4F46E5] text-white rounded-lg hover:bg-[#4338CA] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] text-gray-400 mt-1.5 text-center">
              Powered by Gemini AI
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
