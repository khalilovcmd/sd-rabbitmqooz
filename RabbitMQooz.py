import json
import urllib2
import base64
import json
import logging
import os
import platform
import sys
import time

class RabbitMQooz(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()
        
        self.api_overview = '/api/overview'
        self.api_queues = '/api/queues'
        self.api_aliveness  = '/api/aliveness-test'
        self.api_connections = '/api/connections'
        
        self.host = self.raw_config['RabbitMQooz'].get('host', 'localhost').strip('/')
        self.port = self.raw_config['RabbitMQooz'].get('port', '55672')
        self.username = self.raw_config['RabbitMQooz'].get('username', '')
        self.password = self.raw_config['RabbitMQooz'].get('password', '')
        
     # make a base64 of the username and password combination (for HTTP basic authentication)
    def make_base64(self):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        return base64string
        
    # make http request and add base64 authentication header    
    def make_http_request(self, resource, auth, parameters, headers):
         # create http request
        request = urllib2.Request(self.host + ':' + self.port + resource)
        
        # add basic authorization header
        request.add_header("Authorization", "Basic %s" % auth)
        
        # make request
        return urllib2.urlopen(request)
    
    def make_overview(self,data):
         # make base64 for auth
        base64string = self.make_base64()
        
        # make http request
        http = self.make_http_request(base64string)
        
        # check if http code is 200
        if http.getcode() == 200:
            
            content = http.read()
            parsed_json = json.loads(content)
            
            if content:
                
                if 'publish' in parsed_json['message_stats']:
                    data['publish'] = parsed_json['message_stats']['publish']
                    data['publish_rate'] = parsed_json['message_stats']['publish_details']['rate']
                else:
                    data['publish'] = 0
                    data['publish_rate'] = 0     
                
                if 'deliver' in parsed_json['message_stats']:
                    # Count of messages delivered in acknowledgement mode to consumers.
                    data['delivered_messages'] = parsed_json['message_stats']['deliver']
                    data['delivered_messages_rate'] = parsed_json['message_stats']['deliver_details']['rate']
                else:
                    data['delivered_messages'] = 0
                    data['delivered_messages_rate'] = 0     
                
                if 'deliver_noack' in parsed_json['message_stats']:
                    # Count of messages delivered in no-acknowledgement mode to consumers.
                    data['delivered_noAck_messages'] = parsed_json['message_stats']['deliver_noack']
                    data['delivered_noAck_messages_rate'] = parsed_json['message_stats']['deliver_noack_details']['rate']
                else:
                    data['delivered_noAck_messages'] = 0
                    data['delivered_noAck_messages_rate'] = 0    
                
                if 'get_ack' in parsed_json['message_stats']:
                    # Count of messages delivered in acknowledgement mode in response to basic.get.
                    data['delivered_basicGet_messages'] = parsed_json['message_stats']['get_ack']
                    data['delivered_basicGet_messages_rate'] = parsed_json['message_stats']['get_ack_details']['rate']
                else:
                    data['delivered_basicGet_messages'] = 0
                    data['delivered_basicGet_messages_rate'] = 0        
                
                if 'get_no_ack' in parsed_json['message_stats']:
                    # Count of messages delivered in no-acknowledgement mode in response to basic.get.
                    data['delivered_basicGet_noAck_messages'] = parsed_json['message_stats']['get_no_ack']
                    data['delivered_basicGet_noAck_messages_rate'] = parsed_json['message_stats']['get_no_ack_details']['rate']
                else:
                    data['delivered_basicGet_noAck_messages'] = 0
                    data['delivered_basicGet_noAck_messages'] = 0          
                
                if 'deliver_get' in parsed_json['message_stats']:
                    # Sum of all four of deliver + deliver_noack + get + get_noack
                    data['all_delivered'] = parsed_json['message_stats']['deliver_get']
                    data['all_delivered_rate'] = parsed_json['message_stats']['deliver_get_details']['rate']
                else:
                    data['all_delivered'] = 0
                    data['all_delivered_rate'] = 0      
                
                if 'queue_totals' in parsed_json['message_stats']: 
                    # queue messages
                    data['total_messages_in_queues'] = parsed_json['queue_totals']['messages']
                    # queue message with acknowledge-mode
                    data['total_messages_ready_in_queues'] = parsed_json['queue_totals']['messages_ready']
                    # queue message with no-acknowledge-mode
                    data['total_messages_noAck_in_queues'] = parsed_json['queue_totals']['messages_unacknowledged']
                else:
                    data['total_messages_in_queues'] = 0
                    data['total_messages_ready_in_queues'] = 0         
                    data['total_messages_noAck_in_queues'] = 0
                    
        return data

    def run(self):
        
        # data object to return after calling run() function
        data = {}
        
       
        
        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'RabbitMQooz': {
            'host': 'localhost',
            'port': '55672',
            'username' : 'guest',
            'password': '123456'
        }
    }
    
    main_checks_logger = logging.getLogger('RabbitMQooz')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    rabbitmq = RabbitMQooz({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(rabbitmq.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(5)