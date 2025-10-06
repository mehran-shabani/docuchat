import React from 'react';
import type { Message } from '@/types';
import { t } from '@/lib/i18n';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div
      className={`flex w-full mb-4 ${isUser ? 'justify-start' : 'justify-end'}`}
      dir="rtl"
    >
      <div
        className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-md ${
          isUser
            ? 'bg-indigo-600 text-white rounded-tr-sm'
            : 'bg-white text-gray-800 border border-gray-200 rounded-tl-sm'
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium opacity-75">
            {isUser ? t('user') : t('assistant')}
          </span>
          {message.streaming && (
            <span className="text-xs opacity-75 animate-pulse">
              {t('typing')}
            </span>
          )}
        </div>
        <div className="text-sm md:text-base leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
          {message.streaming && (
            <span className="inline-block w-1 h-4 bg-current ml-1 animate-pulse" />
          )}
        </div>
        <div className="text-xs opacity-60 mt-2 text-left">
          <span dir="ltr" style={{ unicodeBidi: 'isolate' }}>
            {new Date(message.timestamp).toLocaleTimeString('fa-IR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>
    </div>
  );
};
