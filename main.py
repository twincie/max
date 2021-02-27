from PyQt5 import QtWidgets, uic, QtGui, QtMultimedia, QtCore
# from PyQt5.QtWidgets import *
import mutagen
import os
import sys 


def path_dilation(path):
    return os.path.join(os.path.dirname(__file__), path)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        self.playlist = [] 
        self.current_index = -1

        uic.loadUi(path_dilation("ui/max.ui"), self)
        
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

        self.treeWidget.itemClicked['QTreeWidgetItem*','int'].connect(self.tree_item_click)
        #Where tree item click is a self defined slot function

    def Open_File(self):
        print("open file")
        dialog = QtWidgets.QFileDialog()
        path, _ = dialog.getOpenFileName(self, 'Open File', os.getenv('MUSIC_PATH'), 'Sound Files (*.mp3 *.ogg *.wav *.m4a *.aac)')
        if path != '':
            print("File path: " + path)
            self.add_to_plalist(path)
    
    def add_to_plalist(self, path):
        metadata = self.metadata(path) # gets song from path and gets metadata
        content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
        track = {
            "title": metadata["title"],
            "album": metadata["album"],
            "artist": metadata["artist"],
            "media": content,
            "duration": metadata["duration"]
        }
        # this inputs the required slots in place on the tree widget
        item = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item.setText(0, f"{len(self.playlist) + 1:02}")
        item.setText(1, track["title"])
        item.setText(2, track["album"])
        item.setText(3, track["artist"])

        self.playlist.append(track) # adds more tracks to the playlist
            
        # gets data from mtigen and prints all on consol
        # Audio = mutagen.File(content)
        # Audio.pprint() gets all data from mutagen and prints on consol
        # print ("data of selected musuc")
            

    def Save(self):
        print("save")


    def Save_As(self):
        print("save as")
    
    def Exit (self):
        print("Exit")
        self.close()

    def playPauseHandler(self):
        # print("play/pause")
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playPauseButton.setText("Play")
            self.playingStatus.setText("Paused")
            # playPauseButton.setText("Pause")
            print("pause")
        else:
            self.mediaPlayer.play()
            self.playPauseButton.setText("Pause")
            self.playingStatus.setText("Now Playing")
            # playPauseButton.setText("Play")
            print("play")
            
        
        
    
    def media_status_handler(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            print("song has finished playing")
            self.next()
    
    def next(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        track = self.playlist[self.current_index]
        content = track["media"]
        self.mediaPlayer.setMedia(content)
        self.nameStatus.setText(track["title"])
        self.albumStatus.setText(track["album"])
        self.artistStatus.setText(track["artist"])
        self.mediaPlayer.play()


    def previous(self):
        self.current_index -= 1
        track = self.playlist[self.current_index]
        content = track["media"]
        self.mediaPlayer.setMedia(content)
        self.nameStatus.setText(track["title"])
        self.albumStatus.setText(track["album"])
        self.artistStatus.setText(track["artist"])
        self.mediaPlayer.play()

    def tree_item_click(self, item):
        print("tree item clicked")
        # gets current row in playlist
        self.current_index = self.treeWidget.indexFromItem(item).row()
        print(self.current_index) # prints current index
        track = self.playlist[self.current_index] #links current 
        content = track["media"]
        self.mediaPlayer.setMedia(content)

        self.playPauseButton.click()

        # self.mediaPlayer.play()
        self.nameStatus.setText(track["title"])
        self.albumStatus.setText(track["album"])
        self.artistStatus.setText(track["artist"])

        # if self.mediaPlayer.isFinished():
        #     print("song has finished playing")
        # self.next()

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


    # def current_playlist_position(self, item):
    #     print ("current index song is on")
    #     index = self.treeWidget.indexFromItem(item).row()
    #     print (index)
    #     print("current index : "+ index)
        
        
        # self.playlist.indexFromItem(index)
        # if i > -1:
        #     ix = index
        #     self.playlist.setCurrentIndex(ix)
        #     print("current index : " + ix)


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
            "title": audio.get("title", ["<no data>"])[0],
            "album": audio.get("album", ["<no data>"])[0],
            "artist": audio.get("artist", ["<no data>"])[0],
            "duration": self.convert(int(audio.info.length))
        }

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui()
    main_window.show()
    app.exec_()