# SMS Notifier

This is just a short script that registers a message received handler on
a ModemManager-handled modem. That handler reads every message via libnotify.

## Install

If necessary, change the modem_object variable in sms-notify.py. If you
only have one modem, everything should be alright by default.

## Usage

Just run
```bash
    $ ./sms-notify.py
```
and send a text message from your phone.
