# Future Work: Add worker to async update events

# import os
#
# from arq.connections import RedisSettings
#
# from app.adapters.update_events import update_events
#
#
#
# async def startup(_):
#     pass
#
#
# async def shutdown(_):
#     pass
#
#
# class WorkerSettings:
#     functions = [update_events]
#     on_startup = startup
#     on_shutdown = shutdown
#     redis_settings = RedisSettings(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)),
#                                    database=int(os.getenv("REDIS_DB", 0)))
