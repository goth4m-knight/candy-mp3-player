import os
import sqlite3
import threading
import time
from sys import argv, exit
from pytube import YouTube
import lyricsgenius
from PyQt5.QtCore import Qt, QUrl, QTime, QEvent
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, \
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, \
    QStyle, QSlider, QShortcut, QLineEdit, QComboBox, QListWidget, QTabWidget, QPlainTextEdit, QAction, QMenu, QDialog, QMessageBox
import json
from pathlib import Path

genius = lyricsgenius.Genius('J6lSgKHLkgRJHgFNjFi0YWP8l9TRxP9gWg_xACDdfzw8L6ZDYqBgTDLa9njTDTKT', skip_non_songs=True,
                             excluded_terms=["(Remix)", "(Live)"],
                             remove_section_headers=True)

mp3files = {}
song_to_add_to_playlist = []

HOME_PATH = str(Path.home()).replace('\\', '/')

if "CMPdata.db" in os.listdir(HOME_PATH):
    conn = sqlite3.connect(f"{HOME_PATH}/CMPdata.db")
    c = conn.cursor()
else:
    os.startfile("database.exe")
    time.sleep(2.5)
    conn = sqlite3.connect(f"{HOME_PATH}/CMPdata.db")
    c = conn.cursor()

if 'CMPdata.json' in os.listdir(f"{HOME_PATH}"):
    f = open(f'{HOME_PATH}/CMPdata.json', 'r')
    data = json.load(f)
else:
    data = None


class CandyMP3Player(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 840, 930
        self.setGeometry(450, 50, self.window_width, self.window_height)
        self.setMaximumWidth(self.window_width)
        self.setMaximumHeight(self.window_height)
        self.setWindowTitle("Candy Music Player")
        self.setWindowIcon(QIcon("icons/mp3_player_icon1.ico"))
        self.played = []
        self.playing = data['last_played'] if data else None
        self.total_time = data['total_time'] if data else 100
        self.time_elapsed = data['time_elapsed'] if data else 0
        self.volume_value = data['volume'] if data else 100
        self.last_playlist = data['last_playlist'] if data else "Songs"
        self.lyrics_searched = False
        self.repeat_one = data['repeat'] if data else False
        self.once = data['once'] if data else False
        self.create_player()
        self.get_songs()
        self.adjusting()

    def create_player(self):
        self.list = QListWidget()
        self.list.setFont(QFont('Sitka Text', 11))
        self.player = QMediaPlayer()
        self.list.itemClicked.connect(self.file)
        self.list.installEventFilter(self)

        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.playAudioFile)
        self.playBtn.setFont(QFont('Sitka Text', 11))

        self.muteBtn = QPushButton()
        self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.muteBtn.clicked.connect(self.mute)
        self.muteBtn.setToolTip("Mute(Shortcut: Press M)")
        self.muteBtn.setFont(QFont('Sitka Text', 11))

        self.upBtn = QPushButton()
        self.upBtn.setIcon(QIcon('icons/volume up.png'))
        self.upBtn.clicked.connect(self.volumeUp)
        self.upBtn.setToolTip("Volume Up(Shortcut: +)")
        self.upBtn.setFont(QFont('Sitka Text', 11))

        self.downBtn = QPushButton()
        self.downBtn.setIcon(QIcon('icons/volume down.png'))
        self.downBtn.clicked.connect(self.volumeDown)
        self.downBtn.setToolTip("Volume Down(Shortcut: -)")
        self.downBtn.setFont(QFont('Sitka Text', 11))

        self.backwardBtn = QPushButton()
        self.backwardBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.backwardBtn.clicked.connect(self.playPrevious)
        self.backwardBtn.setToolTip("Previous(Shortcut: Arrow Left Key)")
        self.backwardBtn.setFont(QFont('Sitka Text', 11))

        self.forwardBtn = QPushButton()
        self.forwardBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.forwardBtn.clicked.connect(self.playNext)
        self.forwardBtn.setToolTip("Next(Shortcut: Arrow Right Key)")
        self.forwardBtn.setFont(QFont('Sitka Text', 11))

        self.slider = QSlider(Qt.Horizontal)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, self.total_time)
        self.slider.setValue(self.time_elapsed)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.vslider = QSlider(Qt.Horizontal)
        self.vslider = QSlider(Qt.Horizontal, self)
        self.vslider.setRange(0, 100)
        self.vslider.setValue(self.volume_value)
        self.vslider.setFixedWidth(90)
        self.vslider.setAttribute(Qt.WA_TranslucentBackground, True)
        self.vslider.sliderMoved.connect(self.volume)

        self.rateBox = QComboBox()
        self.rateBox.addItem("0.25x", 0.25)
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("0.75x", 0.75)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("1.25x", 1.25)
        self.rateBox.addItem("1.5x", 1.5)
        self.rateBox.addItem("1.75x", 1.75)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.setCurrentIndex(3)
        self.rateBox.setFixedWidth(70)
        self.rateBox.setFont(QFont('Sitka Text', 8))
        self.rateBox.activated.connect(self.updateRate)

        self.tablebox = QComboBox()
        self.tablebox.setFont(QFont('Sitka Text', 11))
        self.tablebox.addItem("Songs")
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for tables in c.fetchall():
            for table in tables:
                if table != "songs":
                    self.tablebox.addItem(table.title())
        self.tablebox.setCurrentText(self.last_playlist)
        self.tablebox.currentIndexChanged.connect(self.get_songs)

        self.repeatBtn = QPushButton()
        self.repeatBtn.setIcon(QIcon("icons/repeat.png"))
        self.repeatBtn.clicked.connect(self.repeat_or_not)
        self.repeatBtn.setToolTip("Repeat All")
        self.repeatBtn.setFont(QFont('Sitka Text', 11))

        self.repeatoneBtn = QPushButton()
        self.repeatoneBtn.setIcon(QIcon("icons/repeat1.png"))
        self.repeatoneBtn.clicked.connect(self.repeat_or_not)
        self.repeatoneBtn.setToolTip("Repeat One")
        self.repeatoneBtn.setFont(QFont('Sitka Text', 11))

        self.playallBtn = QPushButton()
        self.playallBtn.setIcon(QIcon("icons/play_all.png"))
        self.playallBtn.clicked.connect(self.repeat_or_not)
        self.playallBtn.setToolTip("Play All")
        self.playallBtn.setFont(QFont('Sitka Text', 11))

        self.lbl = QLineEdit(' 00:00:00 ')
        self.lbl.setReadOnly(True)
        self.lbl.setFixedWidth(90)
        self.lbl.setUpdatesEnabled(True)
        self.lbl.setFont(QFont('Sitka Text', 9))

        self.vlbl = QLineEdit('Volume: 100')
        self.vlbl.setReadOnly(True)
        self.vlbl.setFixedWidth(120)
        self.vlbl.setUpdatesEnabled(True)
        self.vlbl.setFont(QFont('Sitka Text', 9))

        self.plbl = QLineEdit('Playback Rate:')
        self.plbl.setReadOnly(True)
        self.plbl.setFixedWidth(133)
        self.plbl.setUpdatesEnabled(True)
        self.plbl.setFont(QFont('Sitka Text', 9))

        self.elbl = QLineEdit(' 00:00:00 ')
        self.elbl.setReadOnly(True)
        self.elbl.setFixedWidth(90)
        self.elbl.setUpdatesEnabled(True)
        self.elbl.setFont(QFont('Sitka Text', 9))

        self.lyricBtn = QPushButton()
        self.lyricBtn.setText('Search')
        self.lyricBtn.clicked.connect(self.getLyrics)
        self.lyricBtn.setToolTip("Search For Lyrics")
        self.lyricBtn.setFont(QFont('Sitka Text', 11))

        self.deleteBtn = QPushButton()
        self.deleteBtn.setIcon(QIcon('icons/delete.png'))
        self.deleteBtn.setToolTip('Delete Playlist')
        self.deleteBtn.clicked.connect(self.delete_playlist)
        self.deleteBtn.setFont(QFont('Sitka Text', 11))
        self.deleteBtn.setFixedSize(45, 40)
        self.deleteBtn.hide()

        self.slbl = QLineEdit()
        self.slbl.setFont(QFont('Sitka Text', 11))
        self.slbl.setPlaceholderText('Search for Lyrics')
        self.slbl.setUpdatesEnabled(True)

        self.songlbl = QPlainTextEdit()
        self.songlbl.insertPlainText('')
        self.songlbl.setFont(QFont('Sitka Text', 11))
        self.songlbl.setReadOnly(True)
        self.songlbl.setUpdatesEnabled(True)

        self.sentry = QLineEdit()
        self.sentry.setFont(QFont('Sitka Text', 11))
        self.sentry.setPlaceholderText("Search Songs (Paste url to download)")
        self.sentry.setUpdatesEnabled(True)

        self.download_btn = QPushButton()
        self.download_btn.setIcon(QIcon("icons/download.png"))
        self.download_btn.setToolTip("Download (Copy & Paste the youtube url in Search Songs)")
        self.download_btn.clicked.connect(self.download)
        self.download_btn.setFixedSize(45, 40)

        self.shortcut = QShortcut(QKeySequence(" "), self)
        self.shortcut.activated.connect(self.playAudioFile)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.playNext)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.playPrevious)
        self.shortcut = QShortcut(QKeySequence("+"), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence("-"), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence("m"), self)
        self.shortcut.activated.connect(self.mute)
        self.shortcut = QShortcut(QKeySequence("r"), self)
        self.shortcut.activated.connect(self.repeat_or_not)

        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(400, 300)

        self.tabs.addTab(self.tab1, "Songs")
        self.tabs.addTab(self.tab2, "Lyrics")
        self.tabs.setFont(QFont('Sitka Text', 11))

        sbox = QHBoxLayout()
        sbox.addWidget(self.sentry)
        sbox.addWidget(self.download_btn)
        sbox.addWidget(self.deleteBtn)
        sbox.addWidget(self.tablebox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.playBtn)
        hbox.addWidget(self.backwardBtn)
        hbox.addWidget(self.forwardBtn)
        hbox.addWidget(self.downBtn)
        hbox.addWidget(self.upBtn)
        hbox.addWidget(self.muteBtn)
        hbox.addWidget(self.vlbl)
        hbox.addWidget(self.vslider)
        hbox.addWidget(self.plbl)
        hbox.addWidget(self.rateBox)
        hbox.addWidget(self.playallBtn)
        hbox.addWidget(self.repeatBtn)
        hbox.addWidget(self.repeatoneBtn)
        self.playallBtn.hide()
        self.repeatoneBtn.hide()

        ahbox = QHBoxLayout()
        ahbox.addWidget(self.lbl)
        ahbox.addWidget(self.slider)
        ahbox.addWidget(self.elbl)

        self.flayout = QVBoxLayout()
        self.flayout.addLayout(sbox)
        self.flayout.addWidget(self.list)
        self.flayout.addLayout(ahbox)
        self.flayout.addLayout(hbox)

        self.aaa = QHBoxLayout()
        self.aaa.addWidget(self.slbl)
        self.aaa.addWidget(self.lyricBtn)

        self.llayout = QVBoxLayout()
        self.llayout.addLayout(self.aaa)
        self.llayout.addWidget(self.songlbl)

        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addLayout(self.flayout)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addLayout(self.llayout)
        self.tab2.setLayout(self.tab2.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.player.stateChanged.connect(self.mediastate_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.list.itemClicked.connect(self.playAudioFile)
        self.list.itemClicked.connect(self.get_current_song)
        self.list.itemSelectionChanged.connect(self.nameChange)
        self.sentry.textChanged.connect(self.search)
        self.tablebox.currentTextChanged.connect(self.playlist_changed)
        self.tabs.tabBarClicked.connect(self.lyrics)
        self.x = 0
        self.x += 1
        self.list.clear()
        for keys in mp3files.keys():
            self.list.insertItem(self.x, keys)
        self.list.sortItems(Qt.AscendingOrder)
        self.volume()

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.list:
            menu = QMenu()
            add_to_fav = QAction("Add to Favourite")
            add_to_playlist = QAction("Add to Playlist")
            remove = QAction("Remove from Playlist")
            delete = QAction("Delete")
            if self.tablebox.currentText() == "Songs":
                menu.addAction(add_to_fav)
                menu.addAction(add_to_playlist)
                menu.addAction(delete)
            else:
                menu.addAction(add_to_playlist)
                menu.addAction(remove)
                menu.addAction(delete)
            menu_click = menu.exec(event.globalPos())

            if menu_click == add_to_fav:
                c.execute("INSERT INTO favourites(name, fullpath) VALUES(?, ?)",
                          (self.list.currentItem().text(), mp3files[self.list.currentItem().text()]))
                conn.commit()
            if menu_click == add_to_playlist:
                song_to_add_to_playlist.append(self.list.currentItem().text())
                song_to_add_to_playlist.append(mp3files[self.list.currentItem().text()])
                self.popup = Popup(self.tablebox)
                self.popup.show()
            if menu_click == remove:
                if self.tablebox.currentText() == "Songs":
                    self.list.takeItem(self.list.currentRow())
                else:
                    c.execute(f"DELETE FROM {self.tablebox.currentText()} WHERE name='{self.list.currentItem().text()}'")
                    conn.commit()
                    self.get_songs()
            if menu_click == delete:
                os.remove(mp3files[self.list.currentItem().text()])
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                for tables in c.fetchall():
                    for table in tables:
                        c.execute(f"DELETE FROM {table} WHERE name='{self.list.currentItem().text()}'")
                conn.commit()
            if len(self.played) >= 1:
                self.playing = self.played[-1]
            self.get_songs()
            return True
        return super(CandyMP3Player, self).eventFilter(source, event)

    def adjusting(self):
        try:
            if self.playing:
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.playing])))
            self.set_position(self.time_elapsed)
            self.position_changed(self.time_elapsed)
            while True:
                if not self.repeat_one and not self.once:
                    self.repeatoneBtn.hide()
                    self.playallBtn.hide()
                    self.repeatBtn.show()
                    break

                elif self.repeat_one and not self.once:
                    self.repeatBtn.hide()
                    self.playallBtn.hide()
                    self.repeatoneBtn.show()
                    break

                elif not self.repeat_one:
                    self.repeatBtn.hide()
                    self.repeatoneBtn.hide()
                    self.playallBtn.show()
                    break
        except Exception:
            pass

    def get_songs(self):
        c.execute(f"""SELECT * FROM {self.tablebox.currentText()}""")
        mp3files.clear()
        filenames = []
        fullpath = []
        for both in c.fetchall():
            filenames.append(both[0])
            fullpath.append(both[1])

        for i in range(len(filenames)):
            mp3files[filenames[i]] = fullpath[i]
        self.list.clear()
        for keys in mp3files.keys():
            self.list.insertItem(self.x, keys)
        self.list.sortItems(Qt.AscendingOrder)
        if self.playing is not None:
            try:
                item = self.list.findItems(self.playing, Qt.MatchExactly)
                index = self.list.row(item[0])
                self.list.setCurrentRow(index)
            except Exception:
                pass

    def download(self):
        try:
            url = self.sentry.text()
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            self.message_box("Download", f"Downloading - {yt.title}")
            path = f"{HOME_PATH}/Music"
            out_file = stream.download(output_path=path)
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            self.sentry.clear()
            self.message_box("Download", f"Downloaded - {yt.title} in {path}")
            c.execute("""INSERT INTO songs(name, fullpath) VALUES(?, ?)""", (yt.title, new_file.replace('\\', '/')))
            conn.commit()
            self.get_songs()
        except Exception as e:
            self.error_box("Error Downloading", str(e))

    def message_box(self, win_title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(win_title)
        msg.setWindowIcon(QIcon("icons/mp3_player_icon1"))
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def error_box(self, win_title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(win_title)
        msg.setWindowIcon(QIcon("icons/mp3_player_icon1"))
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def playlist_changed(self):
        if self.tablebox.currentText() in ['Songs', 'Favourites']:
            self.deleteBtn.hide()
        else:
            self.deleteBtn.show()

    def delete_playlist(self):
        index = self.tablebox.currentIndex()
        c.execute(f"""DROP TABLE IF EXISTS {self.tablebox.currentText()}""")
        self.tablebox.setCurrentText("Songs")
        self.tablebox.removeItem(index)

    def nameChange(self):
        try:
            self.setWindowTitle(f'Playing - {self.list.currentItem().text()}')
            self.slbl.setText(
                f'{self.list.currentItem().text().split("(Official")[0].split("(MP3")[0].split("(Mp3")[0].split("(mp3")[0]}')
        except Exception:
            pass
        self.lyrics_searched = False

    def lyrics(self, index):
        def lyrics():
            if index == 1:
                if not self.lyrics_searched:
                    try:
                        self.songlbl.setPlainText("Searching...")
                        name = self.slbl.text()
                        song = genius.search_song(name)
                        self.songlbl.clear()
                        self.songlbl.insertPlainText(f"{song.lyrics}\n")

                    except Exception:
                        self.songlbl.clear()
                        self.songlbl.setPlainText(f"No Lyrics Found.\nPlease Check Your Internet Connection."
                                                  f"\nYou can Type In The Song Name In Search Box.")

        threading.Thread(target=lyrics).start()
        self.lyrics_searched = True

    def getLyrics(self):
        try:
            self.songlbl.setPlainText("Searching...")
            name = self.slbl.text()
            song = genius.search_song(name)
            self.songlbl.clear()
            self.songlbl.insertPlainText(f"{song.lyrics}\n")

        except Exception:
            self.songlbl.clear()
            self.songlbl.setPlainText(f"No Lyrics Found.\nPlease Check Your Internet Connection.\nYou can Type In "
                                      f"The Song Name In Search Box.")

    def repeat_or_not(self):
        while True:
            if not self.repeat_one and not self.once:
                self.repeatBtn.hide()
                self.playallBtn.hide()
                self.repeatoneBtn.show()
                self.repeat_one = True
                self.once = False
                break

            elif self.repeat_one and not self.once:
                self.repeat_one = False
                self.repeatBtn.hide()
                self.playallBtn.show()
                self.repeatoneBtn.hide()
                self.once = True
                break

            elif not self.repeat_one:
                self.repeat_one = False
                self.repeatBtn.show()
                self.playallBtn.hide()
                self.repeatoneBtn.hide()
                self.once = False
                break

    def statusChanged(self, status):
        if not self.repeat_one and not self.once:
            if status == QMediaPlayer.EndOfMedia:
                self.playNext()

        elif not self.repeat_one and self.once:
            if status == QMediaPlayer.EndOfMedia:
                try:
                    self.list.setCurrentRow(self.list.currentRow() + 1)
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
                    self.player.play()

                except Exception:
                    self.setWindowTitle('Candy MP3 Player')
                    self.player.stop()

        if self.repeat_one and not self.once:
            try:
                if status == QMediaPlayer.EndOfMedia:
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
                    self.player.play()
            except Exception:
                self.list.setCurrentRow(0)
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
                self.player.play()

    def search(self):
        songlist = []
        songlist.clear()
        self.list.clear()
        for keys in mp3files.keys():
            db = keys.replace(' ', '').replace('-', '').lower()
            search_song = self.sentry.text().replace(' ', '').replace('-', '').lower()
            if search_song in db:
                songlist.append(keys)

        for song in songlist:
            self.list.insertItem(self.x, song)
        self.list.sortItems(Qt.AscendingOrder)
        if self.playing is not None:
            try:
                item = self.list.findItems(self.playing, Qt.MatchExactly)
                index = self.list.row(item[0])
                self.list.setCurrentRow(index)
            except Exception:
                pass

    def file(self):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))

    def playAudioFile(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playBtn.setToolTip("Play")
            self.setWindowTitle(f'Paused - {self.list.currentItem().text()}')

        else:
            self.player.play()
            self.playBtn.setToolTip("Pause")
            self.setWindowTitle(f'Playing - {self.list.currentItem().text()}')
        self.get_current_song()

    def get_current_song(self):
        self.playing = self.list.currentItem().text()
        self.played.append(self.playing)

    def playbackRate(self):
        return self.rateBox.itemData(self.rateBox.currentIndex())

    def updateRate(self):
        self.player.setPlaybackRate(self.playbackRate())

    def volume(self):
        self.player.setVolume(self.vslider.value())
        self.vlbl.setText(f"Volume: {self.vslider.value()}")

    def mute(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.muteBtn.setToolTip("Mute(Shortcut: Press M)")

        else:
            self.player.setMuted(True)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.muteBtn.setToolTip("Unmute(Shortcut: Press M)")

    def mediastate_changed(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.slider.setValue(position)
        mtime = QTime(0, 0, 0, 0)
        mtime = mtime.addMSecs(self.player.position())
        self.lbl.setText(mtime.toString())

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        mtime = QTime(0, 0, 0, 0)
        mtime = mtime.addMSecs(self.player.duration())
        self.elbl.setText(mtime.toString())

    def set_position(self, position):
        self.player.setPosition(position)

    def volumeUp(self):
        self.player.setVolume(self.player.volume() + 5)
        self.vslider.setValue(self.vslider.value() + 5)
        self.vlbl.setText(f"Volume: {self.vslider.value()}")

    def volumeDown(self):
        self.player.setVolume(self.player.volume() - 5)
        self.vslider.setValue(self.vslider.value() - 5)
        self.vlbl.setText(f"Volume: {self.vslider.value()}")

    def playNext(self):
        try:
            self.list.setCurrentRow(self.list.currentRow() + 1)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
            self.player.play()

        except Exception:
            self.list.setCurrentRow(0)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
            self.player.play()
        self.get_current_song()

    def playPrevious(self):
        try:
            self.list.setCurrentRow(self.list.currentRow() - 1)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
            self.player.play()

        except Exception:
            self.list.setCurrentRow(self.list.count() - 1)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3files[self.list.currentItem().text()])))
            self.player.play()
        self.get_current_song()

    def closeEvent(self, event):
        info = {"last_played": self.playing if self.playing else None,
                "total_time": self.player.duration(),
                "time_elapsed": self.slider.value(),
                "volume": self.vslider.value(),
                "last_playlist": self.tablebox.currentText(),
                "repeat": self.repeat_one,
                "once": self.once}
        json_obj = json.dumps(info, indent=4)
        with open(f'{HOME_PATH}/CMPdata.json', 'w') as file:
            file.write(json_obj)
        conn.close()
        self.showMinimized()
        os.startfile("database.exe")


class Popup(QDialog):
    def __init__(self, tablebox):
        super().__init__()
        self.setWindowTitle("Candy Music Player")
        self.setWindowIcon(QIcon("icons/mp3_player_icon1.ico"))
        self.listWidget = QListWidget()
        self.listWidget.setFont(QFont('Sitka Text', 11))
        self.listWidget.itemDoubleClicked.connect(self.add_to_playlist)

        self.newlbl = QLineEdit()
        self.newlbl.setUpdatesEnabled(True)
        self.newlbl.setPlaceholderText('New Playlist')
        self.newlbl.setFont(QFont('Sitka Text', 11))

        self.btn = QPushButton('Create')
        self.btn.setFont(QFont('Sitka Text', 11))
        self.btn.clicked.connect(self.create_new_playlist)

        self.add_btn = QPushButton('Add To Playlist')
        self.add_btn.setFont(QFont('Sitka Text', 11))
        self.add_btn.clicked.connect(self.add_to_playlist)

        self.tablebox = tablebox

        hbox = QHBoxLayout()
        hbox.addWidget(self.newlbl)
        hbox.addWidget(self.btn)
        layout = QVBoxLayout(self)
        layout.addLayout(hbox)
        layout.addWidget(self.listWidget)
        layout.addWidget(self.add_btn)
        self.get_tables()

    def get_tables(self):
        self.listWidget.clear()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for tables in c.fetchall():
            for table in tables:
                self.listWidget.addItem(table.title())

    def create_new_playlist(self):
        name = self.newlbl.text()
        c.execute(f"""CREATE TABLE IF NOT EXISTS {name.lower()}(
                    name text,
                    fullpath text)""")
        conn.commit()
        self.get_tables()
        self.tablebox.addItem(name.title())

    def add_to_playlist(self):
        c.execute(f"INSERT INTO {self.listWidget.currentItem().text()}(name, fullpath) VALUES(?, ?)",
                  (song_to_add_to_playlist[0], song_to_add_to_playlist[1]))
        conn.commit()
        song_to_add_to_playlist.clear()
        self.close()


if __name__ == '__main__':
    app = QApplication(argv)
    app.setStyleSheet('''
    QSlider::groove:horizontal {
    border: 1px solid #bbb;
    background: white;
    height: 10px;
    border-radius: 4px;
    }

    QSlider::sub-page:horizontal {
    background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
        stop: 0 #66e, stop: 1 #bbf);
    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
        stop: 0 #bbf, stop: 1 #55f);
    border: 1px solid #777;
    height: 10px;
    border-radius: 4px;
    }

    QSlider::add-page:horizontal {
    background: #fff;
    border: 1px solid #777;
    height: 10px;
    border-radius: 4px;
    }

    QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #eee, stop:1 #ccc);
    border: 1px solid #777;
    width: 13px;
    margin-top: -2px;
    margin-bottom: -2px;
    border-radius: 4px;
    }

    QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fff, stop:1 #ddd);
    border: 1px solid #444;
    border-radius: 4px;
    }

    QSlider::sub-page:horizontal:disabled {
    background: #bbb;
    border-color: #999;
    }

    QSlider::add-page:horizontal:disabled {
    background: #eee;
    border-color: #999;
    }

    QSlider::handle:horizontal:disabled {
    background: #eee;
    border: 1px solid #aaa;
    border-radius: 4px;
    }''')
    window = CandyMP3Player()
    window.show()
    exit(app.exec_())
