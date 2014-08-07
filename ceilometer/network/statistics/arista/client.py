# TODO: Copyright notice and stuff

import six
from jsonrpclib import Server
from datetime import datetime

from ceilometer.network.statistics.arista import constants 

class AristaEAPIClient():
    def __init__(self, switch_loc, scheme):
        self.switch_loc = switch_loc
        self.endpoint = "%s://%s/command-api" % (scheme, switch_loc)
    
    def get_samples(self):
        # Pull port data
        req = Server(self.endpoint)
        resp = req.runCmds(version=1,
                           cmds=["show interfaces counters",
                                 "show interfaces counters errors"],
                           timestamps=True)
        
        # Sanity checks
        assert len(resp) == 2, "Response len = %d, expected 2" % len(resp)
        counters = resp[0]
        errors = resp[1]
        assert 'interfaces' in counters, "'interfaces' not in server response!"
        assert 'interfaceErrorCounters' in errors, \
            "'interfaceErrorCounters' not in server response!"
        
        # Start converting data to sample format.
        # i.e. (volume, resource_id, resource_meta, timestamp)
        
        # Setup dictionary
        samples = {}
        for meter in constants.SUPPORTED_METERS:
            samples[meter] = []
        
        # Setup timestamp and initial sample
        timestamp = (datetime.fromtimestamp(counters['_meta']['execStartTime'])
                             .isoformat())
        samples['switch'].append((1, self.switch_loc, {'driver': 'arista'}, timestamp))
        
        # Populate normal counters
        for iface, stats in six.iteritems(counters['interfaces']):
            tail = (self.switch_loc, {"iface": iface, 'driver': 'arista'}, timestamp)
            samples['switch.port'].append((1, ) + tail)
            
            rx_pkts = (int(stats['inUcastPkts']) +
                       int(stats['inMulticastPkts']) +
                       int(stats['inBroadcastPkts']), ) + tail
            tx_pkts = (int(stats['outUcastPkts']) +
                       int(stats['outMulticastPkts']) +
                       int(stats['outBroadcastPkts']), ) + tail
            samples['switch.port.receive.packets'].append(rx_pkts)
            samples['switch.port.transmit.packets'].append(tx_pkts)
            
            rx_bytes = (int(stats['inOctets']),) + tail
            tx_bytes = (int(stats['outOctets']),) + tail
            samples['switch.port.receive.bytes'].append(rx_bytes)
            samples['switch.port.transmit.bytes'].append(tx_bytes)
            
            rx_discards = (int(stats['inDiscards']),) + tail
            tx_discards = (int(stats['outDiscards']),) + tail
            
            samples['switch.port.receive.drops'].append(rx_discards)
            samples['switch.port.transmit.drops'].append(tx_discards)
        
        # Populate error counters
        for iface, stats in six.iteritems(errors['interfaceErrorCounters']):
            tail = (self.switch_loc, {"iface": iface, 'driver': 'arista'}, timestamp)
            
            rx_errs = (int(stats['inErrors']),) + tail
            tx_errs = (int(stats['outErrors']),) + tail
            samples['switch.port.receive.errors'].append(rx_errs)
            samples['switch.port.transmit.errors'].append(tx_errs)
            
            frame_errs = (int(stats['alignmentErrors']),) + tail
            samples['switch.port.receive.frame_error'].append(frame_errs)
            
            #overruns = (int(stats['outErrors']),) + tail 
            #samples['switch.port.receive.overrun_error'].append(overruns)
            
            crc_errs = (int(stats['fcsErrors']),) + tail
            samples['switch.port.receive.crc_error'].append(crc_errs)
        
        return samples
