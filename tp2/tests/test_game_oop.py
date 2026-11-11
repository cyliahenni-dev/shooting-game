import os
import random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest
from bullet import Bullet
from game_board import GameBoard
from game_object import GameObject
from monster import Monster
from player import Player
from reward import Reward


def board():
    return GameBoard(800, 600, rng=random.Random(1))


def clear(b):
    b.monsters, b.bullets, b.rewards = [], [], []


def test_game_object_is_abstract():
    with pytest.raises(TypeError):
        GameObject((0, 0), 5)


def test_all_elements_are_game_objects():
    for obj in (Player((0, 0)), Monster((0, 0)), Bullet((0, 0), (1, 0)), Reward((0, 0), "points")):
        assert isinstance(obj, GameObject)


def test_player_stays_inside_the_area():
    p = Player((10, 10))
    p.move((-1, -1), 5, 800, 600)
    assert p.pos.x == p.radius and p.pos.y == p.radius
    p.move((1, 1), 100, 800, 600)
    assert p.pos.x == 800 - p.radius and p.pos.y == 600 - p.radius


def test_player_reloads_between_shots():
    p = Player((100, 100))
    p.aim((200, 100))
    first = p.shoot()
    assert first is not None and first.dir.x == pytest.approx(1)
    assert p.shoot() is None              # still reloading
    p.update(0.3)
    assert p.shoot() is not None


def test_monster_chases_the_player():
    p = Player((400, 300))
    m = Monster((0, 300))
    m.target = p
    before = m.pos.distance_to(p.pos)
    m.update(0.5)
    assert m.pos.distance_to(p.pos) < before


def test_two_bullets_kill_a_monster_and_give_points():
    b = board()
    clear(b)
    m = Monster((500, 300))
    b.monsters.append(m)
    for _ in range(2):
        b.bullets.append(Bullet((500, 300), (1, 0)))
    b.update(0.01)
    assert m not in b.monsters
    assert b.player.score == 10


def test_monster_hurts_the_player_once_per_second():
    b = board()
    clear(b)
    m = Monster(b.player.pos, speed=0)    # speed 0: it stays on the player
    m.target = b.player
    b.monsters.append(m)
    b.update(0.1)
    assert b.player.health == 90
    b.update(0.1)
    assert b.player.health == 90          # recovering
    b.update(1.0)
    assert b.player.health == 80


def test_game_over_at_zero_health():
    b = board()
    clear(b)
    b.player.health = 5
    m = Monster(b.player.pos)
    m.target = b.player
    b.monsters.append(m)
    b.update(0.1)
    assert b.player.health == 0 and b.game_over


def test_rewards_are_collected():
    b = board()
    clear(b)
    b.player.health = 50
    b.rewards += [Reward(b.player.pos, Reward.POINTS), Reward(b.player.pos, Reward.HEALTH)]
    b.update(0.01)
    assert b.player.score == 50
    assert b.player.health == 70
    assert b.rewards == []


def test_reset_restarts_the_game():
    b = board()
    b.player.health = 0
    b.game_over = True
    b.reset()
    assert not b.game_over and b.player.health == 100 and len(b.monsters) == 1


def test_full_game_runs_headless():
    from game import Game
    Game().run(max_frames=60)
