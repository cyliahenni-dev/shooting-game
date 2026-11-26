"""Tests of the FACTORY METHOD pattern (model only: no window needed). Run with:  pytest"""
import ast
import pathlib
import random

import pytest

import settings as cfg
from model.game_board import GameBoard
from model.monster import Monster
from model.monster_factory import (MonsterFactory, NormalFactory, FastFactory, FlyingFactory, StrongFactory,
                                   ImmobileFactory, ZombieFactory, DragonFactory, RobotFactory)
from model.monster_types import ZombieMonster, DragonMonster, RobotMonster
from model.spawner import Spawner
from model.worlds import ForestWorld

FACTORIES = [NormalFactory, FastFactory, FlyingFactory, StrongFactory,
             ImmobileFactory, ZombieFactory, DragonFactory, RobotFactory]
ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_the_creator_is_abstract():
    with pytest.raises(TypeError):
        MonsterFactory()                              # the factory method has no body: cannot be used alone


@pytest.mark.parametrize("factory_class", FACTORIES)
def test_each_factory_creates_its_own_type(factory_class):
    factory = factory_class()
    monster = factory.create_monster(cfg.WIDTH, cfg.HEIGHT, random.Random(1), avoid=(400, 300))
    assert isinstance(factory, MonsterFactory) and isinstance(monster, Monster)
    assert type(monster) is factory.monster_class


@pytest.mark.parametrize("factory_class", FACTORIES)
def test_spawn_prepares_the_monster(factory_class):
    board = GameBoard(rng=random.Random(2))
    monster = factory_class().spawn(cfg.WIDTH, cfg.HEIGHT, random.Random(2),
                                    avoid=board.player.pos, target=board.player, score=0)
    assert monster.target is board.player


def test_spawn_makes_monsters_harder_with_the_score():
    easy = DragonFactory().spawn(800, 600, random.Random(4), score=0)
    hard = DragonFactory().spawn(800, 600, random.Random(4), score=900)
    assert hard.speed > easy.speed


def test_zombie_rises_inside_the_area_far_from_the_player():
    player_pos = (400, 300)
    for seed in range(40):
        zombie = ZombieFactory().create_monster(cfg.WIDTH, cfg.HEIGHT, random.Random(seed), avoid=player_pos)
        assert 40 <= zombie.pos.x <= cfg.WIDTH - 40 and 40 <= zombie.pos.y <= cfg.HEIGHT - 40


def board_with_every_monster(seed):
    """A board whose single world offers all the monsters (the real worlds each have their own family)."""
    rng = random.Random(seed)
    return GameBoard(rng=rng, worlds=[ForestWorld(rng, catalog=Spawner.DEFAULT_CATALOG)])


def test_monsters_on_demand_coexist_in_the_same_game():
    board = board_with_every_monster(5)
    for name in ("zombie", "dragon", "robot"):
        assert board.spawn_on_demand(name).kind == name
    assert {type(m) for m in board.monsters} >= {ZombieMonster, DragonMonster, RobotMonster}
    for _ in range(300):                              # they all live and act together
        board.update(1 / 60)
        board.player.health = max(board.player.health, 30)


def test_unknown_type_on_demand_creates_nothing():
    board = GameBoard(rng=random.Random(6))
    count = len(board.monsters)
    assert board.spawn_on_demand("unicorn") is None and len(board.monsters) == count


def test_a_long_game_creates_every_type():
    board = board_with_every_monster(9)
    board.player.score = 200
    seen = set()
    for frame in range(60 * 90):
        if board.monsters:
            target = min(board.monsters, key=lambda m: m.pos.distance_to(board.player.pos))
            board.player.aim(target.pos)
            board.fire()
        board.player.health = max(board.player.health, 30)
        board.update(1 / 60)
        seen |= {m.kind for m in board.monsters}
    assert {"zombie", "dragon", "robot"} <= seen


def test_dragon_and_robot_rules():
    assert DragonMonster((0, 0)).take_hit("fire", 20) == 10        # resists fire
    assert RobotMonster((0, 0)).take_hit("laser", 12) == 24        # weak to lasers


def test_spawner_limits_dragons():
    sp = Spawner(random.Random(2))
    two = [DragonMonster((100, 100)), DragonMonster((200, 200))]
    assert all(sp.choose_factory(500, two).monster_class is not DragonMonster for _ in range(300))


def test_the_board_never_names_a_concrete_monster():
    """Client code depends on the abstract factory only (Factory Method / DIP)."""
    text = (ROOT / "model" / "game_board.py").read_text()
    tree = ast.parse(text)
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert "model.monster_types" not in imported and "model.monster_factory" not in imported
    for concrete in ("ZombieMonster", "DragonMonster", "RobotMonster", "ZombieFactory"):
        assert concrete not in text
