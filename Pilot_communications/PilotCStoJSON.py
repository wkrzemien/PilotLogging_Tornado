""" CStoJSONSynchronizer
  Module that keeps the pilot parameters file synchronized with the information
  in the Operations/Pilot section of the CS. If there are additions in the CS,
  these are incorporated to the file.
  The module uploads to a web server the latest version of the pilot scripts.
"""

from __future__ import print_function
__RCSID__ = '$Id$'

import json

import shutil
import os
import glob
import tarfile
import requests

from git import Repo

from DIRAC import gLogger, S_OK, gConfig, S_ERROR
from DIRAC.Core.Security.Locations import getHostCertificateAndKeyLocation
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations





class PilotCStoJSONSynchronizer(object):
  """
  2 functions are executed:
  - It updates a JSON file with the values on the CS which can be used by Pilot3 pilots
  - It updates the pilot 3 files
  This synchronizer can be triggered at any time via PilotCStoJSONSynchronizer().sync().
  As it is today, this is triggered every time there is a successful write on the CS.
  """

  def __init__(self):
    """ c'tor
        Just setting defaults
    """
    self.name_of_group = 'test'
    self.jsonFile = 'pilot.json'  # default filename of the pilot json file

    # domain name of the web server used to upload the pilot json file and the pilot scripts
    self.pilotFileServer = ''

    # pilot sync parameters
    self.pilotRepo = 'https://github.com/DIRACGrid/Pilot.git'  # repository of the pilot
    self.pilotVORepo = ''  # repository of the VO that can contain a pilot extension
    # 'pilotLocalRepo' = 'pilotLocalRepo'  # local repository to be created
    # 'pilotVOLocalRepo' = 'pilotVOLocalRepo'  # local VO repository to be created
    self.pilotSetup = gConfig.getValue('/DIRAC/Setup', '')
    self.projectDir = ''
    # where the find the pilot scripts in the VO pilot repository
    self.pilotScriptPath = 'Pilot'  # where the find the pilot scripts in the pilot repository
    self.pilotVOScriptPath = ''
    self.pilotVersion = ''
    self.pilotVOVersion = ''
    self.certAndKeyLocation = getHostCertificateAndKeyLocation()

  def sync(self):
    """ Main synchronizer method.
    """
    ops = Operations()

    self.pilotFileServer = ops.getValue("Pilot/pilotFileServer", self.pilotFileServer)
    if not self.pilotFileServer:
      gLogger.warn("The /Operations/<Setup>/Pilot/pilotFileServer option is not defined")
      gLogger.warn("Pilot 3 files won't be updated, and you won't be able to use Pilot 3")
      gLogger.warn("The Synchronization steps are anyway displayed")

    gLogger.notice('-- Synchronizing the content of the JSON file %s with the content of the CS --' % self.jsonFile)

    self.pilotRepo = ops.getValue("Pilot/pilotRepo", self.pilotRepo)
    self.pilotVORepo = ops.getValue("Pilot/pilotVORepo", self.pilotVORepo)
    self.projectDir = ops.getValue("Pilot/projectDir", self.projectDir)
    self.pilotScriptPath = ops.getValue("Pilot/pilotScriptsPath", self.pilotScriptPath)
    self.pilotVOScriptPath = ops.getValue("Pilot/pilotVOScriptsPath", self.pilotVOScriptPath)

    result = self._syncJSONFile()
    if not result['OK']:
      gLogger.error("Error uploading the pilot file: %s" % result['Message'])
      return result

    gLogger.notice('-- Synchronizing the pilot scripts %s with the content of the repository --' % self.pilotRepo)

    self._syncScripts()

    return S_OK()

  def get_DN(self, name_of_group):
      '''This function return DN of users in group
         which is defined as name_of_group from configuration file'''
      if not isinstance(name_of_group, basestring):
          return S_ERROR('Name of group must be string')
      else:
         try:
             string_list=gConfig.getValue('/Registry/Groups/'+name_of_group+'/Users')
             Users_list=string_list.split(',')
             DN_list=[gConfig.getValue('/Registry/Users/'+user+'/DN') for user in Users_list]
             return S_OK(json.dumps(DN_list))
         except AttributeError:
             return S_ERROR('There must be problem with name of group')


  def _syncJSONFile(self):
    """ Creates the pilot dictionary from the CS, ready for encoding as JSON
    """
    pilotDict = self._getCSDict()

    result = self._upload(pilotDict=pilotDict)
    if not result['OK']:
      gLogger.error("Error uploading the pilot file: %s" % result['Message'])
      return result
    return S_OK()


  def _getCSDict(self):
    """ Gets minimal info for running a pilot, from the CS
    :returns: pilotDict (containing pilots run info)
    :rtype: dict
    """

    pilotDict = {'Setups': {}, 'CEs': {}, 'DNs':{}}

    gLogger.info('-- Getting the content of the CS --')

    # These are in fact not only setups: they may be "Defaults" sections, or VOs, in multi-VOs installations
    setups = gConfig.getSections('/Operations/')
    if not setups['OK']:
      gLogger.error(setups['Message'])
      return setups
    setups = setups['Value']

    try:
      setups.remove('SoftwareDistribution')  # TODO: remove this section
    except (AttributeError, ValueError):
      pass

    # Something inside? (for multi-VO setups)
    for vo in setups:
      setupsFromVOs = gConfig.getSections('/Operations/%s' % vo)
      if not setupsFromVOs['OK']:
        continue
      else:
        setups.append("%s/%s" % (vo, setupsFromVOs))

    gLogger.verbose('From Operations/[Setup]/Pilot')

    for setup in setups:
      self._getPilotOptionsPerSetup(setup, pilotDict)

    gLogger.verbose('From Resources/Sites')
    sitesSection = gConfig.getSections('/Resources/Sites/')
    if not sitesSection['OK']:
      gLogger.error(sitesSection['Message'])
      return sitesSection

    for grid in sitesSection['Value']:
      gridSection = gConfig.getSections('/Resources/Sites/' + grid)
      if not gridSection['OK']:
        gLogger.error(gridSection['Message'])
        return gridSection

      for site in gridSection['Value']:
        ceList = gConfig.getSections('/Resources/Sites/' + grid + '/' + site + '/CEs/')
        if not ceList['OK']:
          # Skip but log it
          gLogger.error('Site ' + site + ' has no CEs! - skipping')
          continue

        for ce in ceList['Value']:
          ceType = gConfig.getValue('/Resources/Sites/' + grid + '/' + site + '/CEs/' + ce + '/CEType')

          if ceType is None:
            # Skip but log it
            gLogger.error('CE ' + ce + ' at ' + site + ' has no option CEType! - skipping')
          else:
            pilotDict['CEs'][ce] = {'Site': site, 'GridCEType': ceType}

    pilotDict['DNs']=self.get_DN(self.name_of_group)['Value']

    defaultSetup = gConfig.getValue('/DIRAC/DefaultSetup')
    if defaultSetup:
      pilotDict['DefaultSetup'] = defaultSetup

    gLogger.verbose('From DIRAC/Configuration')
    pilotDict['ConfigurationServers'] = gConfig.getServersList()

    gLogger.verbose("Got %s" % str(pilotDict))

    return pilotDict

  def _getPilotOptionsPerSetup(self, setup, pilotDict):
    """ Given a setup, returns its pilot options in a dictionary
    """

    options = gConfig.getOptionsDict('/Operations/%s/Pilot' % setup)
    if not options['OK']:
      gLogger.warn("Section /Operations/%s/Pilot does not exist: skipping" % setup)
      return

    # We include everything that's in the Pilot section for this setup
    if setup == self.pilotSetup:
      self.pilotVOVersion = options['Value']['Version']
    pilotDict['Setups'][setup] = options['Value']
    ceTypesCommands = gConfig.getOptionsDict('/Operations/%s/Pilot/Commands' % setup)
    if ceTypesCommands['OK']:
      # It's ok if the Pilot section doesn't list any Commands too
      pilotDict['Setups'][setup]['Commands'] = {}
      for ceType in ceTypesCommands['Value']:
        # FIXME: inconsistent that we break Commands down into a proper list but other things are comma-list strings
        pilotDict['Setups'][setup]['Commands'][ceType] = ceTypesCommands['Value'][ceType].split(', ')
        # pilotDict['Setups'][setup]['Commands'][ceType] = ceTypesCommands['Value'][ceType]
    if 'CommandExtensions' in pilotDict['Setups'][setup]:
      # FIXME: inconsistent that we break CommandExtensionss down into a proper
      # list but other things are comma-list strings
      pilotDict['Setups'][setup]['CommandExtensions'] = pilotDict['Setups'][setup]['CommandExtensions'].split(', ')
      # pilotDict['Setups'][setup]['CommandExtensions'] = pilotDict['Setups'][setup]['CommandExtensions']

    # Getting the details aboout the MQ Services to be used for logging, if any
    if 'LoggingMQService' in pilotDict['Setups'][setup]:
      loggingMQService = gConfig.getOptionsDict('/Resources/MQServices/%s'
                                                % pilotDict['Setups'][setup]['LoggingMQService'])
      if not loggingMQService['OK']:
        gLogger.error(loggingMQService['Message'])
        return loggingMQService
      pilotDict['Setups'][setup]['Logging'] = {}
      pilotDict['Setups'][setup]['Logging']['Host'] = loggingMQService['Value']['Host']
      pilotDict['Setups'][setup]['Logging']['Port'] = loggingMQService['Value']['Port']

      loggingMQServiceQueuesSections = gConfig.getSections('/Resources/MQServices/%s/Queues'
                                                           % pilotDict['Setups'][setup]['LoggingMQService'])
      if not loggingMQServiceQueuesSections['OK']:
        gLogger.error(loggingMQServiceQueuesSections['Message'])
        return loggingMQServiceQueuesSections
      pilotDict['Setups'][setup]['Logging']['Queue'] = {}

      for queue in loggingMQServiceQueuesSections['Value']:
        loggingMQServiceQueue = gConfig.getOptionsDict('/Resources/MQServices/%s/Queues/%s'
                                                       % (pilotDict['Setups'][setup]['LoggingMQService'], queue))
        if not loggingMQServiceQueue['OK']:
          gLogger.error(loggingMQServiceQueue['Message'])
          return loggingMQServiceQueue
        pilotDict['Setups'][setup]['Logging']['Queue'][queue] = loggingMQServiceQueue['Value']

      queuesRes = gConfig.getSections('/Resources/MQServices/%s/Queues'
                                      % pilotDict['Setups'][setup]['LoggingMQService'])
      if not queuesRes['OK']:
        return queuesRes
      queues = queuesRes['Value']
      queuesDict = {}
      for queue in queues:
        queueOptionRes = gConfig.getOptionsDict('/Resources/MQServices/%s/Queues/%s'
                                                % (pilotDict['Setups'][setup]['LoggingMQService'], queue))
        if not queueOptionRes['OK']:
          return queueOptionRes
        queuesDict[queue] = queueOptionRes['Value']
      pilotDict['Setups'][setup]['Logging']['Queues'] = queuesDict

  def _syncScripts(self):
    """Clone the pilot scripts from the repository and upload them to the web server
    """
    gLogger.info('-- Uploading the pilot scripts --')

    tarFiles = []

    # Extension, if it exists
    if self.pilotVORepo:
      if os.path.isdir('pilotVOLocalRepo'):
        shutil.rmtree('pilotVOLocalRepo')
      os.mkdir('pilotVOLocalRepo')
      repo_VO = Repo.init('pilotVOLocalRepo')
      upstream = repo_VO.create_remote('upstream', self.pilotVORepo)
      upstream.fetch()
      upstream.pull(upstream.refs[0].remote_head)
      if repo_VO.tags:
        repo_VO.git.checkout(repo_VO.tags[self.pilotVOVersion], b='pilotVOScripts')
      else:
        repo_VO.git.checkout('upstream/master', b='pilotVOScripts')
      scriptDir = (os.path.join('pilotVOLocalRepo', self.projectDir, self.pilotVOScriptPath, "*.py"))
      for fileVO in glob.glob(scriptDir):
        result = self._upload(filename=os.path.basename(fileVO), pilotScript=fileVO)
        if not result['OK']:
          gLogger.error("Error uploading the VO pilot script: %s" % result['Message'])
        tarFiles.append(fileVO)
    else:
      gLogger.warn("The /Operations/<Setup>/Pilot/pilotVORepo option is not defined")

    # DIRAC repo
    if os.path.isdir('pilotLocalRepo'):
      shutil.rmtree('pilotLocalRepo')
    os.mkdir('pilotLocalRepo')
    repo = Repo.init('pilotLocalRepo')
    upstream = repo.create_remote('upstream', self.pilotRepo)
    upstream.fetch()
    upstream.pull(upstream.refs[0].remote_head)
    if repo.tags:
      if self.pilotVORepo:
        localRepo = 'pilotVOLocalRepo'
      else:
        localRepo = 'pilotLocalRepo'
      with open(os.path.join(localRepo, self.projectDir, 'releases.cfg'), 'r') as releasesFile:
        lines = [line.rstrip('\n') for line in releasesFile]
        lines = [s.strip() for s in lines]
        if self.pilotVOVersion in lines:
          self.pilotVersion = lines[(lines.index(self.pilotVOVersion)) + 3].split(':')[1]
      repo.git.checkout(repo.tags[self.pilotVersion], b='pilotScripts')
    else:
      repo.git.checkout('upstream/master', b='pilotScripts')
    try:
      scriptDir = os.path.join('pilotLocalRepo', self.pilotScriptPath, "*.py")
      for filename in glob.glob(scriptDir):
        result = self._upload(filename=os.path.basename(filename),
                              pilotScript=filename)
        if not result['OK']:
          gLogger.error("Error uploading the pilot script: %s" % result['Message'])
        tarFiles.append(filename)
      if not os.path.isfile(os.path.join('pilotLocalRepo',
                                         self.pilotScriptPath,
                                         "dirac-install.py")):
        result = self._upload(filename='dirac-install.py',
                              pilotScript=os.path.join('pilotLocalRepo', "Core/scripts/dirac-install.py"))
        if not result['OK']:
          gLogger.error("Error uploading dirac-install.py: %s" % result['Message'])
        tarFiles.append('dirac-install.py')

      with tarfile.TarFile(name='pilot.tar', mode='w') as tf:
        pwd = os.getcwd()
        for ptf in tarFiles:
          shutil.copyfile(ptf, os.path.join(pwd, os.path.basename(ptf)))
          tf.add(os.path.basename(ptf), recursive=False)

      result = self._upload(filename='pilot.tar',
                            pilotScript='pilot.tar')
      if not result['OK']:
        gLogger.error("Error uploading pilot.tar: %s" % result['Message'])
        return result

    except ValueError:
      gLogger.error("Error uploading the pilot scripts: %s" % result['Message'])
      return result
    return S_OK()

  def _upload(self, pilotDict=None, filename='', pilotScript=''):
    """ Method to upload the pilot json file and the pilot scripts to the server.
        :param pilotDict: used only to upload the pilot.json, which is what it is
        :param filename: remote filename
        :param pilotScript: local path to the file to upload
        :returns: S_OK if the upload was successful, S_ERROR otherwise
    """
    # Note: this method could clearly get a revamp... also the upload is not done in an
    # optimal way since we could send the file with request without reading it in memory,
    # or even send multiple files:
    # http://docs.python-requests.org/en/master/user/advanced/#post-multiple-multipart-encoded-files
    # But well, maybe too much optimization :-)

    if pilotDict:  # this is for the pilot.json file
      if not self.pilotFileServer:
        gLogger.warn("NOT uploading the pilot JSON file, just printing it out")
        print(json.dumps(pilotDict, indent=4, sort_keys=True))  # just print here as formatting is important
        return S_OK()

      data = {'filename': self.jsonFile, 'data': json.dumps(pilotDict)}

    else:  # we assume the method is asked to upload the pilots scripts
      if not self.pilotFileServer:
        gLogger.warn("NOT uploading %s" % filename)
        return S_OK()

      # ALWAYS open binary when sending a file
      with open(pilotScript, "rb") as psf:
        script = psf.read()
      data = {'filename': filename, 'data': script}

    resp = requests.post('https://%s/DIRAC/upload' % self.pilotFileServer,
                         data=data,
                         cert=self.certAndKeyLocation)

    if resp.status_code != 200:
      return S_ERROR(resp.text)
    else:
      gLogger.info('-- File and scripts upload done --')
      return S_OK()
