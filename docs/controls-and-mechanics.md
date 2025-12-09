# Controls and gameplay cheatsheet

This server ships the upstream WASD preset (`pkg/unvanquished_0.55.5.dpk` → `presets/input/wasd.cfg`). Core binds:
- Move/shoot: `WASD`, `Space` jump, `CTRL` crouch/wallwalk (aliens), `SHIFT` sprint, mouse buttons fire.
- Actions: `Q` is the context key (`+activate`) — humans use it to open an armoury or reactor, aliens to evolve at an egg/overmind.
- Build/deconstruct: `E` deconstruct (sell your own buildable when using the construction kit), `1` toggles the human blaster, `R` reload, mouse wheel swaps weapons.
- Communication: `T` chat, `Y` team chat, `U` admin chat (if logged in), `V` voice menu, `B` beacon menu, `N` bot tactics.
- Camera/help: `` ` `` console, `Tab` scores, `F1/F2` vote yes/no.

### How buying works (humans)
- Humans earn *credits* from kills and periodically via `g_freeFundPeriod` (already set to `1` in `game/server.cfg` so you drip free cash).
- Higher-tier weapons and suits require team momentum unlocks; the auto-gear script below injects momentum so everything is instantly available.
- To buy manually, stand by an armoury and press `Q` to open the buy menu, or use `/buy <item>` (e.g., `buy shotgun`, `buy jetpack`) with the console.

### Quick “all guns” loadout (no menu)
- Cheats are enabled in `game/server.cfg` (`sv_cheats 1`) so client `/give` commands work.
- Load the helper once per session in your client console: `\exec autogear.cfg` (the file is in the seeded `game/` directory).
- After spawning on the human team, stand at an armoury and press `F5`. The script grants momentum/credits, then runs `buy` for rifles, lasgun, shotgun, mass driver, pulse rifle, chaingun, flamer, lucifer cannon, painsaw, construction kit, jetpack, battlesuit, medium armour, radar, grenades, and firebombs. (Battlesuit and jetpack conflict; whichever is allowed last will stick.)
- Re-hit `F5` after each respawn to instantly re-equip; no buy menu needed.

### Basic mechanics
- Humans build with the construction kit (CKit) and power buildables via reactor/repeater; aliens hatch from eggs and spend evolution points instead of credits.
- Momentum is team-wide and unlocks gear over time; we bypass it for sandbox play via the `give momentum` step in `autogear.cfg`.
- Building/deconstructing and healing teammates/buildings grant momentum; deconstructing live structures without replacing them costs momentum.
