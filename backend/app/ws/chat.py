"""WebSocket chat handler with RAG and streaming"""

import json
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.db.session import async_session_maker
from app.core.security import verify_token
from app.core.config import get_settings
from app.models.chat import ChatSession, Message
from app.services.retriever import retrieve_relevant_chunks
from app.services.rag import build_rag_prompt
from app.services.chunker import count_tokens
from app.services.tokens_meter import record_token_usage

settings = get_settings()

# Initialize OpenAI client
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
)


async def authenticate_websocket(
    websocket: WebSocket,
    token: Optional[str],
    tenant_id: Optional[str]
) -> Optional[dict]:
    """
    Authenticate WebSocket connection
    
    Args:
        websocket: WebSocket connection
        token: JWT token from query or header
        tenant_id: Tenant ID from header
    
    Returns:
        User info dict or None if authentication fails
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return None
    
    if not tenant_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing tenant ID")
        return None
    
    try:
        # Verify token
        payload = verify_token(token.replace("Bearer ", ""))
        user_id = payload.get("sub")
        token_tenant_id = payload.get("tenant_id")
        
        if not user_id or not token_tenant_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return None
        
        # Verify tenant matches
        if str(token_tenant_id) != tenant_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Tenant mismatch")
            return None
        
        return {
            "user_id": user_id,
            "tenant_id": int(tenant_id)
        }
        
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
        return None


async def handle_chat_message(
    websocket: WebSocket,
    message: str,
    user_info: dict,
    session_id: Optional[int] = None
):
    """
    Handle a chat message with RAG and streaming
    
    Args:
        websocket: WebSocket connection
        message: User message
        user_info: User authentication info
        session_id: Optional existing session ID
    """
    async with async_session_maker() as session:
        try:
            # Create or get chat session
            if not session_id:
                chat_session = ChatSession(
                    tenant_id=user_info["tenant_id"],
                    user_id=user_info["user_id"]
                )
                session.add(chat_session)
                await session.commit()
                await session.refresh(chat_session)
                session_id = chat_session.id
            
            # Send start message
            await websocket.send_json({
                "type": "start",
                "session_id": session_id
            })
            
            # Retrieve relevant chunks
            chunks = await retrieve_relevant_chunks(
                message,
                user_info["tenant_id"],
                session
            )
            
            # Build RAG prompt
            system_prompt, user_prompt = build_rag_prompt(message, chunks)
            
            # Validate model
            if settings.OPENAI_MODEL not in settings.ALLOWED_MODELS:
                raise ValueError(f"Model {settings.OPENAI_MODEL} not allowed")
            
            # Stream response from OpenAI
            response_text = ""
            tokens_in = count_tokens(system_prompt + user_prompt, settings.OPENAI_MODEL)
            tokens_out = 0
            
            stream = await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_text += token
                    
                    # Send delta to client
                    await websocket.send_json({
                        "type": "delta",
                        "token": token
                    })
            
            # Count output tokens
            tokens_out = count_tokens(response_text, settings.OPENAI_MODEL)
            
            # Save messages to database
            user_message = Message(
                session_id=session_id,
                role="user",
                content=message,
                tokens_in=tokens_in,
                tokens_out=0
            )
            
            assistant_message = Message(
                session_id=session_id,
                role="assistant",
                content=response_text,
                tokens_in=0,
                tokens_out=tokens_out
            )
            
            session.add(user_message)
            session.add(assistant_message)
            await session.commit()
            
            # Record usage
            await record_token_usage(
                session,
                user_info["tenant_id"],
                user_info["user_id"],
                tokens_in,
                tokens_out
            )
            
            # Send end message with usage
            await websocket.send_json({
                "type": "end",
                "usage": {
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out
                }
            })
            
        except Exception as e:
            # Send error message
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })


async def websocket_chat_handler(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    x_tenant_id: Optional[str] = Header(None, alias=settings.TENANT_HEADER)
):
    """
    WebSocket endpoint handler for chat
    
    Expected message format from client:
    {
        "message": "user question",
        "session_id": 123  // optional
    }
    """
    await websocket.accept()
    
    # Authenticate
    user_info = await authenticate_websocket(websocket, token, x_tenant_id)
    if not user_info:
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message")
                session_id = message_data.get("session_id")
                
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Missing 'message' field"
                    })
                    continue
                
                # Handle message
                await handle_chat_message(
                    websocket,
                    user_message,
                    user_info,
                    session_id
                )
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        pass