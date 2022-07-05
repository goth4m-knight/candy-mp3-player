import shutil
import threading
import os
import time
from os.path import join, basename
from PyQt5.QtWidgets import QApplication, \
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, \
    QStyle, QSlider, QShortcut, QLineEdit, QComboBox, QListWidget, QMessageBox, QTabWidget, QPlainTextEdit, QLabel, \
    QProgressBar, QFrame
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtCore import Qt, QUrl, QTime, QDir, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from sys import argv, exit
import lyricsgenius

genius = lyricsgenius.Genius('whatever-api-you-get-from-API Client management page-in-https://docs.genius.com/', skip_non_songs=True,
                             excluded_terms=["(Remix)", "(Live)"],
                             remove_section_headers=True)
CWD = os.getcwd()


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 350)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("icons/mp3_player_icon1.ico"))
        self.counter = 0
        self.n = 500
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        self.timer.start(30)

    def initUI(self):
        # layout to display splash scrren frame
        layout = QVBoxLayout()
        self.setLayout(layout)
        # splash screen frame
        self.frame = QFrame()
        self.frame.setObjectName('Frame')
        layout.addWidget(self.frame)
        # splash screen title
        self.title_label = QLabel(self.frame)
        self.title_label.setObjectName('title_label')
        self.title_label.resize(690, 120)
        self.title_label.move(0, 5)  # x, y
        self.title_label.setText('Candy MP3 Player')
        self.title_label.setAlignment(Qt.AlignCenter)
        # splash screen title description
        self.description_label = QLabel(self.frame)
        self.description_label.resize(690, 40)
        self.description_label.move(0, self.title_label.height())
        self.description_label.setObjectName('desc_label')
        self.description_label.setText('<b>Collecting Songs</b>')
        self.description_label.setAlignment(Qt.AlignCenter)
        # splash screen pogressbar
        self.progressBar = QProgressBar(self.frame)
        self.progressBar.resize(self.width() - 200 - 10, 50)
        self.progressBar.move(100, 180)  # self.description_label.y()+130
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.n)
        self.progressBar.setValue(20)
        # spash screen loading label
        self.loading_label = QLabel(self.frame)
        self.loading_label.resize(self.width() - 10, 50)
        self.loading_label.move(0, self.progressBar.y() + 70)
        self.loading_label.setObjectName('loading_label')
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setText('Loading...')

    def loading(self):
        # set progressbar value
        self.progressBar.setValue(self.counter)

        def collect():
            os.chdir(QDir.homePath())
            if not os.path.exists('CandyMusic'):
                pass
            else:
                shutil.rmtree('CandyMusic')
            os.mkdir('CandyMusic')
            os.chdir(QDir.homePath() + '/CandyMusic')
            for root, dirs, files in os.walk(QDir.homePath()):
                for file in files:
                    if file.endswith('.mp3'):
                        fullname = os.path.join(root, file).replace('\\', '/')
                        filename = os.path.splitext(os.path.basename(fullname))
                        for name in filename:
                            try:
                                f = open(f"{name}.txt", 'w')
                                for names in fullname:
                                    f.write(names)
                            except Exception:
                                pass

        if self.counter == int(self.n * 0):
            threading.Thread(target=collect).start()

        if self.counter >= self.n:
            self.timer.stop()
            self.close()
            time.sleep(1)
            os.chdir(CWD)
            self.WindowApp = CandyMP3Player()
            self.WindowApp.show()

        self.counter += 1


class CandyMP3Player(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 840, 930
        self.setGeometry(450, 50, self.window_width, self.window_height)
        self.setMaximumWidth(self.window_width)
        self.setMaximumHeight(self.window_height)
        self.setWindowTitle("Candy Music Player")
        self.setWindowIcon(QIcon("icons/mp3_player_icon1.ico"))
        self.create_player()
        self.repeat_one = False
        self.once = False

    def create_player(self):
        self.list = QListWidget()
        self.list.setFont(QFont('Sitka Text', 11))
        self.player = QMediaPlayer()
        self.list.itemClicked.connect(self.file)

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
        self.upBtn.setToolTip("Volume Up(Shortcut: Arrow Up Key)")
        self.upBtn.setFont(QFont('Sitka Text', 11))

        self.downBtn = QPushButton()
        self.downBtn.setIcon(QIcon('icons/volume down.png'))
        self.downBtn.clicked.connect(self.volumeDown)
        self.downBtn.setToolTip("Volume Down(Shortcut: Arrow Down Key)")
        self.downBtn.setFont(QFont('Sitka Text', 11))

        self.backwardBtn = QPushButton()
        self.backwardBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.backwardBtn.clicked.connect(self.playPrevious)
        self.backwardBtn.setToolTip("Previous(Shortcut: Arrow Down Key)")
        self.backwardBtn.setFont(QFont('Sitka Text', 11))

        self.forwardBtn = QPushButton()
        self.forwardBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.forwardBtn.clicked.connect(self.playNext)
        self.forwardBtn.setToolTip("Next(Shortcut: Arrow Down Key)")
        self.forwardBtn.setFont(QFont('Sitka Text', 11))

        self.slider = QSlider(Qt.Horizontal)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.vslider = QSlider(Qt.Horizontal)
        self.vslider = QSlider(Qt.Horizontal, self)
        self.vslider.setRange(0, 100)
        self.vslider.setValue(100)
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

        self.reloadBtn = QPushButton()
        self.reloadBtn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.reloadBtn.clicked.connect(self.reloadr)
        self.reloadBtn.setToolTip("Reload To Add New Songs")
        self.reloadBtn.setFont(QFont('Sitka Text', 11))

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

        self.slbl = QLineEdit('Search For Lyrics')
        self.slbl.setFont(QFont('Sitka Text', 11))
        self.slbl.setUpdatesEnabled(True)

        self.songlbl = QPlainTextEdit()
        self.songlbl.insertPlainText('')
        self.songlbl.setFont(QFont('Sitka Text', 11))
        self.songlbl.setReadOnly(True)
        self.songlbl.setUpdatesEnabled(True)

        self.sentry = QLineEdit()
        self.slbl.setFont(QFont('Sitka Text', 11))
        self.sentry.setUpdatesEnabled(True)

        self.searchBtn = QPushButton()
        self.searchBtn.setText('Search')
        self.searchBtn.clicked.connect(self.search)
        self.searchBtn.setFont(QFont('Sitka Text', 11))

        self.allBtn = QPushButton()
        self.allBtn.setText('All Songs')
        self.allBtn.clicked.connect(self.all_songs)
        self.allBtn.setFont(QFont('Sitka Text', 11))

        self.shortcut = QShortcut(QKeySequence(" "), self)
        self.shortcut.activated.connect(self.playAudioFile)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.playNext)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.playPrevious)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence("m"), self)
        self.shortcut.activated.connect(self.mute)

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
        sbox.addWidget(self.searchBtn)
        sbox.addWidget(self.allBtn)
        sbox.addWidget(self.reloadBtn)

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
        self.list.itemClicked.connect(self.get_lyrics)
        self.list.itemSelectionChanged.connect(self.nameChange)
        os.chdir(QDir.homePath() + '/CandyMusic')
        self.x = 0
        self.x += 1
        self.list.clear()
        for _file in os.listdir(os.getcwd()):
            if not _file == '.mp3.txt':
                self.list.insertItem(self.x, os.path.splitext(os.path.basename(_file))[0])
        self.list.sortItems(Qt.AscendingOrder)

    def get_songs(self):
        self.x = 0
        self.x += 1
        os.chdir(QDir.homePath())
        if not os.path.exists('CandyMusic'):
            pass
        else:
            shutil.rmtree('CandyMusic')
        os.mkdir('CandyMusic')
        os.chdir(QDir.homePath() + '/CandyMusic')
        for root, dirs, files in os.walk(QDir.homePath()):
            for file in files:
                if file.endswith('.mp3'):
                    fullname = join(root, file).replace('\\', '/')
                    filename = os.path.splitext(os.path.basename(fullname))
                    for name in filename:
                        try:
                            f = open(f"{name}.txt", 'w')
                            for names in fullname:
                                f.write(names)
                            os.chdir(QDir.homePath() + '/CandyMusic')
                            self.list.clear()
                            for _file in os.listdir(os.getcwd()):
                                if not _file == '.mp3.txt':
                                    self.list.insertItem(self.x, os.path.splitext(os.path.basename(_file))[0])
                            self.list.sortItems(Qt.AscendingOrder)
                        except Exception:
                            pass

    def nameChange(self):
        try:
            if '(' in self.list.currentItem().text():
                self.slbl.setText(f'{self.list.currentItem().text().split("(")[0]}')

            else:
                self.slbl.setText(f'{self.list.currentItem().text().split("[")[0]}')
        except Exception:
            pass

    def getLyrics(self):
        def lyrics():
            self.songlbl.clear()
            name = self.slbl.text()
            song = genius.search_song(name)
            self.songlbl.insertPlainText(f"{song.lyrics}\n")
            self.songlbl.verticalScrollBar().setValue(
                self.songlbl.verticalScrollBar().minimum())

        def play():
            self.player.play()

        try:
            threading.Thread(target=play()).start()
            threading.Thread(target=lyrics()).start()

        except Exception:
            self.songlbl.clear()
            self.songlbl.insertPlainText(f"No Lyrics Found.\nPlease Check Your Internet Connection.\nYou can Type In "
                                         f"The Song Name In Search Box.")
            self.player.play()

    def get_lyrics(self):
        def lyrics():
            name = self.list.currentItem().text()
            if '(' in name:
                self.songlbl.clear()
                song = genius.search_song(name.split('(')[0])
                self.songlbl.insertPlainText(f"{song.lyrics}\n")
                self.slbl.setText(f"{name.split('(')[0]}")
                self.songlbl.verticalScrollBar().setValue(
                    self.songlbl.verticalScrollBar().minimum())

            else:
                self.songlbl.clear()
                song = genius.search_song(name.split('[')[0])
                self.songlbl.insertPlainText(f"{song.lyrics}\n")
                self.slbl.setText(f"{name.split('.')[0]}")
                self.songlbl.verticalScrollBar().setValue(
                    self.songlbl.verticalScrollBar().minimum())

        def play():
            self.player.play()

        try:
            threading.Thread(target=play()).start()
            threading.Thread(target=lyrics()).start()

        except Exception:
            name = self.list.currentItem().text()
            song = name.split('(')[0]
            self.slbl.setText(f"{song}")
            self.songlbl.clear()
            self.songlbl.insertPlainText(f"No Lyrics Found.\nPlease Check Your Internet Connection.\nYou can Type In "
                                         f"The Song Name In Search Box.")
            self.player.play()

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

            elif not self.repeat_one and self.once:
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
                    f = open(f"{self.list.currentItem().text()}.txt", 'r')
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
                    self.player.play()

                except Exception:
                    self.list.setCurrentRow(0)
                    f = open(f"{self.list.currentItem().text()}.txt", 'r')
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
                    self.player.play()

        if self.repeat_one and not self.once:
            try:
                if status == QMediaPlayer.EndOfMedia:
                    f = open(f"{self.list.currentItem().text()}.txt", 'r')
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
                    self.player.play()
            except Exception:
                self.list.setCurrentRow(0)
                f = open(f"{self.list.currentItem().text()}.txt", 'r')
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
                self.player.play()

    def all_songs(self):
        self.sentry.setText('')
        self.list.clear()
        for files in os.listdir(os.getcwd()):
            if not files == '.mp3.txt':
                self.list.insertItem(self.x, os.path.splitext(os.path.basename(files))[0])
        self.list.sortItems(Qt.AscendingOrder)

    def search(self):
        songlist = []
        songlist.clear()
        self.list.clear()
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                known_song = join(root, file)
                db = known_song.replace(' ', '').replace('-', '').lower()
                search_song = self.sentry.text().replace(' ', '').replace('-', '').lower()
                if search_song in db:
                    songlist.append(known_song)

        if len(songlist) == 0:
            QMessageBox.about(self, 'Error', f'No File Named {self.sentry.text()} Found')

        for song in songlist:
            self.list.insertItem(self.x, os.path.splitext(basename(song))[0])
        self.list.sortItems(Qt.AscendingOrder)

    def reloadr(self):
        os.chdir(QDir.homePath())
        os.system('rmdir /s /q CandyMusic')
        self.get_songs()

    def file(self):
        f = open(f"{self.list.currentItem().text()}.txt", 'r')
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))

    def playAudioFile(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playBtn.setToolTip("Play")

        else:
            self.player.play()
            self.playBtn.setToolTip("Pause")

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
            f = open(f"{self.list.currentItem().text()}.txt", 'r')
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
            self.player.play()
        except Exception:
            self.list.setCurrentRow(0)
            f = open(f"{self.list.currentItem().text()}.txt", 'r')
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
            self.player.play()

    def playPrevious(self):
        try:
            self.list.setCurrentRow(self.list.currentRow() - 1)
            f = open(f"{self.list.currentItem().text()}.txt", 'r')
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
            self.player.play()

        except Exception:
            self.list.setCurrentRow(self.list.currentRow() + 1)
            f = open(f"{self.list.currentItem().text()}.txt", 'r')
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f.read())))
            self.player.play()

    def closeEvent(self, event):
        close = QMessageBox.question(self, "QUIT", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            os.chdir(QDir.homePath())
            shutil.rmtree('CandyMusic')
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(argv)
    app.setStyleSheet('''
        #title_label {
            font-size: 50px;
            color: #ffffff;
        }
        #desc_label {
            font-size: 20px;
            color: #c2ced1;
        }
        #loading_label {
            font-size: 30px;
            color: #e8e8eb;
        }

        #Frame {
            background-color: #2F4454;
            color: rgb(220, 220, 220);
        }

        QProgressBar {
            background-color: #000000;
            color: #c8c8c8;
            border-style: none;
            border-radius: 5px;
            text-align: center;
            font-size: 25px;
        }
        QProgressBar::chunk {
            border-radius: 5px;
            background-color: qlineargradient(spread:pad x1:0, x2:1, y1:0.511364, y2:0.523, stop:0 #33b846);
        }
    ''')
    splash = SplashScreen()
    splash.show()
    exit(app.exec_())
