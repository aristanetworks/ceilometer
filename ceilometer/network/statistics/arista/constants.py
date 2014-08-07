# TODO: Copyright notice and stuff

DEFAULT_AUTH_SCHEME = 'https'

SUPPORTED_METERS = [ 'switch',
                     'switch.port',
                     'switch.port.receive.packets',
                     'switch.port.transmit.packets',
                     'switch.port.receive.bytes',
                     'switch.port.transmit.bytes',
                     'switch.port.receive.drops',
                     'switch.port.transmit.drops',
                     'switch.port.receive.errors',
                     'switch.port.transmit.errors',
                     'switch.port.receive.frame_error',
                     #'switch.port.receive.overrun_error',
                     'switch.port.receive.crc_error' ]
                     #'switch.port.collision.count' ] 