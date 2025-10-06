export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
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

export interface WebSocketMessage {
  type: 'token' | 'end' | 'error';
  content?: string;
  error?: string;
}

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
