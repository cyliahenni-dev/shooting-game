"""Tests of the ABSTRACT FACTORY pattern: worlds and levels (model only: no window needed)."""
import ast
import pathlib
import random

import pytest

from model.game_board import GameBoard
from model.monster import Monster
from model.monster_types import NormalMonster
from model.player import Player
from model.reward import Reward, GoldCoin, HealingPotion
from model.weapons import Weapon
from model.levels import default_worlds
from model.worlds import World, ForestWorld, DesertWorld, SpaceWorld

WORLDS = [ForestWorld, DesertWorld, SpaceWorld]
ROOT = pathlib.Path(__file__).resolve().parent.parent
STEP = GameBoard.LEVEL_SCORE_STEP


def monsters_of(world, draws=400):
    player = Player((400, 300))
    return {world.create_monster((800, 600), player, [], 1000).kind for _ in range(draws)}


def test_the_abstract_factory_cannot_be_used_alone():
    with pytest.raises(TypeError):
        World(random.Random(1))


@pytest.mark.parametrize("world_class", WORLDS)
def test_each_world_creates_a_whole_family(world_class):
    world = world_class(random.Random(1))
    monster = world.create_monster((800, 600), Player((400, 300)), [], 100)
    weapons = world.create_weapons()
    reward = world.create_reward((10, 10))
    assert isinstance(world, World) and isinstance(monster, Monster) and isinstance(reward, Reward)
    assert len(weapons) == 3 and all(isinstance(w, Weapon) for w in weapons)


@pytest.mark.parametrize("world_class", WORLDS)
def test_the_family_is_compatible(world_class):
    world = world_class(random.Random(2))
    assert monsters_of(world) == set(world.monster_names())                   # only monsters of this world
    assert {w.damage_type for w in world.create_weapons()} == {"bullet", "fire", "laser"}
    assert {r.type for r in (world.create_reward((0, 0)) for _ in range(60))} == {Reward.POINTS, Reward.HEALTH}


def test_the_worlds_are_really_different():
    worlds = [cls(random.Random(3)) for cls in WORLDS]
    weapon_names = [{w.name for w in world.create_weapons()} for world in worlds]
    reward_classes = [{type(world.create_reward((0, 0))) for _ in range(60)} for world in worlds]
    for i in range(3):
        for j in range(i + 1, 3):
            assert not weapon_names[i] & weapon_names[j]
            assert not reward_classes[i] & reward_classes[j]
    forest, desert, space = (set(w.monster_names()) for w in worlds)
    assert "dragon" in forest and "robot" not in forest
    assert "robot" in space and "dragon" not in space and "zombie" not in space
    assert forest != desert != space


def test_levels_keep_the_world_and_only_raise_the_difficulty():
    board = GameBoard(rng=random.Random(3))
    assert (board.level, board.world.key) == (1, "forest")
    weapons = [w.name for w in board.player.weapons]
    board.player.select_weapon(1)
    board.player.score = STEP
    board.update(1 / 60)
    assert board.level == 2 and board.world.key == "forest"        # the same world goes on
    assert [w.name for w in board.player.weapons] == weapons       # and the same weapons
    assert board.player.weapon.name == "Fire Staff"
    assert board.banner_time > 0 and len(board.monsters) == 1       # a fresh start of the new level
    assert board.difficulty > 1


@pytest.mark.parametrize("start", [0, 1, 2])
def test_the_world_never_changes_during_the_campaign(start):
    board = GameBoard(rng=random.Random(4), start_world=start)
    key = board.world.key
    for level in range(1, 11):
        board.player.score = (level - 1) * STEP
        board.update(1 / 60)
        assert board.level == level and board.world.key == key


def test_each_level_makes_the_monsters_tougher():
    board = GameBoard(rng=random.Random(5))
    first = board.spawn_on_demand("zombie")
    board.player.score = 3 * STEP
    board.update(1 / 60)
    later = board.spawn_on_demand("zombie")
    assert board.level == 4 and later.health.max_hp > first.health.max_hp
    assert later.health.hp == later.health.max_hp


def test_each_level_makes_the_waves_faster():
    def waves(level):
        board = GameBoard(rng=random.Random(6))
        board.level = level                                         # score stays low: no level-up
        board.monsters = []
        board.player.health = 10 ** 6
        count = 0
        for _ in range(60 * 8):
            before = len(board.monsters)
            board.update(1 / 60)
            count += max(0, len(board.monsters) - before)
        return count
    assert waves(5) > waves(1)


def test_the_monsters_of_the_world_appear_as_the_score_grows_and_never_start_over():
    board = GameBoard(rng=random.Random(7))
    board.player.score = 3 * STEP                                   # level 4: everything is unlocked
    board.update(1 / 60)
    names = {board.world.create_monster((800, 600), board.player, [], board.progress).kind for _ in range(300)}
    assert names == set(board.world.monster_names())


def test_reset_goes_back_to_the_first_level():
    board = GameBoard(rng=random.Random(5))
    board.player.score = 2 * STEP
    board.update(1 / 60)
    board.reset()
    assert (board.level, board.world.key, board.player.score) == (1, "forest", 0)


def test_the_start_world_can_be_chosen():
    board = GameBoard(rng=random.Random(6), start_world=2)
    assert board.world.key == "space" and [w.name for w in board.player.weapons][0] == "Blaster"
    board.player.score = STEP
    board.update(1 / 60)
    assert board.world.key == "space"                               # it stays in the chosen world


def test_on_demand_monsters_must_belong_to_the_world():
    board = GameBoard(rng=random.Random(7))                        # forest: dragons yes, robots no
    assert board.spawn_on_demand("robot") is None
    assert board.spawn_on_demand("dragon").kind == "dragon"


def test_rewards_dropped_by_kills_come_from_the_current_world():
    board = GameBoard(rng=random.Random(8))
    board.LEVEL_SCORE_STEP = 10 ** 9                               # stay in the first level
    for _ in range(200):
        dead = NormalMonster((50, 50))
        dead.health.hp = 0
        board.monsters.append(dead)
        board.update(0.01)
    kinds = {type(r) for r in board.rewards}
    assert kinds and kinds <= {GoldCoin, HealingPotion}


@pytest.mark.parametrize("start", [0, 1, 2])
def test_a_long_game_runs_from_every_world(start):
    board = GameBoard(rng=random.Random(10 + start), start_world=start)
    for frame in range(60 * 60):
        if board.monsters:
            target = min(board.monsters, key=lambda m: m.pos.distance_to(board.player.pos))
            board.player.select_weapon((frame // 90) % 3)
            board.player.aim(target.pos)
            board.fire()
        board.player.health = max(board.player.health, 30)
        board.update(1 / 60)
    assert board.player.score > 0


def test_the_board_never_names_a_concrete_world_weapon_or_reward():
    """Client code depends only on the abstract factory (Abstract Factory / DIP)."""
    text = (ROOT / "model" / "game_board.py").read_text()
    imported = {n.module for n in ast.walk(ast.parse(text)) if isinstance(n, ast.ImportFrom)}
    assert not imported & {"model.monster_types", "model.monster_factory", "model.weapons", "model.reward"}
    for concrete in ("ForestWorld", "DesertWorld", "SpaceWorld", "AcornSling", "Blaster",
                     "GoldCoin", "RepairKit", "ZombieMonster", "ExtremeLevelBuilder"):
        assert concrete not in text, concrete


def test_default_worlds_are_in_level_order():
    assert [w.key for w in default_worlds(random.Random(1))] == ["forest", "desert", "space"]


def test_the_campaign_never_reaches_the_extreme_level():
    board = GameBoard(rng=random.Random(9))
    seen = set()
    for level in range(1, 13):
        board.player.score = (level - 1) * STEP
        board.update(1 / 60)
        seen.add(board.world.key)
    assert seen == {"forest"}                                       # one world for the whole campaign...
    assert "extreme" not in seen                                    # ...and never the Extreme level
