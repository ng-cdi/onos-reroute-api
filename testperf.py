import requests 
import uuid
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

class TestPerf:

    def __init__(self):
        h = {'Content-type': 'application/json',}
        logger.info("Killing all iperfs")
        for c in range(1, 10):
            d = '{\"command\": \"killall iperf3\", \"name\": \"kill iperf' + str(uuid.uuid4()) + '\"}'
            logger.info("h"  + str(c) + " | " + str(requests.post("http://localhost:8080/cmd/h" + str(c), headers = h, data = d)))
        
        logger.info("Starting all iperfs...")
        s = 1
        for j in range(7, 10):
            e = s + 2
            self.__iperf(s, e, h, j)
            s = e
                
        logger.info("Complete!")



    def __iperf(self, startHost, endHost, h, j):
        for i in range(startHost, endHost):
            d = '{\"command\": \"iperf3 -s -p 520' + str(i) + '\", \"name\": \"iperf' + str(uuid.uuid4()) + '\"}'
            logger.info("[MNO] h"  + str(i) + " | " + str(requests.post("http://localhost:8080/cmd/h" + str(j), headers = h, data = d)))
            
            d = '{\"command\": \"iperf3 -c 10.0.0.' + str(j) + ' -t 600 -p 520' + str(i) + '\", \"name\": \"iperf' + str(uuid.uuid4())+ '\"}'
            logger.info("[BTS] h"  + str(i) + " | " + str(requests.post("http://localhost:8080/cmd/h" + str(i), headers = h, data=d)))