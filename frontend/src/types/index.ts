export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string; // ISO 8601 format
  streaming?: boolean;
}

export interface ChatRequest {
  message: string;
  model?: string;
  conversationId?: string;
}

export interface ChatResponse {
  response: string;
  conversationId?: string;
  model?: string;
}

export type WebSocketMessage =
  | { type: 'token'; content: string }
  | { type: 'end' }
  | { type: 'error'; error: string };

export const ALLOWED_OPENAI_MODELS = [
  'gpt-3.5-turbo',
  'gpt-4o',
  'gpt-4o-mini',
] as const;

export type OpenAIModel = typeof ALLOWED_OPENAI_MODELS[number];

export interface FeatureFlags {
  enableWs: boolean;
  enablePdfUpload: boolean;
  enableTeamSharing: boolean;
}
