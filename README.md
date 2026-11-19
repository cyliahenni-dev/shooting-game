# Space Defender - Shooting Game (Pygame)

* `tp1/` : TP1, original single-file prototype. Run: `python tp1/game.py`
* `tp2/` : TP2, OOP structure (GameObject, Player, Monster, Bullet, Reward, GameBoard, Game) with tests.
* `tp3/` : TP3, SOLID refactoring: SRP (Health/HealthBar), OCP (monster types and Spawner), LSP (all monsters usable as Monster), ISP (small ability interfaces), DIP (DamageStrategy).
* `tp4/` : TP4, MVC architecture: `model/` (game rules), `view/` (drawing, themes, sounds), `controller/` (input and main loop), with image and sound assets for three themes (desert, forest, space).

For TP2, TP3 and TP4: `cd tp2`, `cd tp3` or `cd tp4`, then `pip install -r requirements.txt`, `python main.py` to play and `pytest` to run the tests.