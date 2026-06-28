import pytest

from app.llm.mock_provider import MockLLMProvider


@pytest.mark.asyncio
async def test_mock_llm_chat():
    llm = MockLLMProvider()
    result = await llm.chat([{"role": "user", "content": "hola"}])
    assert result.provider == "mock"
    assert "Hola" in result.content


@pytest.mark.asyncio
async def test_mock_llm_stream():
    llm = MockLLMProvider()
    chunks = []
    async for chunk in llm.chat_stream([{"role": "user", "content": "hola"}]):
        chunks.append(chunk)
    assert any(chunk.content for chunk in chunks)
    assert chunks[-1].done is True
