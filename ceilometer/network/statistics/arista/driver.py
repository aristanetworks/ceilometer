# TODO: Copyright notice and stuff

import traceback
from six.moves.urllib import parse as urlparse

from ceilometer.network.statistics import driver
from ceilometer.network.statistics.arista import constants
from ceilometer.network.statistics.arista import client

class AristaDriver(driver.Driver):
    """ Arista Switch statistics pollster driver. """
    
    def get_sample_data(self, meter_name, parse_url, params, cache):
        # Ignore unsupported meters
        if not meter_name in constants.SUPPORTED_METERS:
            return None
        
        # Grab raw data off switch and check that requested meter exists.
        try:
            samples = self._get_all_samples(parse_url, params, cache)
            assert meter_name in samples, \
                   "Samples for %s unavailable!" % meter_name
        except:
            # Switch connection has failed or meter name not in data.
            print "AristaDriver: unable to get meter data for %s" % meter_name
            traceback.print_exc()
            return None
        
        # Return samples for requested meter
        return samples[meter_name]
    
    @staticmethod
    def _get_all_samples(parse_url, params, cache):
        """ Get all samples to avoid making multiple small requests """
        
        if 'network.statistics.arista' in cache:
            return cache['network.statistics.arista']
        
        # Instantiate EAPI client and grab samples.
        scheme = params.get('scheme', [constants.DEFAULT_AUTH_SCHEME])[0]
        eapi_client = client.AristaEAPIClient(parse_url.netloc, scheme)
        cache['network.statistics.arista'] = eapi_client.get_samples()
        
        return cache['network.statistics.arista']
