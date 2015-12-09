# sd-rabbitmqooz

## Introduction

A comprehensive server density plugin for RabbitMQ. It's still a work in progress but here is some of the metrics covered so far.

> **Note:** Metrics definitions based on rabbitmq management http api [documentation](http://hg.rabbitmq.com/rabbitmq-management/raw-file/c1c6c64ac1ab/priv/www/doc/stats.html).

### **Metrics**

**publish**: Count of messages published.
**publish_rate**:  How much the count has changed per second in the most recent sampling interval.

**delivered_messages**  
**delivered_messages_rate**
Count of messages delivered in acknowledgement mode to consumers.

**delivered_noAck_messages**  
**delivered_noAck_messages_rate**  
Count of messages delivered in no-acknowledgement mode to consumers.

**delivered_basicGet_messages**  
**delivered_basicGet_messages_rate**  
Count of messages delivered in acknowledgement mode in response to basic.get.

**delivered_basicGet_noAck_messages**  
**delivered_basicGet_noAck_messages_rate**  
Count of messages delivered in no-acknowledgement mode in response to basic.get.

**all_delivered**  
**all_delivered_rate**  
Sum of all four of deliver + deliver_noack + get + get_noack

**total_messages_in_queues**:  Total number of messages in all queues.
**total_messages_ready_in_queues** : Total number of messages in all queues with acknowledge-mode
**total_messages_noAck_in_queues**: Total number of messages in all queues with no-acknowledge-mode


----------


## Installation

 - go to directory **/usr/bin/sd-agent/plugins/** (your server density agent directory)
 - download plugin **wget https://raw.githubusercontent.com/khalilovcmd/sd-rabbitmqooz/master/RabbitMQooz.py**
 - edit **/etc/sd-agent/config.cfg**

    **[RabbitMQooz]**  
    **host**: http://rabbitmyqserver.com  
    **port**: 55672  
    **username**: guest  
    **password**: 123456

 - **service sd-agent restart**

----------

## Usage

TODO: Write usage instructions

----------

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

----------

## History

TODO: Write history





