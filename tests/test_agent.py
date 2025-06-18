"""
Test suite for Zara's agent system.
Tests Ollama integration, tool routing, and conversation handling.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import asyncio
from pathlib import Path

from zara.agent import get_agent, ZaraAgent, ToolError

# Mock responses
MOCK_OLLAMA_RESPONSE = {
    "message": {
        "content": "I'll help you with that task."
    }
}

MOCK_TOOL_RESPONSE = {
    "success": True,
    "result": "Operation completed successfully"
}

@pytest.fixture
def mock_ollama():
    """Mock Ollama client."""
    with patch('ollama.chat') as mock_chat:
        mock_chat.return_value = MOCK_OLLAMA_RESPONSE
        yield mock_chat

@pytest.fixture
def mock_memory():
    """Mock memory manager."""
    with patch('zara.agent.get_memory_manager') as mock_mem:
        mock_mem.return_value = MagicMock()
        yield mock_mem.return_value

@pytest.fixture
def test_agent(mock_ollama, mock_memory):
    """Create test agent instance with mocked dependencies."""
    # Reset singleton
    ZaraAgent._instance = None
    return get_agent()

@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """Test agent initialization and Ollama verification."""
    assert test_agent.model == "llama2"
    assert len(test_agent.tools) > 0
    assert test_agent.witty_prefixes
    assert test_agent.witty_postscripts

@pytest.mark.asyncio
async def test_ollama_connection_error():
    """Test handling of Ollama connection failure."""
    with patch('ollama.list', side_effect=Exception("Connection failed")):
        with pytest.raises(RuntimeError) as exc_info:
            ZaraAgent()
        assert "Ollama service not detected" in str(exc_info.value)

@pytest.mark.asyncio
async def test_message_processing(test_agent, mock_memory):
    """Test basic message processing flow."""
    message = "Hello Zara!"
    response = await test_agent.process_message(message)
    
    # Verify memory storage
    mock_memory.store_chat.assert_called_with("user", message, None)
    assert response == MOCK_OLLAMA_RESPONSE['message']['content']

@pytest.mark.asyncio
async def test_conversation_context(test_agent, mock_memory):
    """Test conversation context handling."""
    mock_memory.get_recent_chat.return_value = [
        {"speaker": "user", "content": "Hello"},
        {"speaker": "assistant", "content": "Hi there"}
    ]
    
    context = await test_agent._get_conversation_context()
    assert "Hello" in context
    assert "Hi there" in context

@pytest.mark.asyncio
async def test_tool_execution(test_agent):
    """Test tool execution and error handling."""
    # Test successful tool execution
    with patch.dict(test_agent.tools, {'test_tool': AsyncMock(return_value=MOCK_TOOL_RESPONSE)}):
        result = await test_agent._execute_tool('test_tool', {'param': 'value'})
        assert result['success']
    
    # Test unknown tool
    result = await test_agent._execute_tool('nonexistent_tool', {})
    assert not result['success']
    assert 'error' in result

@pytest.mark.asyncio
async def test_personality_features(test_agent):
    """Test witty response generation."""
    # Test without personality (90% case)
    with patch('random.random', return_value=0.5):
        response = test_agent._add_personality("Normal response")
        assert response == "Normal response"
    
    # Test with prefix (5% case)
    with patch('random.random', return_value=0.05):
        with patch('random.choice', side_effect=[True, test_agent.witty_prefixes[0]]):
            response = test_agent._add_personality("Normal response")
            assert response.startswith(test_agent.witty_prefixes[0])
    
    # Test with postscript (5% case)
    with patch('random.random', return_value=0.05):
        with patch('random.choice', side_effect=[False, test_agent.witty_postscripts[0]]):
            response = test_agent._add_personality("Normal response")
            assert response.endswith(test_agent.witty_postscripts[0])

@pytest.mark.asyncio
async def test_error_response_generation(test_agent):
    """Test error response generation."""
    response = test_agent._generate_error_response("test_tool", "Connection failed")
    assert "test_tool" in response
    assert "Connection failed" in response
    assert any(phrase in response for phrase in [
        "Oops!", "embarrassing", "moments", "promise"
    ])

@pytest.mark.asyncio
async def test_tool_registration(test_agent):
    """Test tool registration system."""
    # Add a test tool
    async def test_tool(params):
        return {"result": params}
    
    test_agent.tools['test_tool'] = test_tool
    assert 'test_tool' in test_agent.tools
    
    # Execute the tool
    result = await test_agent._execute_tool('test_tool', {'test': 'value'})
    assert result['success']
    assert result['result']['result']['test'] == 'value'

@pytest.mark.asyncio
async def test_error_handling(test_agent, mock_memory):
    """Test error handling in message processing."""
    # Simulate Ollama error
    mock_memory.get_recent_chat.side_effect = Exception("Database error")
    
    response = await test_agent.process_message("Hello")
    assert "apologize" in response.lower()
    assert "trouble" in response.lower()

@pytest.mark.asyncio
async def test_tool_error_handling(test_agent):
    """Test handling of tool execution errors."""
    async def failing_tool(params):
        raise ToolError("Tool execution failed")
    
    test_agent.tools['failing_tool'] = failing_tool
    result = await test_agent._execute_tool('failing_tool', {})
    
    assert not result['success']
    assert 'error' in result
    assert 'apology' in result
    assert "Tool execution failed" in result['error']

@pytest.mark.asyncio
async def test_concurrent_processing(test_agent):
    """Test handling multiple concurrent requests."""
    async def process_messages():
        tasks = [
            test_agent.process_message(f"Message {i}")
            for i in range(5)
        ]
        return await asyncio.gather(*tasks)
    
    responses = await process_messages()
    assert len(responses) == 5
    assert all(isinstance(r, str) for r in responses)

@pytest.mark.asyncio
async def test_memory_integration(test_agent, mock_memory):
    """Test integration with memory system."""
    # Process a message
    await test_agent.process_message("Remember this")
    
    # Verify memory interactions
    assert mock_memory.store_chat.called
    assert mock_memory.get_recent_chat.called
    
    # Verify context retrieval
    mock_memory.get_recent_chat.return_value = [
        {"speaker": "user", "content": "Remember this"}
    ]
    context = await test_agent._get_conversation_context()
    assert "Remember this" in context