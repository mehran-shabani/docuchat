"""RAG prompt construction service"""

from typing import List, Tuple

from app.services.chunker import count_tokens
from app.core.config import get_settings

settings = get_settings()


def build_rag_prompt(
    user_question: str,
    retrieved_chunks: List[Tuple[str, int, str]],
    max_tokens: int = None
) -> Tuple[str, str]:
    """
    Build system and user prompts for RAG
    
    Args:
        user_question: User's question
        retrieved_chunks: List of (chunk_text, page, title) tuples
        max_tokens: Maximum tokens for context (from settings if not provided)
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    if max_tokens is None:
        max_tokens = settings.MAX_CONTEXT_TOKENS
    
    # Build retrieved documents context
    context_parts = []
    current_tokens = 0
    
    for chunk_text, page, title in retrieved_chunks:
        chunk_context = f"[سند: {title} - صفحه {page}]\n{chunk_text}\n"
        chunk_tokens = count_tokens(chunk_context)
        
        # Check if adding this chunk exceeds max tokens
        if current_tokens + chunk_tokens > max_tokens * 0.7:  # Reserve 30% for question and system prompt
            break
        
        context_parts.append(chunk_context)
        current_tokens += chunk_tokens
    
    retrieved_context = "\n".join(context_parts)
    
    # System prompt in Farsi
    system_prompt = """شما دستیار هوشمند پاسخ‌دهی بر پایه اسناد PDF فارسی هستید.
وظیفه شما پاسخ دقیق و کامل به سؤالات کاربر بر اساس اطلاعات موجود در اسناد بازیابی‌شده است.

قوانین:
- فقط از اطلاعات موجود در اسناد بازیابی‌شده استفاده کنید
- اگر پاسخ در اسناد نیست، صادقانه اعلام کنید که اطلاعات کافی ندارید
- پاسخ‌های خود را واضح، دقیق و به زبان فارسی ارائه دهید
- در صورت امکان، به سند و صفحه مرجع اشاره کنید"""
    
    # User prompt with context and question
    user_prompt = f"""اسناد بازیابی‌شده:

{retrieved_context}

پرسش کاربر:
{user_question}"""
    
    return system_prompt, user_prompt
