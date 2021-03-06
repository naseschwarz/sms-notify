#/usr/bin/env python2
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import pynotify

bus_name = "org.freedesktop.ModemManager1"
sms_base_object = "/org/freedesktop/ModemManager1/SMS/"
modem_object = "/org/freedesktop/ModemManager1/Modem/0"

DBusGMainLoop(set_as_default=True)

system_bus = dbus.SystemBus()

class mm_sms:
    def _get_manager(self, interface):
        sms_proxy = system_bus.get_object(bus_name, self.sms_path)
        return dbus.Interface(sms_proxy, interface)
    
    def _get_properties_manager(self):
        return self._get_manager("org.freedesktop.DBus.Properties")
    
    def _get_sms_manager(self):
        return self._get_manager("org.freedesktop.ModemManager1.Sms")

    def _load_sms(self, sms_path):
        self.sms_path = sms_path
        sms_manager   = self._get_properties_manager()
        self.text     = sms_manager.Get(bus_name + ".Sms", "Text")
        self.sender   = sms_manager.Get(bus_name + ".Sms", "Number")
        self.received = True

    def _create_sms(self, recipient, text):
        self.sms_path  = self._modem.create_message(recipient, text)
        self.received  = False
        self.text      = text
        self.recipient = recipient

    def __init__(self, sms_path = None, recipient = None, text = None, 
            modem = None):
        self.sms_path  = None
        self.sender    = None
        self.received  = None
        self.recipient = None
        self._modem    = modem
        if sms_path != None:
            self._load_sms(sms_path)
        elif recipient != None:
            self._create_sms(recipient, text)

    def pretty(self):
        if (self.received == True):
            return ("SMS %s from <%s> says: %s" 
                    % (self.sms_path, self.sender, self.text))
        elif (self.received == False):
            return ("SMS %s to <%s> says: %s" 
                    % (self.sms_path, self.recipient, self.text))

    def delete_from_modem(self):
        self._modem.delete_message(self.sms_path)

    def send(self):
        sms_manager = self._get_sms_manager()
        sms_manager.Send()

class mm_modem_messaging:
    def __init__(self, modem_id = 0):
        self._messaging_proxy = system_bus.get_object(bus_name, modem_object)
        self._messaging_manager = dbus.Interface(self._messaging_proxy,
                        "org.freedesktop.ModemManager1.Modem.Messaging")
    
    def delete_message(self, path):
        self._messaging_manager.Delete(path)

    def add_added_callback(self, handler):
        self._messaging_manager.connect_to_signal("Added", handler)

    def create_message(self, number, text):
        return self._messaging_manager.Create({
                'number': number, 
                'text': text,
            })
        
modem = mm_modem_messaging()

def handler(path = None, received = None):
    print("Got signal from %s, received = %d" % (path, received))
    sms = mm_sms(sms_path = path, modem = modem)
    print(sms.pretty())
    title = "SMS Received from %s" % sms.sender
    text  = sms.text
    icon  = "/usr/share/icons/Tango/32x32/status/sunny.png"
    pynotify.init("Test Application")
    notification = pynotify.Notification(title, text, icon) 
    notification.set_urgency(pynotify.URGENCY_NORMAL)
    notification.show() 
    sms.delete_from_modem()

modem.add_added_callback(handler)
#sms = mm_sms(modem = modem, recipient = '+49-and-so-on', text = 'Test')
#sms.send()
loop = gobject.MainLoop()
loop.run()
