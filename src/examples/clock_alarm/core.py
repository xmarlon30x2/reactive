from winsound import Beep
from asyncio import sleep

value = (2000, 700)
rounds = 5

async def sound_alarm():
    for _ in range(rounds):
        Beep(*value)
        await sleep(1)

def format_seconds(seconds: int):
    return f'{seconds//60:02d}:{seconds%60:02d}'
