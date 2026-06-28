import pytest

from app.audio.echo_guard import EchoGuard
from app.audio.tts_queue import TTSQueue
from app.core.config import Settings
from app.orchestration.action_scheduler import ActionIntent, ActionScheduler
from app.robot.simulated import SimulatedRobotClient


@pytest.mark.asyncio
async def test_scheduler_manual_priority_completes():
    settings = Settings(llm_provider="mock", tts_provider="mock")
    echo = EchoGuard(enabled=True, cooldown_s=0)
    tts = TTSQueue(settings, echo)
    robot = SimulatedRobotClient()
    scheduler = ActionScheduler(settings=settings, robot=robot, tts=tts, idle_enabled=False)
    await robot.connect()
    await tts.start()
    await scheduler.start()
    try:
        action = await scheduler.enqueue(ActionIntent(emotion="saludo", layer="manual", motion_enabled=True), wait=True)
        assert action.done.is_set()
        assert scheduler.status().busy is False
    finally:
        await scheduler.stop()
        await tts.stop()
        await robot.close()
