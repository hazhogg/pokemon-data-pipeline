# Pokemon Data Pipeline

A data pipeline that fetches stats for all 151 original Pokemon from the PokeAPI, stores them in PostgreSQL and generates visualisation charts comparing stats, types and abilities.

## What it does

- Fetches all 151 original Pokemon from the free PokeAPI
- Stores full stats (HP, Attack, Defense, Speed etc.) in PostgreSQL
- Analyses strongest Pokemon, best types and stat breakdowns
- Generates 6 visualisation charts
- Runs weekly to stay up to date
- No API key needed — completely free

## Tech stack

- Python
- pandas
- PostgreSQL
- psycopg2
- PokeAPI (free, no key required)
- schedule
- matplotlib

## Sample output

```
--- Top 10 Strongest Pokemon ---
     name    type1  type2  total_stats
   mewtwo  psychic    NaN          680
dragonite   dragon flying          600
      mew  psychic    NaN          600
   zapdos electric flying          580
  moltres     fire flying          580
 articuno      ice flying          580
 arcanine     fire    NaN          555
 gyarados    water flying          540
  snorlax   normal    NaN          540
   lapras    water    ice          535
```

## Database table

### pokemon

| Column | Description |
|---|---|
| pokemon_id | National Pokedex number |
| name | Pokemon name |
| type1 | Primary type |
| type2 | Secondary type (if any) |
| hp | HP stat |
| attack | Attack stat |
| defense | Defense stat |
| sp_attack | Special Attack stat |
| sp_defense | Special Defense stat |
| speed | Speed stat |
| total_stats | Sum of all stats |
| height | Height in decimetres |
| weight | Weight in hectograms |
| base_exp | Base experience yield |
| species | Species name |

## Setup

1. Install PostgreSQL

2. Clone the repo:
```bash
git clone https://github.com/yourusername/pokemon-pipeline.git
cd pokemon-pipeline
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```
DB_PASSWORD=yourpassword
DB_HOST=localhost
```

5. Run the pipeline:
```bash
python pipeline.py
```

## Visualisations

```bash
python visualise.py
```

Generates 6 charts:
- Top 20 strongest Pokemon by total stats
- Pokemon count by type
- Average stats by type (HP, Attack, Defense, Speed)
- Attack vs Defense scatter plot coloured by type
- Speed vs Total Stats scatter plot
- Top 10 heaviest and lightest Pokemon

## Example queries

```sql
-- Top 10 strongest Pokemon
SELECT name, type1, type2, total_stats
FROM pokemon
ORDER BY total_stats DESC
LIMIT 10;

-- Average stats by type
SELECT type1,
       ROUND(AVG(hp), 1) as avg_hp,
       ROUND(AVG(attack), 1) as avg_attack,
       ROUND(AVG(defense), 1) as avg_defense,
       ROUND(AVG(speed), 1) as avg_speed
FROM pokemon
GROUP BY type1
ORDER BY avg_attack DESC;

-- Fastest Pokemon
SELECT name, speed, type1, total_stats
FROM pokemon
ORDER BY speed DESC
LIMIT 10;

-- Best single type Pokemon
SELECT name, type1, total_stats
FROM pokemon
WHERE type2 IS NULL
ORDER BY total_stats DESC
LIMIT 10;

-- Most common dual types
SELECT type1, type2, COUNT(*) as count
FROM pokemon
WHERE type2 IS NOT NULL
GROUP BY type1, type2
ORDER BY count DESC;
```

## Schedule

Pipeline runs automatically every week. Pokemon stats are static so weekly updates are more than enough.

## Project structure

```
pokemon-pipeline/
├── pipeline.py      ← main ETL pipeline
├── visualise.py     ← chart generation
├── requirements.txt ← dependencies
├── .gitignore       ← excludes .env and charts
└── .env             ← database password (not pushed)
```

## Data source

Data from [PokeAPI](https://pokeapi.co/) — a free, open RESTful API for Pokemon data. No API key required.

## Author

Harry
