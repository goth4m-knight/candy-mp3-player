import sqlite3
import os

fullnames = []
filenames = []
mp3files = {}

conn = sqlite3.connect(f"C:/Users/{os.getlogin()}/CMPdata.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS songs_current (
            name text,
            fullpath text)
            """)

c.execute("""CREATE TABLE IF NOT EXISTS favourites (
            name text,
            fullpath text)
            """)


exclude = set(['AppData'])

for root, dirs, files in os.walk(f"C:/Users/{os.getlogin()}"):
    for file in files:
        dirs[:] = [d for d in dirs if d not in exclude]
        if file.endswith(".mp3") or file.endswith(".wav"):
            fullname = os.path.join(root, file).replace('\\', '/')
            filename = os.path.basename(fullname)
            fullnames.append(fullname)
            filenames.append(filename.replace('.mp3', '').replace('.wav', ''))

try:
    for root, dirs, files in os.walk("D:"):
        for file in files:
            if file.endswith(".mp3"):
                fullname = os.path.join(root, file).replace('\\', '/')
                filename = os.path.basename(fullname)
                fullnames.append(fullname)
                filenames.append(filename.replace('.mp3', '').replace('.wav', ''))

except Exception as e:
    pass

try:
    for root, dirs, files in os.walk("E:"):
        for file in files:
            if file.endswith(".mp3"):
                fullname = os.path.join(root, file).replace('\\', '/')
                filename = os.path.basename(fullname)
                fullnames.append(fullname)
                filenames.append(filename.replace('.mp3', '').replace('.wav', ''))
                
except Exception as e:
    pass

try:
    for root, dirs, files in os.walk("F:"):
        for file in files:
            if file.endswith(".mp3"):
                fullname = os.path.join(root, file).replace('\\', '/')
                filename = os.path.basename(fullname)
                fullnames.append(fullname)
                filenames.append(filename.replace('.mp3', '').replace('.wav', ''))

except Exception as e:
    pass

for i in range(len(filenames)):
    mp3files[filenames[i]] = fullnames[i]

for keys in mp3files.keys():
    c.execute("INSERT INTO songs_current(name, fullpath) VALUES(?, ?)", (keys, mp3files[keys]))

c.execute("DROP TABLE IF EXISTS songs")
c.execute("ALTER TABLE songs_current RENAME TO songs")

conn.commit()
conn.close()
