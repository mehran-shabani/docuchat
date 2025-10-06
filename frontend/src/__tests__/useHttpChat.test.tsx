import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useHttpChat } from '@/hooks/useHttpChat';

// Mock fetch
global.fetch = vi.fn();

describe('useHttpChat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with empty messages', () => {
    const { result } = renderHook(() => useHttpChat());
    
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('sends message and receives response', async () => {
    const mockResponse = { response: 'سلام! چطور می‌توانم کمکتان کنم؟' };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useHttpChat());
    
    await result.current.sendMessage('سلام');
    
    await waitFor(() => {
      expect(result.current.messages.length).toBe(2);
      expect(result.current.messages[0].content).toBe('سلام');
      expect(result.current.messages[1].content).toBe(mockResponse.response);
    });
  });

  it('handles errors correctly', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useHttpChat());
    
    await result.current.sendMessage('test');
    
    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('clears messages when clearMessages is called', async () => {
    const mockResponse = { response: 'پاسخ' };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useHttpChat());
    
    await result.current.sendMessage('سلام');
    
    await waitFor(() => {
      expect(result.current.messages.length).toBeGreaterThan(0);
    });
    
    result.current.clearMessages();
    
    await waitFor(() => {
      expect(result.current.messages).toEqual([]);
      expect(result.current.error).toBeNull();
    });
  });

  it('does not send empty messages', async () => {
    const { result } = renderHook(() => useHttpChat());
    
    await result.current.sendMessage('   ');
    
    expect(result.current.messages).toEqual([]);
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
