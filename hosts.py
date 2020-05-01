import json, base64
import coloredlogs, logging
from onos_api import OnosAPI

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

class Hosts:
    def __init__(self):
        self.__hosts = OnosAPI().get_hosts()
    
    def get_host_id(self, hostname):
        hostname = hostname.strip("H")
        mac = "00:00:00:00:00:{:02x}".format(int(hostname))
        logger.info("Parsed host: " + mac)
        for host in self.__hosts.get("hosts"):
            if host.get("mac") == mac:
                return host.get("id")  
        return ""
    
    def get_host_mac(self, hostname):
        hostname = hostname.strip("H")
        mac = "00:00:00:00:00:{:02x}".format(int(hostname))
        logger.info("Parsed host: " + mac)
        for host in self.__hosts.get("hosts"):
            if host.get("mac") == mac:
                return host.get("mac")  
        return ""



