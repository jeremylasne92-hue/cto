import os
from datetime import datetime, timedelta

# Database Configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///srs_engine.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# FSRS-5 Algorithm Parameters
FSRS5_PARAMS = {
    'w': [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.7, 0.3, 0.08, 5.5, 0.71, 0.03, 1.52, 0.15, 5.3],
}

# Retention target for scheduling (90% = 0.9)
TARGET_RETENTION = 0.9

# Session Configuration
SESSION_TARGET_DURATION_MINUTES = 25
SESSION_TARGET_CARD_COUNT = 20

# Leech Detection
LEECH_THRESHOLD_LAPSES = 2  # Flag cards with >2 lapses

# Retention Mechanics - Category Decay Rates
CATEGORY_DECAY_RATES = {
    'tech_framework': 0.5,      # 50%/year
    'language': 0.3,             # 30%/year
    'historical_fact': 0.01,     # 1%/year
    'default': 0.3,              # 30%/year (default)
}

# Date format
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Session Warmup Config
WARMUP_DIFFICULTY_RANGE = (4, 6)   # Medium difficulty cards for warmup
MAIN_DIFFICULTY_MIN = 7             # Hard cards in main session
COOLDOWN_DIFFICULTY_MAX = 5         # Easy cards for cooldown
