import serial
import time
import sys
from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from PyQt4 import QtGui
from practice_gui import Ui_MainWindow

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.com_port_setup()
        # self.ui.checkBox_voltageMonitor.setChecked(0)
        self.connect_buttons()
        self.gui_setup()
        # self.manual_ser_select()

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def com_port_setup(self):
        print("Please wait for Python to determine which port the Arduino is connected to.")
        ser_port_list = self.serial_ports()

        print("List of possible ports: " + str(ser_port_list))

        for k in range(0, len(ser_port_list)):
            self.ser = serial.Serial(ser_port_list[k], 115200, timeout=0, writeTimeout=0)
            print("Testing serial port "+ str(ser_port_list[k]) + " for Arduino")
            time.sleep(2)
            self.ser.write("#")
            time.sleep(1)
            con_val = self.ser.readline()
            # print([type(con_val), con_val] )
            # print(ser_port_list[k])

            if "@" in con_val:
                print("This is the com port: " + str(ser_port_list[k]))
                self.ui.pB_Fire.setEnabled(True)
                break
            else:
                print("It's not port " + str(ser_port_list[k]))
                self.ser.close()

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]

        result = []
        for port in ports:
            try:
                print("Testing port: " + str(port))
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                print("Invalid port")
                pass
        return result

    def gui_setup(self):
        self.setWindowTitle("Railgun")
        self.setWindowIcon(QtGui.QIcon("lightninglogo.ico"))
        # sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.ui.sBox_chargeMonitor.setEnabled(True)
        # self.ui.pB_stopCharge1.setEnabled(False)
        self.ui.cB_autoFire.setEnabled(False)
        self.ui.pB_stopChargeInjector.setEnabled(False)
        self.ui.cB_bank1Charge.setChecked(False)
        self.ui.cB_injector.setChecked(True)
        self.ui.sBox_setChargeValue.setValue(300)
        self.ui.cB_fire.setEnabled(False)
        self.ui.pB_alert.setIcon(QtGui.QIcon('white_button.png'))
        self.ui.pB_alert.setIconSize(QtCore.QSize(230, 230))
#Initializes the menu bar with several functions
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        # port_menu = menubar.addMenu('&Manual Port Selection')
        start_vehicle=QtGui.QAction('&Turn on Vehicle', self)
        stop_vehicle=QtGui.QAction('&Turn off Vehicle', self)
        start_chargeRelay=QtGui.QAction('&Turn on Charging Relay', self)
        stop_chargeRelay=QtGui.QAction('&Turn off Charging Relay', self)
        start_chargeRelay.triggered.connect(self.start_charge_relay)
        stop_chargeRelay.triggered.connect(self.stop_charge_relay)
        start_vehicle.triggered.connect(self.start_vehicle_function)
        stop_vehicle.triggered.connect(self.stop_vehicle_function)
        connect_arduino_action=QtGui.QAction(QtGui.QIcon('Arduino.png'), '&Connect Arduino', self)
        connect_arduino_action.setStatusTip('Connect Arduino using Serial')
        connect_arduino_action.triggered.connect(self.com_port_setup)
        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)
        self.statusBar()
        file_menu.addAction(start_chargeRelay)
        file_menu.addAction(stop_chargeRelay)
        file_menu.addAction(start_vehicle)
        file_menu.addAction(stop_vehicle)
        file_menu.addAction(connect_arduino_action)
        file_menu.addAction(exit_action)

#Starts the emergy voltage monitor to ensure that the voltage of the caps never exceeds the given amount
        self.emergencyCapMonitorThread = emergencyVoltageMonitor(self.ui, self)
        self.emergencyCapMonitorThread.start()


        ##Uncomment past this poinnnnt
        self.arduino_send_communication = arduinoCommunicationSendThread(self.ui, self.ser ,self)
        self.arduino_send_communication.start()

        self.emerg_shutdown = False
        self.vehicle_on = False
        self.charge_relay1 = False
        self.connect_bank_2 = False

    def start_charge_relay(self):
        self.charge_relay1=False

    def stop_charge_relay(self):
        self.charge_relay1=False

    def start_vehicle_function(self):
        self.vehicle_on=True

    def stop_vehicle_function(self):
        self.vehicle_on=False

    def manual_ser_select(self):
        print("Manually Connecting to COM12")
        self.ser = serial.Serial("COM12", 115200, timeout=0, writeTimeout=0)

    def connect_buttons(self):
        self.ui.PB_LightOn.clicked.connect(self.test_func1)
        self.ui.vSlider_Red.sliderMoved.connect(self.slider_red)
        self.ui.vSlider_Green.sliderMoved.connect(self.slider_green)
        self.ui.vSlider_Blue.sliderMoved.connect(self.slider_blue)
        self.ui.cB_voltageMonitor.clicked.connect(self.capacitor_voltage_monitor_start)
        self.ui.pB_Fire.clicked.connect(self.fire1_function)
        # self.ui.pB_charge1.clicked.connect(self.charge1_function)
        # self.ui.pB_stopCharge1.clicked.connect(self.chargeStop1_function)
        self.ui.pB_stopChargeInjector.clicked.connect(self.chargeStopInjector_function)
        self.ui.pB_chargeInjector.clicked.connect(self.chargeInjector_function)
        # self.ui.cB_injector.stateChanged.connect(self.injectorButtons)
        self.ui.cB_bank2Charge.stateChanged.connect(self.bank2buttons)
        self.ui.cB_autoCharge.stateChanged.connect(self.autoCharge)
        self.ui.cB_oneShot.stateChanged.connect(self.oneShot)
        self.ui.pB_test.clicked.connect(self.test_function)
        self.ui.cB_bank1Charge.stateChanged.connect(self.connect_bank2_fun)
        self.ui.cB_laser.stateChanged.connect(self.laser_toggle)

    def laser_toggle(self):
        is_checked = self.ui.cB_laser.isChecked()
        print("Laser is toggled to: " + str(is_checked))

    def connect_bank2_fun(self):
        is_checked = self.ui.cB_bank1Charge.isChecked()
        print("Bank 1 is connected: " + str(is_checked))
        if is_checked==True:
            voltage_val=abs(self.ui.sBox_chargeMonitor.value() - self.ui.sBox_chargeMonitor_2.value())
            if voltage_val<50:
                print("Connecting Capacitor Bank 2")
                self.connect_bank_2 = True
                # self.ui.pB_charge1.setEnabled(True)
            else:
                self.ui.cB_autoCharge.setChecked(False)
                self.ui.cB_bank1Charge.setChecked(False)
                print("Voltage too high to connect capacitor bank 2")
                msg = QtGui.QMessageBox(self)
                msg.setIconPixmap(QtGui.QPixmap("dialog_warning.ico"))
                msg.setText("Voltage in primary capacitor bank is too high to connect secondary bank. Discharge bank "
                            "before connecting.")
                msg.setWindowTitle("WARNING")
                msg.exec_()

        elif is_checked==False:
            print("Disconnecting Capacitor Bank 2")
            self.connect_bank_2 = False
            # self.ui.pB_charge1.setEnabled(False)


    def test_function(self):
        QtGui.QMessageBox.about(self, "My message box", "SUCKMYASS -TEST")
    #     if self.connect_bank_2 == True:
    #         self.connect_bank_2 = False
    #     elif self.connect_bank_2 == False:
    #         self.connect_bank_2 = True
    #     print(self.connect_bank_2)

    def autoCharge(self):
        is_checked=self.ui.cB_autoCharge.isChecked()
        print("AutoCharge set to: " + str(is_checked))
        if is_checked==True:
            print("Starting AutoCharging")
            # autoChargeThread_start = autoChargeThread(self.ui, self.ser)
            self.ui.cB_oneShot.setEnabled(False)
            self.ui.cB_autoFire.setEnabled(True)
            self.autoChargeThread_start = autoChargeThread(self.ui)
            self.autoChargeThread_start.start()
        else:
            print("Ending AutoCharging")
            self.autoChargeThread_start.terminate()
            self.ui.cB_bank2Charge.setEnabled(True)
            self.ui.cB_bank1Charge.setEnabled(True)
            # self.ui.cB_injector.setEnabled(True)
            # self.ui.pB_charge1.setEnabled(True)
            self.ui.pB_chargeInjector.setEnabled(True)
            # self.ui.pB_stopCharge1.setEnabled(True)
            self.ui.pB_stopChargeInjector.setEnabled(True)
            self.ui.cB_injectorChargingIndicator.setChecked(False)
            # self.ui.cB_bank1chargingIndicator.setChecked(False)
            self.ui.cB_oneShot.setEnabled(True)

    def oneShot(self):
        is_checked = self.ui.cB_oneShot.isChecked()
        print("OneShot set to: " + str(is_checked))
        if is_checked==True:
            print("yeaa")
        else:
            print("aweeeee")

    # def injectorButtons(self):
    #     is_checked=self.ui.cB_injector.isChecked()
    #     print("Injector checkbox is: " +str(is_checked))
    #     self.ui.pB_chargeInjector.setEnabled(is_checked)
    #     self.ser.write("9")

    def bank2buttons(self):
        is_checked=self.ui.cB_bank2Charge.isChecked()
        print("Bank 2 checkbox is: " + str(is_checked))
    #     self.ser.write("7")

    def chargeInjector_function(self):
        # self.ser.write("=")
        print("Charging Injector Bank")
        self.ui.cB_injectorChargingIndicator.setChecked(True)
        self.ui.pB_chargeInjector.setEnabled(False)
        self.ui.pB_stopChargeInjector.setEnabled(True)
        # self.ui.cB_injector.setEnabled(False)

    def chargeStopInjector_function(self):
        # self.ser.write("=")
        print("Stopped charging injector bank")
        self.ui.cB_injectorChargingIndicator.setChecked(False)
        self.ui.pB_chargeInjector.setEnabled(True)
        self.ui.pB_stopChargeInjector.setEnabled(False)
        # self.ui.cB_injector.setEnabled(True)

    def chargeStop1_function(self):
        # self.ser.write("!0")
        print("Stopped charging Bank 1")
        # self.ui.cB_bank1chargingIndicator.setChecked(False)
        # self.ui.pB_charge1.setEnabled(True)
        # self.ui.pB_stopCharge1.setEnabled(False)
        self.ui.cB_bank1Charge.setEnabled(True)

    # def charge1_function(self):
    #     # self.ser.write("!1")
    #     print("Charging Bank 1")
    #     self.ui.cB_bank1chargingIndicator.setChecked(True)
    #     # self.ui.pB_charge1.setEnabled(False)
    #     self.ui.pB_stopCharge1.setEnabled(True)
    #     self.ui.cB_bank1Charge.setEnabled(False)

    def fire1_function(self):
        self.ui.pB_Fire.setEnabled(False)
        self.projectFire_thread = projectFire_thread(self.ui)
        self.projectFire_thread.start()

    def capacitor_voltage_monitor_start(self):
        self.VoltageMonitorThread = VoltageMonitorThread(self.ui,self.ser,self)
        self.VoltageMonitorThread.start()
        is_checked=self.ui.cB_voltageMonitor.isChecked()
        print("Voltage monitor is set to: " + str(is_checked))

    def slider_red(self):
        red_value = self.ui.vSlider_Red.value()
        red_value=red_value*2.55
        self.ser.write("$"+str(red_value))

    def slider_green(self):
        green_value = self.ui.vSlider_Green.value()
        green_value = green_value*2.55
        self.ser.write("#"+str(green_value))

    def slider_blue(self):
        blue_value = self.ui.vSlider_Blue.value()
        self.ser.write("*"+str(int(blue_value)*2.55))

    def test_func1(self):
        self.ser.write("@")

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.ui.textEdit_cmd.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.textEdit_cmd.setTextCursor(cursor)
        self.ui.textEdit_cmd.ensureCursorVisible()

class arduinoCommunicationReceiveThread(QThread):
    def __init__(self, ui):
        QThread.__init__(self)
        self.ui=ui
        # self.ser=serial
    def __del__(self):
        self.wait()
    def run(self):
        self.ui.cB_fire.setChecked(True)
        print("Fire")
        time.sleep(1)
        # self.ser.write("&")
        self.ui.cB_fire.setChecked(False)
        self.ui.pB_Fire.setEnabled(True)

class arduinoCommunicationSendThread(QThread):
    def __init__(self, ui, serial, self_other):
        QThread.__init__(self)
        self.ui = ui
        self.other=self_other
        self.ser=serial
    def __del__(self):
        self.wait()
    def run(self):
        x=0
        loop_ctr = 0
        current_ind_list, repeat_ind_list, numbers_ind_list = self.gui_checker()
        previous_ind_list = current_ind_list
        previous_numbers_ind_list = numbers_ind_list
        current_ind_str_list = ['bank2_ind', 'discharge_ind', 'fire_ind', 'inj_charge_ind',
                                'bank1_ind', 'emerg_stop', 'vehicle_on', 'charge_relay1', 'connect_bank_2', 'laser_toggle']
        repeat_ind_str_list = ['volt_mon_ind']
        numbers_ind_str_list = ['blue_val', 'green_val', 'red_val']
        ascii_list_non_repeat = ['m', 'k', '&', '(', '4', '%','*','(','5', '!']
        ascii_list_repeat = ['+']
        ascii_list_numbers = ['(',')','/']

        truefalse_dict = {False:'0', True:'1'}
        ascii_item_dict_non_repeat=self.dict_maker(ascii_list_non_repeat, current_ind_str_list)
        ascii_item_dict_repeat = self.dict_maker(ascii_list_repeat, repeat_ind_str_list)
        ascii_item_dict_numbers = self.dict_maker(ascii_list_numbers, numbers_ind_str_list)


        # print(ascii_item_dict_repeat)
        # print(ascii_item_dict_non_repeat)
        # print(ascii_item_dict_numbers)

        while x==0:
            for_arduino_list = []
            current_ind_list, repeat_ind_list, numbers_ind_list=self.gui_checker()
            current_ctr=0
            repeat_ctr=0
            numbers_ctr=0

            if loop_ctr==3:
                for items in repeat_ind_list:
                    ascii_char = ascii_item_dict_repeat[repeat_ind_str_list[repeat_ctr]]
                    true_false = truefalse_dict[items]

                    if true_false == "1":
                        for_arduino_list.append(str(ascii_char) + str(true_false))

                    elif true_false == "0":
                        for_arduino_list.append(str(ascii_char)+str(true_false))

                loop_ctr=0

            for items in numbers_ind_list:
                ascii_char = ascii_item_dict_numbers[numbers_ind_str_list[numbers_ctr]]
                if items != previous_numbers_ind_list[numbers_ctr]:
                    for_arduino_list.append(str(ascii_char) + str(items))

                numbers_ctr=numbers_ctr+1

            previous_numbers_ind_list = numbers_ind_list

            for items in current_ind_list:
                ascii_char = ascii_item_dict_non_repeat[current_ind_str_list[current_ctr]]
                true_false = truefalse_dict[items]

                if items != previous_ind_list[current_ctr]:
                    # print(items,previous_ind_list[current_ctr], current_ind_str_list[current_ctr])
                    for_arduino_list.append(str(ascii_char) + str(true_false))

                current_ctr=current_ctr+1

            previous_ind_list=current_ind_list
            for_arduino_str = ','.join(map(str, for_arduino_list))

            if for_arduino_str == '':
                for_arduino_str="x"

            # print(for_arduino_str)
            self.ser.write(for_arduino_str)

            loop_ctr=loop_ctr+1
            time.sleep(.1)

    def dict_maker(self, ascii_list, ind_str_list):
        dict_ctr = 0
        ascii_item_dict={}
        for items in ind_str_list:
            ascii_item_dict[items] = ascii_list[dict_ctr]
            dict_ctr=dict_ctr+1
        return ascii_item_dict

    def gui_checker(self):
        discharge_ind = self.ui.cB_discharge.isChecked()
        if discharge_ind == True:
            discharge_ind = False
        else:
            discharge_ind = True

        bank2_ind = self.ui.cB_bank2Charge.isChecked()
        fire_ind = self.ui.cB_fire.isChecked()
        laser_toggle = self.ui.cB_laser.isChecked()
        volt_mon_ind = self.ui.cB_voltageMonitor.isChecked()
        # bank1_charge_ind = self.ui.cB_bank1chargingIndicator.isChecked()
        inj_charge_ind = self.ui.cB_injectorChargingIndicator.isChecked()
        # if inj_charge_val == True:
        #     inj_charge_ind = False
        # elif inj_charge_val == False:
        #     inj_charge_ind = True
        # inj_ind = self.ui.cB_injector.isChecked()
        bank1_ind = self.ui.cB_bank1Charge.isChecked()
        blue_val = self.ui.vSlider_Blue.value()
        red_val = self.ui.vSlider_Red.value()
        green_val = self.ui.vSlider_Green.value()

        current_ind_list = [bank2_ind, discharge_ind, fire_ind, inj_charge_ind, bank1_ind,
                            self.other.emerg_shutdown, self.other.vehicle_on, self.other.charge_relay1,
                            self.other.connect_bank_2, laser_toggle]
        repeat_ind_list = [volt_mon_ind]
        numbers_ind_list = [blue_val, green_val, red_val]

        return current_ind_list, repeat_ind_list, numbers_ind_list


class VoltageMonitorThread(QThread):
    def __init__(self, ui, serial, self_other):
        QThread.__init__(self)
        self.ui=ui
        self.other=self_other
        self.ser=serial
        print("Voltage Monitor Started")
    def __del__(self):
        self.wait()
    def run(self):
        k=0
        while k==0:
            self.ui.lineEdit_test.setText(str(self.other.emerg_shutdown))
            # self.ser.write("+")
            ser_string = self.ser.readline()
            # print(ser_string)
            for x in ser_string.split(','):
                indicator=x[:1]
                cap_voltage=x[1:]
                # print(x)
                if '+' in indicator:
                    try:
                        # print("CapVoltage= "+str(cap_voltage))
                        adj_cap_voltage=int(cap_voltage)*0.4375476
                        self.ui.sBox_chargeMonitor.setValue(adj_cap_voltage)
                    except ValueError:
                        pass
                time.sleep(0.05)
                if '-' in indicator:
                    try:
                        adj_cap_voltage=int(cap_voltage)*0.4375476
                        self.ui.sBox_chargeMonitor_2.setValue(adj_cap_voltage)
                    except ValueError:
                        pass
                time.sleep(0.05)


class projectFire_thread(QThread):
    def __init__(self, ui):
        QThread.__init__(self)
        self.ui=ui
        self.ser=serial
    def __del__(self):
        self.wait()
    def run(self):
        # self.ser.write("&")
        bank1_val = self.ui.cB_bank1Charge.isChecked()
        self.ui.cB_bank1Charge.setChecked(False)
        time.sleep(.05)
        self.ui.cB_fire.setChecked(True)
        print("Fire")
        time.sleep(1)
        self.ui.cB_bank1Charge.setChecked(bank1_val)
        # self.ser.write("&")

        self.ui.cB_fire.setChecked(False)
        self.ui.pB_Fire.setEnabled(True)

# This class is in place to prevent the caps from being overcharged. Constantly watched cap voltage
# to make sure it doesn't go too high
class emergencyVoltageMonitor(QThread):
    def __init__(self, ui, other_self):
        QThread.__init__(self)
        self.ui=ui
        self.other=other_self
        # self.ser=serial
    def __del__(self):
        self.wait()
    def run(self):
        x=0
        over_charge=False
        ctr=0
        # ctr2=100
        # while x==0:
        #     charge_to=self.ui.sBox_setChargeValue.value()
        #     charge_value=self.ui.sBox_chargeMonitor.value()
        #
        #     if charge_value>charge_to+20:
        #         print("ALERT! CAPACITORS OVER CHARGED")
        #         self.ui.cB_bank1chargingIndicator.setChecked(False)
        #         self.ui.cB_injectorChargingIndicator.setChecked(False)
        #         self.ui.pB_charge1.setEnabled(True)
        #         self.ui.pB_stopCharge1.setEnabled(False)
        #         self.ui.pB_chargeInjector.setEnabled(True)
        #         self.ui.pB_stopChargeInjector.setEnabled(False)
        #         over_charge = True
        #         ctr=ctr+1
        #         # print(ctr,ctr2)
        #
        #     else:
        #         self.other.emerg_shutdown=False
        #
        #     if ctr==4 and ctr2==4:
        #         self.other.emerg_shutdown=True
        #         ctr=0
        #
        #     if self.other.emerg_shutdown == True:
        #         self.ui.pB_alert.setIcon(QtGui.QIcon('emergShutdown_button.png'))
        #         self.ui.pB_alert.setIconSize(QtCore.QSize(230, 230))
        #         print("EMERGENCY SHUTDOWN OF VEHICLE")
        #         self.other.vehicle_on=True
        #     elif over_charge == True:
        #         self.ui.pB_alert.setIcon(QtGui.QIcon('emerg_button.png'))
        #         self.ui.pB_alert.setIconSize(QtCore.QSize(230, 230))
        #
        #     ctr2=ctr+1
        #     time.sleep(1)

class autoChargeThread(QThread):
    # def __init__(self, ui, serial):
    def __init__(self, ui):
        QThread.__init__(self)
        self.ui=ui
        self.ui.cB_bank2Charge.setEnabled(False)
        self.ui.cB_bank1Charge.setEnabled(False)
        # self.ui.cB_injector.setEnabled(False)
        # self.ui.pB_charge1.setEnabled(False)
        self.ui.pB_chargeInjector.setEnabled(False)
        # self.ui.pB_stopCharge1.setEnabled(False)
        self.ui.pB_stopChargeInjector.setEnabled(False)
        # self.ser=serial
    def __del__(self):
        self.wait()
    def run(self):
        loop_ctr=0
        # ctr=0
        target_indicator=False
        stage=0
        while loop_ctr==0:
            # print(ctr)
            # ctr=ctr+1
            charge_value = self.ui.sBox_chargeMonitor.value()
            charge_to = self.ui.sBox_setChargeValue.value()
            # print(charge_to, charge_value)
            if charge_to-25<=charge_value<charge_to and target_indicator==True:
                print("Waiting until charge drops to: " + str(charge_to-25))
                self.ui.cB_injectorChargingIndicator.setChecked(False)
                stage=1

            elif charge_value<charge_to:
            #     ser.write("!1")
                if stage !=2:
                    print("Charging back up to " + str(charge_to) + "V")
                    self.ui.cB_injectorChargingIndicator.setChecked(True)
                    target_indicator=False
                    stage=2

            elif charge_value>=charge_to:
                if stage != 3:
                    self.ui.cB_injectorChargingIndicator.setChecked(False)
                    print("Reached Charging Limit")
                    target_indicator=True
                    stage = 3

                auto_fire_var = self.ui.cB_autoFire.isChecked()
                if auto_fire_var == True:
                    self.ui.pB_Fire.setEnabled(False)
                    self.projectFire_thread = projectFire_thread(self.ui)
                    self.projectFire_thread.start()
            time.sleep(.1)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow=MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())