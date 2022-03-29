import asyncio
import math

from elden_ring import EldenRingMod
import os

from uuid import UUID
from playsound import playsound

from settings import Settings as settings

elden_ring = EldenRingMod()


def callback_channel_points(uuid: UUID, data: dict) -> None:
    reward = data['data']['redemption']['reward']['title']
    print(f"{reward} redeemed!")
    if reward == "Kill Player":
        play_local_sound("gotcha")
        elden_ring.set_hp(0)
    elif reward == "Give HP Regen":
        asyncio.ensure_future(async_regen_hp_timer(10))
    elif reward == "No Mana":
        elden_ring.set_fp(0)
    elif reward == "Max Mana":
        elden_ring.set_fp(99999)
    elif reward == "Giant Head":
        asyncio.ensure_future(async_head_timer(60))
    elif reward == "No Endurance":
        asyncio.ensure_future(async_endurance_timer(60))
    elif reward == "Drain HP":
        asyncio.ensure_future(async_drain_hp_timer(10))
    elif reward == "Give Runes for Level Up":
        give_runes_for_level()


def callback_bits(uuid: UUID, data: dict) -> None:
    amount = data["data"]["bits_used"]
    print(f"{amount} bits redeemed!")
    if amount == 1:
        asyncio.ensure_future(async_head_timer(60))
    elif amount == 10:
        give_runes_for_level()
    elif amount == 25:
        asyncio.ensure_future(async_drain_hp_timer(10))
    elif amount == 50:
        play_local_sound("gotcha")
        elden_ring.set_hp(0)
    elif amount >= 100:
        elden_ring.set_runes(0)


def give_runes_for_level():
    next_level = elden_ring.get_level()+1
    runes_required = math.ceil(0.02*(next_level**3) + 3.06*(next_level**2) + 105.6*next_level - 895)
    elden_ring.set_runes(elden_ring.get_runes()+runes_required)
    play_local_sound("thankyou")


async def async_head_timer(time):
    initial_head_size = elden_ring.get_head_size()
    elden_ring.set_head_size(50.0)
    play_local_sound("yell")
    await asyncio.sleep(time)
    elden_ring.set_head_size(initial_head_size)


async def async_endurance_timer(time):
    initial_endurance = elden_ring.get_endurance()
    elden_ring.set_endurance(1)
    await asyncio.sleep(time)
    elden_ring.set_endurance(initial_endurance)


async def async_drain_hp_timer(time):
    initial_hp = elden_ring.get_hp()
    for i in range(0, time):
        await asyncio.sleep(1)
        elden_ring.set_hp(elden_ring.get_hp() - initial_hp // time)
        play_local_sound("blood")


async def async_regen_hp_timer(time):
    max_hp = elden_ring.get_maxhp()
    for i in range(0, time):
        await asyncio.sleep(1)
        elden_ring.set_hp(elden_ring.get_hp() + max_hp // 4)
        play_local_sound("heal")


def callback_subs(uuid: UUID, data: dict) -> None:
    print(f"New Subscription")
    play_local_sound("gotcha")
    elden_ring.kill_player()


def play_local_sound(sound):
    if settings.MUTED == "false":
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, f'sounds\\{sound}.wav')
        playsound(filename)
