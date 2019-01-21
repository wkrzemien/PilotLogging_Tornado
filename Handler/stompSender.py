import logging
import stomp

class StompSender(object):
  """ Stomp message sender.
      It depends on stomp module.
  """
  def __init__(self, params):
    """
      Raises:
        ValueError: If params are not correct.
    """
    self.params = params

  def sendMessage(self, msg, flag):
    """ Method first copies the message content to the
        local storage, then it checks if the connection
        to the MQ server is up,
        If it is the case it sends all messages stored
        locally.  The string flag can be used as routing_key,
        it can contain:  'info', 'warning', 'error',
        'debug'. If the connection is down, the method
        does nothing and returns False
    Returns:
      bool: False in case of any errors, True otherwise
    """

    # queue = self.params.get('QueuePath')
    # host = self.params.get('Host')
    # port = int(self.params.get('Port'))
    # hostKey = self.params.get('HostKey')
    # hostCertificate = self.params.get('HostCertificate')
    # CACertificate = self.params.get('CACertificate')
    credentials = {'username':'ala', 'passcode':'ala'}
    # credentials = {'key_file': hostKey, 'cert_file': hostCertificate, 'ca_certs': CACertificate}
    # host = '127.0.0.1'
    host = '127.0.0.1'

    port = int(61613)
    queue = '/queue/test'
      
    connection = self._connect([(host, port)], credentials)
    if not connection:
      return False
    res = self._send(msg,queue,connection)
    if not res:
      return False
    self._disconnect(connection)
    return True

  def _connect(self, hostAndPort, credentials):
    """ Connects to MQ server and returns connection
        handler or None in case of connection down.
        Stomp-depended function.
    Args:
      hostAndPort(list): of tuples, containing ip address and the port 
                         where the message broker is listening for stomp 
                         connections. e.g. [(127.0.0.1,6555)]
      credentials(dict): with three keys 'key_file', 'cert_file', and 'ca_certs'. TO BE CHANGED
    Return:
      stomp.Connection: or None in case of errors. 
    """
    # if not sslCfg:
      # logging.error("sslCfg argument is None")
      # return None
    if not hostAndPort:
      logging.error("hostAndPort argument is None")
      return None
    # if not all(key in sslCfg for key in ['key_file', 'cert_file', 'ca_certs']):
      # logging.error("Missing sslCfg keys")
      # return None

    try:
      connection = stomp.Connection(host_and_ports=hostAndPort, use_ssl=False)
      # connection.set_ssl(for_hosts=hostAndPort,
                         # key_file=sslCfg['key_file'],
                         # cert_file=sslCfg['cert_file'],
                         # ca_certs=sslCfg['ca_certs'])
      # connection = stomp.Connection(host_and_ports=hostAndPort, use_ssl=True)
      # connection.set_ssl(for_hosts=hostAndPort,
                         # key_file=sslCfg['key_file'],
                         # cert_file=sslCfg['cert_file'],
                         # ca_certs=sslCfg['ca_certs'])
      connection.start()
      # connection.connect()

      connection.connect(credentials['username'], credentials['passcode'])
      return connection
    except stomp.exception.ConnectFailedException:
      logging.error('Connection error')
      return None
    except IOError:
      logging.error('Could not find files with ssl certificates')
      return None


  def _send(self, msg, destination, connectHandler):
    """Sends a message and logs info.
       Stomp-depended function.
    """
    if not connectHandler:
      return False
    connectHandler.send(destination=destination,
                        body=msg)
    logging.info(" [x] Sent %r ", msg)
    return True


  def _disconnect(self, connectHandler):
    """Disconnects.
       Stomp-depended function.
    """
    connectHandler.disconnect()

