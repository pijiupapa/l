from blinker import signal

engine_setup = signal('engine_setup')
engine_start = signal('engine_start')
engine_stop =  signal('engine_stop')
