import React, { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ModelPicker } from './ModelPicker';
import { FeatureToggle } from './FeatureToggle';
import { useHttpChat } from '@/hooks/useHttpChat';
import { useWsChat } from '@/hooks/useWsChat';
import type { OpenAIModel, FeatureFlags } from '@/types';
import { t } from '@/lib/i18n';

export const ChatBox: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [selectedModel, setSelectedModel] = useState<OpenAIModel>('gpt-3.5-turbo');
  const [useWebSocket, setUseWebSocket] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const httpChat = useHttpChat();
  const wsChat = useWsChat(() => {
    // Fallback to HTTP if WebSocket fails
    setUseWebSocket(false);
  });

  const activeChat = useWebSocket ? wsChat : httpChat;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeChat.messages]);

  const handleFlagsChange = (flags: FeatureFlags) => {
    setUseWebSocket(flags.enableWs && wsChat.isConnected);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || activeChat.isLoading) return;

    await activeChat.sendMessage(inputText, selectedModel);
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-indigo-50" dir="rtl">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-indigo-600">DocuChat</h1>
            <div className="flex items-center gap-4">
              <ModelPicker
                currentModel={selectedModel}
                onModelChange={setSelectedModel}
              />
              {useWebSocket && wsChat.isConnected && (
                <span className="text-xs text-green-600 flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  {t('connected')}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden max-w-6xl mx-auto w-full">
        {/* Messages Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-6">
            {activeChat.messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-6xl mb-4">💬</div>
                  <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                    {t('welcome')}
                  </h2>
                  <p className="text-gray-500">
                    پیام خود را تایپ کرده و با دستیار هوشمند گفتگو کنید
                  </p>
                </div>
              </div>
            ) : (
              <>
                {activeChat.messages.map(message => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 bg-white p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={t('placeholder')}
                className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                rows={1}
                dir="rtl"
                disabled={activeChat.isLoading}
              />
              <button
                type="submit"
                disabled={activeChat.isLoading || !inputText.trim()}
                className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {activeChat.isLoading ? t('loading') : t('send')}
              </button>
            </form>
            
            {activeChat.error && (
              <div className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg" dir="rtl">
                {t('error')}: {activeChat.error}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <aside className="hidden lg:block w-80 border-r border-gray-200 bg-white p-4 overflow-y-auto">
          <FeatureToggle onFlagsChange={handleFlagsChange} />
          
          <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
            <h3 className="text-sm font-semibold text-indigo-900 mb-2">
              راهنما
            </h3>
            <ul className="text-xs text-indigo-700 space-y-1">
              <li>• از مدل‌های OpenAI استفاده کنید</li>
              <li>• پیام‌ها به صورت لحظه‌ای ارسال می‌شوند</li>
              <li>• برای خط جدید از Shift+Enter استفاده کنید</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
};
