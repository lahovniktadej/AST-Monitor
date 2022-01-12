from ast_monitor.mainwindow import Ui_MainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QProcess
import os
from datetime import datetime
import geopy.distance
from ast_monitor.classes import SensorData, Intervals
from pyqt_feedback_flow.feedback import Feedback

TICK_TIME = 2**6
        
class AST(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self, hr_data_path, gps_data_path):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.hr_data_path = hr_data_path
        self.gps_data_path = gps_data_path

        self.time_series = [] #storing all the data in this struct
        
        self.hr_data_collection = []
        
        #SHOW REAL TIME HR
        self.timer = QTimer()
        self.timer.timeout.connect(self.real_time_hr)
        self.timer.start(1000)
    
        #taking values from the sensors
        #self.build_time_series()
        
        #shutdown
        self.shutdown.clicked.connect(self.shutdown_now)
        
        #on clicked buttons
        self.tracker = QTimer()
        self.tracker.setInterval(TICK_TIME)
        self.tracker.timeout.connect(self.tick)
        self.do_reset()
        
        # menu buttons
        self.actionAbout_program.triggered.connect(self.about)
        self.actionLicense.triggered.connect(self.license)
        self.actionDisclaimer.triggered.connect(self.disclaimer)

        self.tracking_flag = False
        self.start_tracking.clicked.connect(self.startTracking)
        
        self.stop_tracking.clicked.connect(self.endTracker)
        
    def startTracking(self):
        # counter start
        self.startTracker()
        self.tracking_flag = True

        # show simple notification that workout just started
        self._feedback = Feedback(text="Workout started!")
        self._feedback.show()

    def startTracker(self):
        self.tracker.start()
        
    def endTracker(self):
        self.tracker.stop()
        self.tracking_flag = False

    def tick(self):
        self.track_time += TICK_TIME/1000
        self.display_stopwatch()

    def display_stopwatch(self):
        self.watch.display("%d:%05.2f" % (self.track_time // 60, self.track_time % 60))

    def update_distance(self):
        dist = self.calculate_distance()
        self.total_distance.setText(str(dist))

    def update_ascent(self):
        pass
    
    def update_average_hr(self):
        avhr = str(self.calculate_avhr())
        self.average_hr.setText(avhr)
    
    def update_interval_hr(self):
        pass
    
    @pyqtSlot()
    def do_reset(self):
        self.track_time = 0
        self.display_stopwatch()
        
    def showtrackingTime(self):
        time=QDateTime.currentDateTime()
        timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.label.setText(timeDisplay)

    def shutdown_now(self):
        os.system("shutdown now -h")
        
    def startTimer(self):
        self.timer.start(1000)
    
    def endTimer(self):
        self.timer.stop()
    
    def get_current_time(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return current_time
    
    #collect, GPS data, HR data and current time
    def build_time_series(self):
        HR = self.return_curr_hr()
        GPS_LON, GPS_LAT, GPS_ALT = self.return_curr_gps()
        TIME = self.get_current_time
        self.time_series.append(SensorData(HR, GPS_LON, GPS_LAT, GPS_ALT, TIME))

    @pyqtSlot()
    def real_time_hr(self):
        with open(self.hr_data_path, "r") as ins:
            array = []
            for line in ins:
                array.append(line)
            final = str(array[-1].rstrip())
        self.current_hr.setText(final)
        
        #build_time_series in case tracker is enabled
        if self.tracking_flag == True:
            self.build_time_series()
            self.update_distance()
            #self.update_average_hr()
        
        return int(final)
    
    def return_curr_hr(self):
        with open(self.hr_data_path, "r") as ins:
            array = []
            for line in ins:
                array.append(line)
            final = str(array[-1].rstrip())
            
        return int(final)
    
    def return_curr_gps(self):
        with open(self.gps_data_path, "r") as ins:
            array = []
            for line in ins:
                array.append(line)
            final1 = str(array[-1].rstrip())
            
            final = final1.split(";")
        return float(final[0]), float(final[1]), float(final[2])

    def calculate_avhr(self):
        # TODO
        avg_hr = 0
        return 150
        
    def calculate_distance(self):
        total_distance = 0.0
        if (len(self.time_series) < 5):
            pass
        else:
            for i in range(len(self.time_series)-1):
                coords_1 = (self.time_series[i+1].lon, self.time_series[i+1].lat)
                coords_2 = (self.time_series[i].lon, self.time_series[i].lat)
                total_distance = total_distance + abs(geopy.distance.geodesic(coords_1, coords_2).m)

            return round((total_distance / 1000), 3)

    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Developed by I. Fister Jr., 2021")
        msg.setWindowTitle("About this application")
        #msg.setDetailedText("The details are as follows:")
        retval = msg.exec_()

    def license(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Licensed under MIT license!")
        msg.setWindowTitle("License info!")
        retval = msg.exec_()

    def disclaimer(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        #msg.setText("Developed by I. Fister Jr., 2021")
        msg.setWindowTitle("Disclaimer")
        msg.setDetailedText("This framework is provided as-is, and there are no guarantees that it fits your purposes or that it is bug-free. Use it at your own risk!")
        retval = msg.exec_()