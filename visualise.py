import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host='localhost',
    database='pokemon_data',
    user='postgres',
    password=os.environ.get('DB_PASSWORD'),
    port='5432'
)

# ── 1. TOP 20 STRONGEST ────────────────────────────────────────────────────
def plot_strongest():
    df = pd.read_sql("""
        SELECT name, total_stats, type1
        FROM pokemon
        ORDER BY total_stats DESC
        LIMIT 20
    """, conn)

    colors = {
        'fire': '#FF4500', 'water': '#4169E1', 'grass': '#228B22',
        'psychic': '#FF69B4', 'electric': '#FFD700', 'dragon': '#8B008B',
        'normal': '#A9A9A9', 'ice': '#00CED1', 'fighting': '#B22222',
        'poison': '#9400D3', 'ground': '#D2691E', 'flying': '#87CEEB',
        'bug': '#9ACD32', 'rock': '#808000', 'ghost': '#483D8B',
    }
    bar_colors = [colors.get(t, '#5b4fcf') for t in df['type1']]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(df['name'][::-1], df['total_stats'][::-1], color=bar_colors[::-1])
    ax.bar_label(bars, padding=3)
    ax.set_title('Top 20 Strongest Pokemon (Total Stats)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Total Stats')
    plt.tight_layout()
    plt.savefig('strongest.png', dpi=150)
    plt.show()
    print('Saved strongest.png')

# ── 2. POKEMON BY TYPE ─────────────────────────────────────────────────────
def plot_by_type():
    df = pd.read_sql("""
        SELECT type1, COUNT(*) as count
        FROM pokemon
        GROUP BY type1
        ORDER BY count DESC
    """, conn)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(df['type1'], df['count'], color='#5b4fcf')
    ax.bar_label(bars, padding=3)
    ax.set_title('Pokemon Count by Type', fontsize=16, fontweight='bold')
    ax.set_xlabel('Type')
    ax.set_ylabel('Number of Pokemon')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('by_type.png', dpi=150)
    plt.show()
    print('Saved by_type.png')

# ── 3. STAT COMPARISON BY TYPE ─────────────────────────────────────────────
def plot_stats_by_type():
    df = pd.read_sql("""
        SELECT type1,
               ROUND(AVG(hp), 1) as avg_hp,
               ROUND(AVG(attack), 1) as avg_attack,
               ROUND(AVG(defense), 1) as avg_defense,
               ROUND(AVG(speed), 1) as avg_speed
        FROM pokemon
        GROUP BY type1
        ORDER BY avg_attack DESC
    """, conn)

    x = range(len(df))
    width = 0.2

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar([i - width*1.5 for i in x], df['avg_hp'],      width, label='HP',      color='#ef4444')
    ax.bar([i - width*0.5 for i in x], df['avg_attack'],  width, label='Attack',  color='#f97316')
    ax.bar([i + width*0.5 for i in x], df['avg_defense'], width, label='Defense', color='#22c55e')
    ax.bar([i + width*1.5 for i in x], df['avg_speed'],   width, label='Speed',   color='#3b82f6')
    ax.set_xticks(x)
    ax.set_xticklabels(df['type1'], rotation=45, ha='right')
    ax.set_title('Average Stats by Type', fontsize=16, fontweight='bold')
    ax.set_ylabel('Average Stat Value')
    ax.legend()
    plt.tight_layout()
    plt.savefig('stats_by_type.png', dpi=150)
    plt.show()
    print('Saved stats_by_type.png')

# ── 4. ATTACK vs DEFENSE SCATTER ───────────────────────────────────────────
def plot_attack_vs_defense():
    df = pd.read_sql("""
        SELECT name, attack, defense, type1, total_stats
        FROM pokemon
    """, conn)

    colors = {
        'fire': '#FF4500', 'water': '#4169E1', 'grass': '#228B22',
        'psychic': '#FF69B4', 'electric': '#FFD700', 'dragon': '#8B008B',
        'normal': '#A9A9A9', 'ice': '#00CED1', 'fighting': '#B22222',
        'poison': '#9400D3', 'ground': '#D2691E', 'flying': '#87CEEB',
        'bug': '#9ACD32', 'rock': '#808000', 'ghost': '#483D8B',
    }

    fig, ax = plt.subplots(figsize=(12, 8))
    for type1, group in df.groupby('type1'):
        ax.scatter(group['attack'], group['defense'],
                  label=type1, color=colors.get(type1, '#5b4fcf'),
                  alpha=0.7, s=60)

    # Label the extremes
    for _, row in df.nlargest(5, 'attack').iterrows():
        ax.annotate(row['name'], (row['attack'], row['defense']),
                   textcoords='offset points', xytext=(5, 5), fontsize=8)

    ax.set_title('Attack vs Defense — All Pokemon', fontsize=16, fontweight='bold')
    ax.set_xlabel('Attack')
    ax.set_ylabel('Defense')
    ax.legend(loc='upper right', fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig('attack_vs_defense.png', dpi=150)
    plt.show()
    print('Saved attack_vs_defense.png')

# ── 5. SPEED vs TOTAL STATS ────────────────────────────────────────────────
def plot_speed_vs_total():
    df = pd.read_sql("""
        SELECT name, speed, total_stats, type1
        FROM pokemon
        ORDER BY speed DESC
    """, conn)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.scatter(df['speed'], df['total_stats'], color='#5b4fcf', alpha=0.6, s=60)

    # Label top 5 fastest
    for _, row in df.nlargest(5, 'speed').iterrows():
        ax.annotate(row['name'], (row['speed'], row['total_stats']),
                   textcoords='offset points', xytext=(5, 5), fontsize=9)

    ax.set_title('Speed vs Total Stats', fontsize=16, fontweight='bold')
    ax.set_xlabel('Speed')
    ax.set_ylabel('Total Stats')
    plt.tight_layout()
    plt.savefig('speed_vs_total.png', dpi=150)
    plt.show()
    print('Saved speed_vs_total.png')

# ── 6. HEAVIEST AND LIGHTEST ───────────────────────────────────────────────
def plot_weight():
    heaviest = pd.read_sql("""
        SELECT name, weight FROM pokemon ORDER BY weight DESC LIMIT 10
    """, conn)

    lightest = pd.read_sql("""
        SELECT name, weight FROM pokemon ORDER BY weight ASC LIMIT 10
    """, conn)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    ax1.barh(heaviest['name'][::-1], heaviest['weight'][::-1], color='#ef4444')
    ax1.set_title('Top 10 Heaviest Pokemon', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Weight (hectograms)')

    ax2.barh(lightest['name'][::-1], lightest['weight'][::-1], color='#22c55e')
    ax2.set_title('Top 10 Lightest Pokemon', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Weight (hectograms)')

    plt.tight_layout()
    plt.savefig('weight.png', dpi=150)
    plt.show()
    print('Saved weight.png')

# ── RUN ALL ────────────────────────────────────────────────────────────────
print('Generating Pokemon visualisations...')
plot_strongest()
plot_by_type()
plot_stats_by_type()
plot_attack_vs_defense()
plot_speed_vs_total()
plot_weight()

conn.close()
print('\nAll charts saved!')