""" Message sender module to send messages  to MQ systems via STOMP protocol.
"""
import logging
import stomp

class StompSender(object):
  """ Stomp message sender.
      It depends on stomp module.
  """
  REQUIRED_KEYS = ['QueuePath', 'Host', 'Port']
  OPTIONAL_KEYS_GROUPS = [['HostKey', 'HostCertififcate','CACertificate'], ['Username','Password']]

  def __init__(self, params):
    """
      Raises:
        ValueError: If params are not correct.
    """
    self.params = params
    if not self._areParamsCorrect(self.params, self.REQUIRED_KEYS, self.OPTIONAL_KEYS_GROUPS):
      raise ValueError("Parameters missing needed to send message.")

  def sendMessage(self, msg):
    """ Method checks if the connection
        to the MQ server is up and sends the message.
        If the connection is down, the method
        does nothing and returns False
    Returns:
      bool: False in case of any errors, True otherwise
    """

    queue = self.params.get('QueuePath')
    connection = self._connect(self.params)
    if not connection:
      return False
    res = self._send(msg,queue,connection)
    if not res:
      return False
    self._disconnect(connection)
    return True

  def _connect(self, params):
    """ Connects to MQ server and returns connection
        handler or None in case of connection down.
        Stomp-depended function.
    Return:
      stomp.Connection: or None in case of errors.
    """
    hostAndPort = [(self.params.get('Host'), int(self.params.get('Port')))]
    try:
      if self._isUserPassword(params):
        connection = stomp.Connection(host_and_ports=hostAndPort, use_ssl=False)
        connection.start()
        connection.connect(params.get('Username'), params.get('Password'))
      else:
        connection.set_ssl(for_hosts=hostAndPort,
                           key_file=params.get('HostKey'),
                           cert_file=params.get('HostCertificate'),
                           ca_certs=params.get('CACertificate'))
        connection = stomp.Connection(host_and_ports=hostAndPort, use_ssl=True)
        connection.start()
        connection.connect()
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

  def _isUserPassword(self, params):
    return 'Username' in params

  def _areParamsCorrect(self, params, requiredKeys, optionalKeyGroups):
    """
      Args:
        params(dict):
      Return:
        bool:
    """
    if not params:
      return False
    if not all(k in params for k in requiredKeys):
      print "not all in required?"
      return False
    optionalRes = [all(k in params for k in keyGroup) for keyGroup in optionalKeyGroups]
    if not any(optionalRes):
      print "not any in optional?"
      return False
    return True
