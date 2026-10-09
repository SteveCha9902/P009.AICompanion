import sqlite3

conn = sqlite3.connect("companion.db")
c = conn.cursor()
c.execute("UPDATE companions SET name = 'Genie (지니)' WHERE id = 'default_companion'")
c.execute("UPDATE companions SET name = 'Mani (마니)' WHERE id = 'c_mani'")
c.execute("UPDATE companions SET name = 'Hana (하나)' WHERE id = 'c_hana'")

c.execute("UPDATE character_dnas SET role_title = '아내 (Wife)' WHERE companion_id = 'default_companion'")
c.execute("UPDATE character_dnas SET role_title = '사랑스러운 딸 (Daughter)' WHERE companion_id = 'c_mani'")
c.execute("UPDATE character_dnas SET role_title = '취미 친구 (Friend)' WHERE companion_id = 'c_hana'")

conn.commit()

for r in c.execute("SELECT id, name FROM companions").fetchall():
    print(r)

conn.close()
