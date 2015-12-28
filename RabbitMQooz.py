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

        self.raw_config = raw_config
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.version = platform.python_version_tuple()

        self.api_queues = '/api/queues'
        self.api_nodes = '/api/nodes'
        self.api_overview = '/api/overview'
        self.api_connections = '/api/channels'
        self.api_connections = '/api/connections'

        #self.api_vhosts = '/api/vhosts'

        self.host = self.raw_config['RabbitMQooz'].get('host', 'localhost').strip('/')
        self.port = self.raw_config['RabbitMQooz'].get('port', '55672')
        self.username = self.raw_config['RabbitMQooz'].get('username', '')
        self.password = self.raw_config['RabbitMQooz'].get('password', '')
        self.queues = self.raw_config['RabbitMQooz'].get('queues', '')
        self.nodes = self.raw_config['RabbitMQooz'].get('nodes', '')
        
     # make a base64 of the username and password combination (for HTTP basic authentication)
    def make_base64(self):
        return base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        
    # make basic authentication string 
    def make_basic_authentication(self, auth):
        return ("Authorization", "Basic %s" % auth)
        
    # make http request and add base64 authentication header    
    def make_http_request(self, resource, parameters, headers):
        
        # create http request
        request = urllib2.Request(self.host + ':' + self.port + resource) 
        
        if parameters and len(parameters) > 0:
            pass
        
        # adding headers
        if headers and len(headers) > 0:
            for (key, value) in headers:
                request.add_header(key, value)
        
        # make request
        return urllib2.urlopen(request)

    def convert_from_bytes_to_megabytes(self, bytes):
        return bytes / 1024 / 1024
        
    # fetch metrics for "api/queues" endpoint   
    def fetch_queues_metrics(self, data):

        if self.queues:

            queues = self.queues.split(',')

             # make base64 for auth
            base64_result = self.make_base64()

            # make basic authentication header
            auth_result = self.make_basic_authentication(base64_result)

            # make http request
            http = self.make_http_request(self.api_queues, None, [auth_result])

            # http code is 200, read results
            if http.getcode() == 200:

                # read http content
                content = http.read()

                # parse json
                parsed_json = json.loads(content)

                if content:
                    for j in parsed_json:
                        if j['name'].lower() in queues and j['vhost']:
                            data[j['vhost'] + '.' + j['name'] + '.' + 'memory'] = j['memory']
                            data[j['vhost'] + '.' + j['name'] + '.' + 'messages_ready'] = j['messages_ready']
                            data[j['vhost'] + '.' + j['name'] + '.' + 'messages_unacknowledged'] = j['messages_unacknowledged']
                            data[j['vhost'] + '.' + j['name'] + '.' + 'messages'] = j['messages']
                            data[j['vhost'] + '.' + j['name'] + '.' + 'consumers'] = j['consumers']

                            if 'rate' in j['messages_details']:
                                data[j['vhost'] + '.' + j['name'] + '.' + 'messages_rate'] = j['messages_details']['rate']

                            if 'rate' in j['messages_ready_details']:
                                data[j['vhost'] + '.' + j['name'] + '.' + 'messages_ready_rate'] = j['messages_ready_details']['rate']

                            if 'rate' in j['messages_unacknowledged_details']:
                                data[j['vhost'] + '.' + j['name'] + '.' + 'messages_unacknowledged_rate'] = j['messages_unacknowledged_details']['rate']

    # fetch metrics for "api/nodes" endpoint
    def fetch_nodes_metrics(self, data):

        if self.nodes:

            nodes = self.nodes.split(',')

             # make base64 for auth
            base64_result = self.make_base64()

            # make basic authentication header
            auth_result = self.make_basic_authentication(base64_result)

            # make http request
            http = self.make_http_request(self.api_nodes, None, [auth_result])

            # http code is 200, read results
            if http.getcode() == 200:

                # read http content
                content = http.read()

                # parse json
                parsed_json = json.loads(content)

                if content:
                    for j in parsed_json:
                        if j['name'].lower() in nodes:
                            data[j['name'] + '.' + 'memory_used_megabyte'] = self.convert_from_bytes_to_megabytes(j['mem_used'])
                            data[j['name'] + '.' + 'memory_free_megabyte'] = self.convert_from_bytes_to_megabytes(j['mem_limit'])
                            data[j['name'] + '.' + 'disk_free_megabyte'] = self.convert_from_bytes_to_megabytes(j['disk_free'])
                            data[j['name'] + '.' + 'processes_used'] = j['proc_used']
                            data[j['name'] + '.' + 'processes_remaining'] = j['proc_total'] - j['proc_used']
                            data[j['name'] + '.' + 'file_descriptors_used'] = j['fd_used']
                            data[j['name'] + '.' + 'file_descriptors_remaining'] = j['fd_total'] - j['fd_used']
                            data[j['name'] + '.' + 'sockets_used'] = j['sockets_used']
                            data[j['name'] + '.' + 'sockets_remaining'] = j['sockets_total'] - j['sockets_used']
                            data[j['name'] + '.' + 'running'] = 1 if j['running'] else 0

    # fetch metrics for "api/aliveness-test" endpoint    
    def fetch_aliveness_metrics(self, data):
        return None
    
    # fetch metrics for "api/overview" endpoint
    def fetch_overview_metrics(self,data):
        
         # make base64 for auth
        base64_result = self.make_base64()
        
        # make basic authentication header
        auth_result = self.make_basic_authentication(base64_result)
        
        # make http request
        http = self.make_http_request(self.api_overview, None, [auth_result]) 
        
        # http code is 200, read results
        if http.getcode() == 200:
            
            # read http content
            content = http.read()
            
            # parse json
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
                
                if parsed_json['queue_totals']: 
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
        
        data = {} # data object to return after calling run() function
        
        self.fetch_overview_metrics(data)
        self.fetch_queues_metrics(data)
        self.fetch_nodes_metrics(data)
        
        return data

if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'RabbitMQooz': {
            'host': 'localhost',
            'port': '55672',
            'username' : 'guest',
            'password': 'pass',
            'queues' : 'queue1,queue2',
            'nodes' : 'node1,node2'
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
            time.sleep(25)