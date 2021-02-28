from PyQt5 import QtWidgets, uic, QtGui, QtMultimedia, QtCore
# from PyQt5.QtWidgets import *
import datetime
import mutagen
import os
import sys 


def path_dilation(path):
    return os.path.join(os.path.dirname(__file__), path)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        self.playlist = [] 
        self.playlist_path = None
        self.current_index = None

        uic.loadUi(path_dilation("ui/max.ui"), self)

        self.treeWidget.setColumnWidth(0, 43)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(None)
        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_handler)
        self.mediaPlayer.positionChanged.connect(self.position_changed_handler)
        self.mediaPlayer.durationChanged.connect(self.duration_changed_handler)
        self.positionSlider.sliderMoved.connect(self.slider_moved_handler)
        # self.mediaPlayer.positionChanged.

        self.playPauseButton.clicked.connect(self.playPauseHandler)
        self.nextButton.clicked.connect(self.next)
        self.previousButton.clicked.connect(self.previous)

        # self.progessBar.timeout.connect()
        
        self.actionOpen_File.triggered.connect(self.Open_File)
        self.actionSave.triggered.connect(self.Save)
        self.actionSave_As.triggered.connect(self.Save_As)
        self.actionExit.triggered.connect(self.Exit)

        self.treeWidget.itemDoubleClicked['QTreeWidgetItem*','int'].connect(self.tree_item_double_click)
        #Where tree item click is a self defined slot function

    def Open_File(self):
        print("open file")
        dialog = QtWidgets.QFileDialog()
        paths, _ = dialog.getOpenFileNames(self, 'Open File', os.getenv('MUSIC_PATH'), 'Sound Files (*.mp3 *.ogg *.wav *.m4a *.aac)')
        for path in paths:
            if path != '':
                print("File path: " + path)
                self.add_to_plalist(path)
    
    def add_to_plalist(self, path):
        metadata = self.metadata(path) # gets song from path and gets metadata
        content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
        track = {
            **metadata,
            "path": path,
            "media": content,
            "item": QtWidgets.QTreeWidgetItem(self.treeWidget),
            "statuslabel": QtWidgets.QLabel()
        }

        # this inputs the required slots in place on the tree widget
        track["statuslabel"].setAlignment(QtCore.Qt.AlignCenter)
        self.treeWidget.setItemWidget(track["item"], 0, track["statuslabel"])

        track["item"].setText(1, track["trackn"].split("/")[0])
        track["item"].setText(2, track["title"])
        track["item"].setText(3, track["album"])
        track["item"].setText(4, track["artist"])
        track["item"].setText(5, self.humanify_seconds(track["duration"]))
        try:
            track["item"].setText(6, str(datetime.date.fromisoformat(track["date"]).year))
        except:
            pass

        self.playlist.append(track)  # adds more tracks to the playlist

        # gets data from mtigen and prints all on consol
        # Audio = mutagen.File(content)
        # Audio.pprint() gets all data from mutagen and prints on consol
        # print ("data of selected musuc")
            
    def saveHandler(self, path):
        if path != '':
            file, ext = os.path.splitext(path)
            path = file + (ext or ".m3u")
            print("path : " + path)
            with open(path,'w') as f:
                for track in self.playlist:
                    # f.write("# " + track["title"] + "\n")
                    f.write(track["path"] + "\n")
            self.playlist_path = path



    def Save(self):
        print("save")
        # impliments save as and also saves the changes to the files
        if self.playlist_path:
            self.saveHandler(self.playlist_path)
        else:
            self.Save_As()


    def Save_As(self):
        print("save as")
        # saves the files in list view so i can import list whenever i want
        dialog = QtWidgets.QFileDialog()
        path, _ = dialog.getSaveFileName(self, "Save file", "", "Playlist File(*.m3u)")
        self.saveHandler(path)
    
    def Exit (self):
        print("Exit")
        self.close()

    def playPauseHandler(self):
        # print("play/pause")
        if self.current_index != None:
            if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
                self.playPauseButton.setText("Play")
                self.playingStatus.setText("Paused")
                # playPauseButton.setText("Pause")
                icon = QtGui.QIcon.fromTheme("media-playback-pause")
                self.playlist[self.current_index]["statuslabel"].setPixmap(
                    icon.pixmap(icon.actualSize(QtCore.QSize(16, 16))))
                print("pause")
            else:
                self.mediaPlayer.play()
                self.playPauseButton.setText("Pause")
                self.playingStatus.setText("Now Playing")
                # playPauseButton.setText("Play")
                icon = QtGui.QIcon.fromTheme("media-playback-start")
                self.playlist[self.current_index]["statuslabel"].setPixmap(
                    icon.pixmap(icon.actualSize(QtCore.QSize(16, 16))))
                print("play")

    def media_status_handler(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            print("song has finished playing")
            self.next()

    def indicate_now_playing(self, track, brush=None):
        if brush:
            icon = QtGui.QIcon.fromTheme("media-playback-start")
            track["statuslabel"].setPixmap(icon.pixmap(icon.actualSize(QtCore.QSize(16, 16))))
        else:
            track["statuslabel"].clear()
        for index in range(7):
            if not brush:
                track["item"].setData(index, QtCore.Qt.BackgroundRole, None)
            else:
                track["item"].setBackground(index, brush)

    def next(self):
        if self.current_index != None and len(self.playlist) > 0:
            self.indicate_now_playing(self.playlist[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.playlist)
            track = self.playlist[self.current_index]
            self.indicate_now_playing(track, QtGui.QBrush(QtGui.QColor("#168479")))
            content = track["media"]
            self.mediaPlayer.setMedia(content)
            self.nameStatus.setText(track["title"])
            self.albumStatus.setText(track["album"])
            self.artistStatus.setText(track["artist"])
            self.mediaPlayer.play()

    def previous(self):
        if self.current_index != None and len(self.playlist) > 0:
            self.indicate_now_playing(self.playlist[self.current_index])
            self.current_index = (self.current_index +
                                  len(self.playlist) - 1) % len(self.playlist)
            track = self.playlist[self.current_index]
            self.indicate_now_playing(track, QtGui.QBrush(QtGui.QColor("#168479")))
            content = track["media"]
            self.mediaPlayer.setMedia(content)
            self.nameStatus.setText(track["title"])
            self.albumStatus.setText(track["album"])
            self.artistStatus.setText(track["artist"])
            self.mediaPlayer.play()

    def tree_item_double_click(self, item):
        print("tree item clicked")
        if self.current_index != None:
            self.indicate_now_playing(self.playlist[self.current_index])
        # gets current row in playlist
        self.current_index = self.treeWidget.indexFromItem(item).row()
        print(self.current_index) # prints current index
        track = self.playlist[self.current_index] #links current 
        self.indicate_now_playing(track, QtGui.QBrush(QtGui.QColor("#168479")))
        content = track["media"]
        self.mediaPlayer.setMedia(content)

        self.playPauseButton.click()

        # self.mediaPlayer.play()
        self.nameStatus.setText(track["title"])
        self.albumStatus.setText(track["album"])
        self.artistStatus.setText(track["artist"])

    def humanify_seconds(self, seconds):
        parts = []
        for (index, part) in enumerate(reversed(self.convert(seconds))):
            part = int(part)
            if index < 2 or part > 0:
                parts.append(f"{part:02}")

        return ":".join(reversed(parts))
    
    def position_changed_handler(self, position):
        print("position_changed_handler:", position)
        seconds = position / 1000
        self.positionTimer.setText(self.humanify_seconds(seconds))
        try:
            self.positionSlider.setValue(int(position / self.mediaPlayer.duration() * 100))
        except:
            pass

    def duration_changed_handler(self, duration):
        self.fixedTimer.setText(self.humanify_seconds(self.mediaPlayer.duration() / 1000))

    def slider_moved_handler(self, value):
        self.mediaPlayer.setPosition((value / 100) * self.mediaPlayer.duration())

    def statusView(self, state):
        if self.mediaPlaer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.playPauseButton.setText(str("Play"))
            self.playingStatus.setText("Now Playing:")
        else:
            self.playPauseButton.setText(str("Pause"))
            self.playingStatus.setText("Paused:")
        
    def convert(self, seconds):
        hours = seconds // 3600
        seconds %= 3600
        mins = seconds // 60
        seconds %= 60
        return hours, mins, seconds
    
    def metadata(self, path):
        audio = mutagen.File(path, easy=True)
        audio.get('duration')

        print(int(audio.info.length))
        return {
            "trackn": audio.get("tracknumber", ["<no data>"])[0],
            "title": audio.get("title", ["<no data>"])[0],
            "album": audio.get("album", ["<no data>"])[0],
            "artist": audio.get("artist", ["<no data>"])[0],
            "date": audio.get("date", ["<no data>"])[0],
            "duration": int(audio.info.length)
        }

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui()
    main_window.show()
    app.exec_()