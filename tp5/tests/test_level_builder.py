"""Tests of the BUILDER pattern: the Extreme level (model only: no window needed)."""
import ast
import pathlib
import random

import pytest

from model.game_board import GameBoard
from model.level_builder import Level, LevelBuilder, LevelDirector, ExtremeLevelBuilder
from model.monster_factory import NormalFactory
from model.monster_types import ZombieMonster, RobotMonster, ImmobileMonster
from model.player import Player
from model.reward import Reward, SoulRuby, VitalFlask
from model.weapons import ObsidianShard, SoulFlame, Weapon
from model.worlds import World

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARENA = (800, 600)
STEP = GameBoard.LEVEL_SCORE_STEP


def extreme(seed=1):
    return LevelDirector(ExtremeLevelBuilder(random.Random(seed))).construct()


def test_the_builder_cannot_be_used_alone():
    with pytest.raises(TypeError):
        LevelBuilder(random.Random(1))


def test_the_director_builds_the_extreme_level():
    level = extreme()
    assert isinstance(level, Level) and isinstance(level, World)
    assert level.key == "extreme" and level.title == "Extreme Inferno"
    assert [type(w) for w in level.create_weapons()][0] is ObsidianShard
    assert {w.damage_type for w in level.create_weapons()} == {"bullet", "fire", "laser"}
    assert level.spawn_scale < 1


def test_monsters_are_placed_at_their_positions():
    level = extreme()
    player = Player((400, 300))
    monsters = level.opening_monsters(ARENA, player)
    assert len(monsters) == 8
    assert sum(isinstance(m, ImmobileMonster) for m in monsters) == 2
    assert sum(isinstance(m, ZombieMonster) for m in monsters) == 2
    assert sum(isinstance(m, RobotMonster) for m in monsters) == 2
    assert abs(monsters[0].pos.x - 80) < 1e-6 and abs(monsters[0].pos.y - 84) < 1e-6    # 0.10 and 0.14 of the arena
    assert all(m.target is player for m in monsters)
    assert all(m.pos.distance_to(player.pos) > 150 for m in monsters)           # nobody starts on top of you
    assert all(0 <= m.pos.x <= 800 and 0 <= m.pos.y <= 600 for m in monsters)


def test_rewards_are_placed_at_their_positions():
    rewards = extreme().opening_rewards(ARENA)
    assert len(rewards) == 5 and all(isinstance(r, Reward) for r in rewards)
    assert {type(r) for r in rewards} == {VitalFlask, SoulRuby}
    assert abs(rewards[0].pos.x - 200) < 1e-6 and abs(rewards[0].pos.y - 180) < 1e-6    # 0.25 and 0.30


def test_positions_follow_the_size_of_the_arena():
    level = extreme()
    small = level.opening_monsters((400, 300), Player((200, 150)))
    big = level.opening_monsters((800, 600), Player((400, 300)))
    assert all(abs(a.pos.x * 2 - b.pos.x) < 1e-6 and abs(a.pos.y * 2 - b.pos.y) < 1e-6 for a, b in zip(small, big))


def test_an_incomplete_level_is_refused():
    class Lazy(ExtremeLevelBuilder):
        def build_weapons(self):
            pass                                              # forgets the weapons

    with pytest.raises(ValueError):
        LevelDirector(Lazy(random.Random(1))).construct()


def test_the_builder_is_ready_for_another_level():
    builder = ExtremeLevelBuilder(random.Random(2))
    first = LevelDirector(builder).construct()
    second = LevelDirector(builder).construct()
    assert first is not second and first.key == second.key


def test_the_same_director_works_with_any_builder():
    class ArenaBuilder(LevelBuilder):                         # a tiny level made by a different builder
        def build_background(self):
            self.set_background("forest", "Small arena")

        def build_monsters(self):
            self.add_monster_type(NormalFactory(), 1, 0)
            self.place_monster(NormalFactory(), 0.2, 0.2)

        def build_weapons(self):
            self.add_weapon(SoulFlame)

        def build_rewards(self):
            self.add_reward_type(VitalFlask)

    level = LevelDirector(ArenaBuilder(random.Random(3))).construct()
    assert level.title == "Small arena" and len(level.opening_monsters(ARENA, Player((400, 300)))) == 1
    assert level.opening_rewards(ARENA) == []
    board = GameBoard(rng=random.Random(3), worlds=[level])             # and the board plays it
    for _ in range(300):
        board.player.health = max(board.player.health, 30)
        board.update(1 / 60)


def test_the_board_starts_the_extreme_level_with_everything_in_place():
    board = GameBoard.extreme(rng=random.Random(4))
    assert board.world.key == "extreme"
    assert len(board.monsters) == 8 + 1 and len(board.rewards) == 5      # placed ones + the first wave
    assert board.player.weapon.name == "Obsidian Shard"
    assert board.world.spawn_scale == 0.6


def test_the_extreme_level_is_played_alone():
    board = GameBoard.extreme(rng=random.Random(5))
    assert board.single_level and [w.key for w in board.worlds] == ["extreme"]
    board.player.score = 10 * STEP                          # far more than any campaign level needs
    board.update(1 / 60)
    assert (board.level, board.world.key) == (1, "extreme")          # no level-up, no other world


def test_the_campaign_is_not_a_single_level_and_has_no_extreme():
    board = GameBoard(rng=random.Random(5))
    assert not board.single_level and "extreme" not in [w.key for w in board.worlds]


def test_reset_restarts_the_extreme_level():
    board = GameBoard.extreme(rng=random.Random(6))
    board.player.score = 500
    board.monsters = []
    board.reset()
    assert board.player.score == 0 and len(board.monsters) == 9 and len(board.rewards) == 5
    assert board.world.key == "extreme"


def test_the_waves_of_the_extreme_level_come_faster():
    for key in ("forest", "extreme"):
        board = GameBoard(rng=random.Random(6)) if key == "forest" else GameBoard.extreme(rng=random.Random(6))
        board.monsters = []
        board.player.health = 10 ** 6
        count = 0
        for _ in range(60 * 6):
            before = len(board.monsters)
            board.update(1 / 60)
            count += max(0, len(board.monsters) - before)
        if key == "forest":
            forest_waves = count
        else:
            assert count > forest_waves


def test_on_demand_monsters_work_in_the_extreme_level():
    board = GameBoard.extreme(rng=random.Random(7))
    assert [board.spawn_on_demand(n).kind for n in ("zombie", "dragon", "robot")] == ["zombie", "dragon", "robot"]


def test_a_long_game_in_the_extreme_level():
    board = GameBoard.extreme(rng=random.Random(8))
    for frame in range(60 * 60):
        if board.monsters:
            target = min(board.monsters, key=lambda m: m.pos.distance_to(board.player.pos))
            board.player.select_weapon((frame // 90) % 3)
            board.player.aim(target.pos)
            board.fire()
        board.player.health = max(board.player.health, 30)
        board.update(1 / 60)
    assert board.player.score > 0


def test_the_board_does_not_know_the_builder():
    text = (ROOT / "model" / "game_board.py").read_text()
    imported = {n.module for n in ast.walk(ast.parse(text)) if isinstance(n, ast.ImportFrom)}
    assert not imported & {"model.level_builder", "model.worlds"}
    for name in ("ExtremeLevelBuilder", "LevelDirector", "ObsidianShard"):
        assert name not in text


def test_a_weapon_is_a_weapon():
    assert isinstance(ObsidianShard(), Weapon)
