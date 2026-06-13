# AI Assistant Improvement Guide

This guide outlines steps to improve the "ИИ-помощник" (AI Assistant) in the Computer Networks project.

## Current Implementation Status
- Basic AI chat interface in base.html
- API endpoint at `/api/ai-chat/`
- Uses `DEEPSEEK_API_KEY` from environment variables (config/settings.py line 289)
- Custom styling in dark and light modes

## Key Improvements

### 1. Integrate Network Simulator Context
- Modify the AI API endpoint (`core/views.py` → `ai_chat_api`) to accept current topology state
- Add logic to let the AI analyze devices, connections, and configurations in real‑time
- Example prompt context:
  ```json
  {
    "topology": "Current network topology data",
    "user_prompt": "Why can't PC1 ping PC2?"
  }
  ```

### 2. Add Specialized Knowledge Base
- Add training data about common network protocols (TCP/IP, OSPF, BGP, etc.)
- Include lab‑specific troubleshooting tips
- Use RAG (Retrieval‑Augmented Generation) with embedded course content

### 3. Implement Simulation Guidance
- AI can suggest step‑by‑step configuration for:
  - Setting IP addresses
  - Configuring routers and switches
  - Creating VLANs
  - Setting up DHCP servers

### 4. Add Voice Interaction
- Integrate Web Speech API for voice commands
- Let users speak network questions and hear AI responses

### 5. Improve Error Handling
- Gracefully handle missing API keys
- Show user‑friendly error messages
- Provide fallbacks for offline scenarios

### 6. Log Conversations
- Store AI interactions in a new Django model
- Let users revisit past conversations
- Analytics to improve prompts and responses

## Required Environment Variables
- Add `DEEPSEEK_API_KEY` to your `.env` file
- Example: `DEEPSEEK_API_KEY=your_api_key_here`

## Example Model for AI Conversations
```python
# network_simulator/models.py
from django.db import models
from django.conf import settings

class AIConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField(default=list)  # Stores conversation history
    topology_snapshot = models.JSONField(null=True, blank=True)
```

## Example Enhanced API View
```python
# core/views.py
def ai_chat_api(request):
    from network_simulator.services import serialize_topology
    topology = get_or_create_user_topology(request.user)
    
    messages = request.POST.getlist("messages") or []
    system_prompt = """You are an expert network engineering tutor. 
    Help students with network design, protocol questions, and troubleshooting.
    Use simple, clear explanations with practical examples."""
    
    # Add context from current topology
    context = serialize_topology(topology)
    full_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Current network topology: {context}"},
        *messages
    ]
    
    # Call DeepSeek or other API here
    # ...
```

## Future Roadmap
- Add AI‑generated quiz questions based on user progress
- Personalized learning recommendations
- Integration with real network hardware for remote labs
- Support for multiple AI providers (OpenAI, Anthropic, etc.)
