# Space Defender - Shooting Game (Pygame)

* `tp1/` : TP1, original single-file prototype. Run: `python tp1/game.py`
* `tp2/` : TP2, OOP structure (GameObject, Player, Monster, Bullet, Reward, GameBoard, Game) with tests.
* `tp3/` : TP3, SOLID refactoring: SRP (Health/HealthBar), OCP (monster types and Spawner), LSP (all monsters usable as Monster), ISP (small ability interfaces), DIP (DamageStrategy).
* `tp4/` : TP4, MVC architecture: `model/` (game rules), `view/` (drawing, themes, sounds), `controller/` (input and main loop), with image and sound assets for three themes (desert, forest, space).
* `tp5/` : TP5, design patterns on top of the MVC game: Factory Method (monster factories), Abstract Factory (worlds: forest, desert, space), Builder (the Extreme level), with the matching tests.

For TP2 to TP5: `cd tp2`, `cd tp3`, `cd tp4` or `cd tp5`, then `pip install -r requirements.txt`, `python main.py` to play and `pytest` to run the tests.