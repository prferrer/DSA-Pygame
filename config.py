WIDTH  = 1280
HEIGHT = 720

WHITE = (255, 255, 255)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)

# ── Game timer ────────────────────────────────
GAME_DURATION   = 180000   # 3 minute game time
SHRINK_START    = 60000    # shrink starts at 1 min
SHRINK_INTERVAL = 5000     # map shrinks every 5 seconds

# ── Powerups ──────────────────────────────────
POWERUP_DESPAWN = 15000
POWERUP_RESPAWN = 5000

# ── Movement ──────────────────────────────────
NORMAL_MOVE_DELAY = 100
FAST_MOVE_DELAY   = 50
SLOW_MOVE_DELAY   = 200

# ── Melee ─────────────────────────────────────
MELEE_COOLDOWN      = 800    # ms between swings (timing-based, prevents spam)
MELEE_STUN_DURATION = 1200   # ms the struck player is stunned
MELEE_RANGE         = 1      # tiles — must be directly adjacent in facing direction
MELEE_ANIM_DURATION = 400    # ms for the hit-spark animation to play

# ── Armor ─────────────────────────────────────
ARMOR_RESPAWN_TIME  = 8000   # ms between armor pickups appearing
ARMOR_DESPAWN_TIME  = 12000  # ms an armor pickup stays on the map before vanishing
ARMOR_MAX_STACK     = 2      # maximum armor points a player can carry