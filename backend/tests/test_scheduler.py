from __future__ import annotations

import pytest

from app.scheduler.scheduler import SchedulerService


@pytest.mark.asyncio
async def test_start_and_shutdown() -> None:
    svc = SchedulerService()
    svc.start()
    assert svc._scheduler.running
    svc.shutdown(wait=False)


@pytest.mark.asyncio
async def test_register_job() -> None:
    svc = SchedulerService()
    svc.start()

    async def dummy() -> None:
        pass

    job = svc.register_job(dummy, "interval", id="test_job", seconds=30)
    assert job is not None
    assert job.id == "test_job"
    svc.shutdown(wait=False)


@pytest.mark.asyncio
async def test_get_jobs() -> None:
    svc = SchedulerService()
    svc.start()

    async def dummy() -> None:
        pass

    svc.register_job(dummy, "interval", id="job_a", seconds=30)
    svc.register_job(dummy, "interval", id="job_b", seconds=60)
    jobs = svc.get_jobs()
    assert len(jobs) == 2
    ids = {j["id"] for j in jobs}
    assert ids == {"job_a", "job_b"}
    svc.shutdown(wait=False)


@pytest.mark.asyncio
async def test_pause_and_resume_job() -> None:
    svc = SchedulerService()
    svc.start()

    async def dummy() -> None:
        pass

    svc.register_job(dummy, "interval", id="test_job", seconds=30)
    assert svc.pause_job("test_job") is True
    assert svc.pause_job("nonexistent") is False
    assert svc.resume_job("test_job") is True
    assert svc.resume_job("nonexistent") is False
    svc.shutdown(wait=False)


@pytest.mark.asyncio
async def test_stop_job() -> None:
    svc = SchedulerService()
    svc.start()

    async def dummy() -> None:
        pass

    svc.register_job(dummy, "interval", id="test_job", seconds=30)
    assert svc.stop_job("test_job") is True
    assert svc.stop_job("nonexistent") is False
    svc.shutdown(wait=False)


@pytest.mark.asyncio
async def test_shutdown_without_start() -> None:
    svc = SchedulerService()
    svc.shutdown()


@pytest.mark.asyncio
async def test_disabled_scheduler_registers_no_jobs() -> None:
    from app.scheduler.startup import SchedulerStartup

    cfg = {"enabled": False}
    startup = SchedulerStartup(cfg)
    startup.start()
    jobs = startup.scheduler.get_jobs()
    assert len(jobs) == 0
    startup.shutdown()


@pytest.mark.asyncio
async def test_enabled_scheduler_registers_all_jobs() -> None:
    from app.scheduler.startup import SchedulerStartup

    cfg = {"enabled": True}
    startup = SchedulerStartup(cfg)
    startup.start()
    jobs = startup.scheduler.get_jobs()
    assert len(jobs) == 4
    job_ids = {j["id"] for j in jobs}
    assert job_ids == {"simulator", "alert_processing", "cleanup", "statistics_update"}
    startup.shutdown()
