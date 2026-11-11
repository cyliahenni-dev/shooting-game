"""Tests of the TP N3 homework (SOLID). Run with:  pytest"""
import os
import random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
import pytest

import settings as cfg
from abilities import Chaser, Flyer, Shooter, Shielded
from damage import DamageStrategy, NormalDamage, ResistantDamage, WeaknessDamage
from game import Game
from game_board import GameBoard
from health import Health, HealthBar
from monster import Monster
from monster_types import (NormalMonster, FastMonster, FlyingMonster,
                           StrongMonster, ImmobileMonster)
from spawner import Spawner

ALL_TYPES = [NormalMonster, FastMonster, FlyingMonster, StrongMonster, ImmobileMonster]


def make(kind):
    from player import Player
    player = Player((400, 300))
    m = kind((100, 100))
    m.target = player
    return m, player


# ---- SRP
def test_health_only_stores_points():
    h = Health(50)
    h.take(20); assert h.hp == 30 and h.alive
    h.take(100); assert h.hp == 0 and not h.alive


def test_monster_does_not_draw_its_own_bar():
    screen = pygame.Surface((200, 200))
    screen.fill((0, 0, 0))
    m, _ = make(NormalMonster)
    m.pos = pygame.Vector2(100, 100)
    m.draw(screen)
    assert screen.get_at((100, 100 - m.radius - 10)) == (0, 0, 0, 255)       # no bar above it
    HealthBar().render(screen, m.health, 82, 100 - m.radius - 12)
    assert screen.get_at((90, 100 - m.radius - 10))[:3] == (40, 200, 40)


# ---- DIP
def test_damage_strategies():
    assert NormalDamage().compute("fire", 20) == 20
    assert ResistantDamage(["bullet"]).compute("bullet", 25) == 12.5
    assert ResistantDamage(["bullet"]).compute("fire", 20) == 20
    assert WeaknessDamage(["fire"]).compute("fire", 20) == 40


def test_monster_uses_injected_strategy():
    class Immune(DamageStrategy):
        def compute(self, weapon, base_damage): return 0
        def describe(self): return "immune"
    m = NormalMonster((0, 0), damage_strategy=Immune())
    assert m.take_hit("bullet", 25) == 0 and m.health.hp == m.health.max_hp


def test_flying_and_strong_rules():
    f, _ = make(FlyingMonster)
    assert f.take_hit("bullet", 25) == 12.5
    s, _ = make(StrongMonster)
    assert s.take_hit("fire", 20) == 20            # 20 * 2 (weak) * 0.5 (shield)
    s2, _ = make(StrongMonster)
    assert s2.take_hit("laser", 12) == 6           # shield only


# ---- ISP
def test_each_monster_only_has_its_abilities():
    assert isinstance(NormalMonster((0, 0)), Chaser)
    assert isinstance(FlyingMonster((0, 0)), Flyer) and not isinstance(FlyingMonster((0, 0)), Chaser)
    assert isinstance(ImmobileMonster((0, 0)), Shooter) and not isinstance(ImmobileMonster((0, 0)), Chaser)
    assert isinstance(StrongMonster((0, 0)), Shielded) and not isinstance(FastMonster((0, 0)), Shielded)


# ---- LSP
@pytest.mark.parametrize("kind", ALL_TYPES)
def test_every_type_works_as_a_monster(kind):
    m, player = make(kind)
    assert isinstance(m, Monster)
    shots = m.update(0.1)
    assert isinstance(shots, list)
    m.take_hit("bullet", 25)
    m.attack_player(player)
    m.draw(pygame.Surface((800, 600)))
    assert m.speed >= 0 and m.score_value > 0


def test_immobile_never_moves_but_shoots():
    m, _ = make(ImmobileMonster)
    start = pygame.Vector2(m.pos)
    shots = []
    for _ in range(300):
        shots += m.update(1 / 60)
    assert m.pos == start and len(shots) >= 2


def test_chasers_get_closer():
    for kind in (NormalMonster, FastMonster, FlyingMonster, StrongMonster):
        m, player = make(kind)
        d0 = m.pos.distance_to(player.pos)
        for _ in range(30):
            m.update(1 / 60)
        assert m.pos.distance_to(player.pos) < d0, kind


# ---- OCP
def test_spawner_follows_the_catalog_and_score():
    sp = Spawner(random.Random(1))
    assert {sp.choose_kind(0, []) for _ in range(200)} <= {NormalMonster, FastMonster}
    assert StrongMonster in {sp.choose_kind(500, []) for _ in range(500)}


def test_immobile_limit():
    sp = Spawner(random.Random(2))
    two = [ImmobileMonster((100, 100)), ImmobileMonster((200, 200))]
    assert all(sp.choose_kind(500, two) is not ImmobileMonster for _ in range(300))


def test_new_monster_type_without_editing_existing_code():
    class GhostMonster(NormalMonster):              # a brand new type = a new subclass
        name = "Ghost"
        base_speed = 70
    sp = Spawner(random.Random(3), catalog=[(GhostMonster, 1, 0)])
    board = GameBoard(rng=random.Random(3))
    board.spawner = sp
    board.spawn_monster()
    assert isinstance(board.monsters[-1], GhostMonster)


# ---- whole game
def test_board_play_without_crash():
    rng = random.Random(5)
    board = GameBoard(rng=rng)
    board.player.score = 200
    screen = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
    for frame in range(60 * 30):
        if board.monsters:
            tgt = min(board.monsters, key=lambda m: m.pos.distance_to(board.player.pos))
            board.player.select_weapon(list(cfg.WEAPONS)[(frame // 90) % 3])
            board.player.aim(tgt.pos)
            board.fire()
        board.player.health = max(board.player.health, 30)
        board.update(1 / 60)
        if frame % 30 == 0:
            board.draw(screen)
    assert board.player.score > 200


def test_enemy_shots_hurt_the_player():
    board = GameBoard(rng=random.Random(7))
    board.monsters = [ImmobileMonster((100, 100))]
    board.monsters[0].target = board.player
    hp = board.player.health
    for _ in range(600):
        board.update(1 / 60)
        if board.game_over: break
    assert board.player.health < hp


def test_game_runs_a_few_frames():
    Game().run(max_frames=5)
