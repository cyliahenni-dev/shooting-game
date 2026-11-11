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
