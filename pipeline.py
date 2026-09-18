import requests
import psycopg2
import pandas as pd
import os
import schedule
import time
import warnings
from datetime import datetime
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

warnings.filterwarnings('ignore')
load_dotenv()

# ── CONFIG ─────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'database': 'pokemon_data',
    'user':     'postgres',
    'password': os.environ.get('DB_PASSWORD'),
    'port':     '5432'
}
# How many pokemon to fetch
POKEMON_LIMIT = 151

# ── SETUP DATABASE ─────────────────────────────────────────────────────────
def setup_database():
    # Create database
    try:
        setup_conn = psycopg2.connect(
            host='localhost', database='postgres',
            user='postgres', password=os.environ.get('DB_PASSWORD'), port='5432'
        )
        setup_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        setup_conn.cursor().execute('CREATE DATABASE pokemon_data')
        setup_conn.close()
        print('Database created!')
    except Exception as e:
        print(f'Database note: {e}')

    # Create tables
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemon (
            pokemon_id   INTEGER UNIQUE,
            name         VARCHAR(100),
            type1        VARCHAR(50),
            type2        VARCHAR(50),
            hp           INTEGER,
            attack       INTEGER,
            defense      INTEGER,
            sp_attack    INTEGER,
            sp_defense   INTEGER,
            speed        INTEGER,
            total_stats  INTEGER,
            height       INTEGER,
            weight       INTEGER,
            base_exp     INTEGER,
            species      VARCHAR(100),
            fetched_at   TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print('Database ready!')

# ── EXTRACT ────────────────────────────────────────────────────────────────
def extract(pokemon_id):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
    if response.status_code != 200:
        raise Exception(f'API error: {response.status_code}')
    return response.json()

# ── TRANSFORM ──────────────────────────────────────────────────────────────
def transform(data):
    print('  Transforming...')

    stats = {s['stat'] ['name']: s['base_stat'] for s in data['stats']}

    #Extract types
    types = [t['type']['name'] for t in data['types']]
    type1 = types[0] if len(types) > 0 else None
    type2 = types[1] if len(types) > 1 else None

    #Extract species name
    species = data['species']['name']

    return {
        'pokemon_id':  data['id'],
        'name':        data['name'],
        'type1':       type1,
        'type2':       type2,
        'hp':          stats.get('hp', 0),
        'attack':      stats.get('attack', 0),
        'defense':     stats.get('defense', 0),
        'sp_attack':   stats.get('special-attack', 0),
        'sp_defense':  stats.get('special-defense', 0),
        'speed':       stats.get('speed', 0),
        'total_stats': sum(stats.values()),
        'height':      data['height'],
        'weight':      data['weight'],
        'base_exp':    data.get('base_experience', 0),
        'species':     species,
        'fetched_at':  datetime.now(),
    }
# ── LOAD ───────────────────────────────────────────────────────────────────
def load(row, conn):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pokemon
        (pokemon_id, name, type1, type2, hp, attack, defense,
         sp_attack, sp_defense, speed, total_stats, height,
         weight, base_exp, species, fetched_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (pokemon_id) DO UPDATE SET
            fetched_at = EXCLUDED.fetched_at
    """, tuple(row.values()))
    conn.commit()

# ── MAIN PIPELINE ──────────────────────────────────────────────────────────
def run_pipeline():
    print(f'\n[{datetime.now().strftime("%H:%M:%S")}] Running Pokemon pipeline...')
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        loaded = 0

        for pokemon_id in range(1, POKEMON_LIMIT + 1):
            try:
                raw  = extract(pokemon_id)
                row  = transform(raw)
                load(row, conn)
                loaded += 1
                print(f'  ✅ {row["name"].capitalize()} loaded ({pokemon_id}/{POKEMON_LIMIT})')
                time.sleep(0.1)  # be nice to the API
            except Exception as e:
                print(f'  ❌ Error on pokemon {pokemon_id}: {e}')
                continue

        print(f'\n✅ Pipeline complete! {loaded} pokemon loaded')

        # Summary
        summary = pd.read_sql("""
            SELECT name, type1, type2, total_stats
            FROM pokemon
            ORDER BY total_stats DESC
            LIMIT 10
        """, conn)
        print('\n--- Top 10 Strongest Pokemon ---')
        print(summary.to_string(index=False))

        conn.close()

    except Exception as e:
        print(f'❌ Pipeline failed: {e}')

# ── RUN ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    setup_database()
    run_pipeline()

    # Pokemon data doesn't change often — run weekly
    schedule.every().week.do(run_pipeline)

    print('\nScheduler running — updates weekly.')
    while True:
        schedule.run_pending()
        time.sleep(60)