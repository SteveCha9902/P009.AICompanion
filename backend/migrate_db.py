import sqlite3

conn = sqlite3.connect("companion.db")
cursor = conn.cursor()

# 1. Recreate companions table with proper multi-character support (NO unique on user_id)
cursor.execute("PRAGMA foreign_keys = OFF")

cursor.execute("""
CREATE TABLE IF NOT EXISTS companions_new (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    lifecycle_status VARCHAR(20) DEFAULT 'available',
    is_system_character BOOLEAN DEFAULT 0,
    archived_at DATETIME,
    deleted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Copy old data if companions table exists
table_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companions'").fetchone()
if table_exists:
    # Check what columns exist in old companions
    cols = [col[1] for col in cursor.execute("PRAGMA table_info(companions)").fetchall()]
    print("Old columns:", cols)
    cursor.execute("""
        INSERT OR IGNORE INTO companions_new (id, user_id, name, created_at, updated_at)
        SELECT id, user_id, name, created_at, updated_at FROM companions
    """)
    cursor.execute("DROP TABLE companions")

cursor.execute("ALTER TABLE companions_new RENAME TO companions")
cursor.execute("CREATE INDEX IF NOT EXISTS ix_companions_user_id ON companions (user_id)")

# 2. Ensure character_dnas table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS character_dnas (
    id VARCHAR PRIMARY KEY,
    companion_id VARCHAR UNIQUE NOT NULL,
    archetype VARCHAR,
    role_title VARCHAR,
    speaking_style VARCHAR,
    avatar_preset VARCHAR,
    voice_id VARCHAR,
    mbti VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# 3. Ensure user_character_preferences table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_character_preferences (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR UNIQUE NOT NULL,
    active_companion_id VARCHAR NOT NULL,
    switched_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# 4. Seed Standard Companions for default_user (Genie, Mani, Hana)
companions = [
    ("default_companion", "default_user", "Genie", "available", 1),
    ("c_mani", "default_user", "마니", "available", 1),
    ("c_hana", "default_user", "하나", "available", 1),
]

for c_id, u_id, name, status, is_sys in companions:
    cursor.execute("""
        INSERT INTO companions (id, user_id, name, lifecycle_status, is_system_character)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            lifecycle_status = excluded.lifecycle_status,
            is_system_character = excluded.is_system_character
    """, (c_id, u_id, name, status, is_sys))

# 5. Seed DNAs
dnas = [
    ("dna_genie", "default_companion", "wife", "다정한 아내", "warm_natural", "warm_wife_2d", "nova", "ENFJ"),
    ("dna_mani", "c_mani", "daughter", "사랑스러운 딸", "daughter_teen_natural", "lovely_daughter_2d", "shimmer", "ESFP"),
    ("dna_hana", "c_hana", "friend", "취미 친구", "casual_natural", "casual_friend_2d", "alloy", "ENTP"),
]

for dna_id, comp_id, arch, role, style, av, voice, mbti in dnas:
    cursor.execute("""
        INSERT INTO character_dnas (id, companion_id, archetype, role_title, speaking_style, avatar_preset, voice_id, mbti)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(companion_id) DO UPDATE SET
            role_title = excluded.role_title,
            speaking_style = excluded.speaking_style,
            avatar_preset = excluded.avatar_preset,
            voice_id = excluded.voice_id
    """, (dna_id, comp_id, arch, role, style, av, voice, mbti))

# 6. Ensure default preference is set
cursor.execute("""
    INSERT INTO user_character_preferences (id, user_id, active_companion_id)
    VALUES ('pref_default', 'default_user', 'default_companion')
    ON CONFLICT(user_id) DO UPDATE SET
        active_companion_id = excluded.active_companion_id
""")

cursor.execute("PRAGMA foreign_keys = ON")
conn.commit()

print("\n--- Current Companions for default_user ---")
for row in cursor.execute("SELECT id, user_id, name, lifecycle_status FROM companions WHERE user_id = 'default_user'").fetchall():
    print(row)

print("\n--- Current DNAs ---")
for row in cursor.execute("SELECT companion_id, role_title, avatar_preset, voice_id FROM character_dnas").fetchall():
    print(row)

print("\n--- Active Preference ---")
for row in cursor.execute("SELECT * FROM user_character_preferences").fetchall():
    print(row)

conn.close()
print("\n[SUCCESS] SQLite migration and 3 standard characters seeded!")
