"""All the game constants in one place."""
WIDTH, HEIGHT = 800, 600
FPS = 60

# player
PLAYER_SPEED = 280
PLAYER_HEALTH = 100
PLAYER_RADIUS = 16
SHOOT_DELAY = 0.25          # seconds between two bullets

# bullet
BULLET_SPEED = 600
BULLET_DAMAGE = 25
BULLET_RADIUS = 4

# monster
MONSTER_SPEED = 90
MONSTER_HEALTH = 50
MONSTER_ATTACK = 10
MONSTER_RADIUS = 18
MONSTER_HIT_DELAY = 1.0     # a monster hurts the player at most once per second

# rewards / score
KILL_POINTS = 10
REWARD_DROP_CHANCE = 0.6
REWARD_POINTS = 50
REWARD_HEALTH = 20
REWARD_RADIUS = 9

# weapons (NEW, TP N3): damage, delay between two shots, color of the bullet
WEAPONS = {
    "bullet": {"damage": BULLET_DAMAGE, "delay": SHOOT_DELAY, "color": (255, 230, 80)},
    "fire":   {"damage": 20,            "delay": 0.35,        "color": (255, 140, 50)},
    "laser":  {"damage": 12,            "delay": 0.12,        "color": (80, 230, 255)},
}
DEFAULT_WEAPON = "bullet"

# shots fired by monsters (NEW, TP N3)
ENEMY_SHOT_SPEED = 230
ENEMY_SHOT_DAMAGE = 10
ENEMY_SHOT_RADIUS = 6
