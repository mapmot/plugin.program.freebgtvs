# -*- coding: utf8 -*-
import os, sys, gzip, urllib.request, urllib.error, urllib.parse

### Basic class to download assets on a give time interval
### If download fails, and the old file doesn't exist
### Use a local file

class Assets:
  interval = 24 #Hours Interval to check for new version of the asset
  
  def __init__(self, temp_dir, url, backup_file, log):
    if os.path.isdir(temp_dir) is False:
      self.create_dir(temp_dir)
    
    if url == '':
      raise ValueError("Valid asset url must be provided!")
    else:
      self.log = log
      self.url = url
      # self.log("Setting DB url %s" % self.url)
      self.file_name = os.path.basename(url)
      self.file = os.path.join(temp_dir, self.file_name)
      self.backup_file = backup_file
      if os.path.isfile(self.file):
        self.first_run = False
    if self.is_expired():
      self.log("DB file is old. Will be updated.")
      self.get_asset()
    else:
      self.log("DB file is new.")
    if self.file.endswith('gz'):
      self.extract()

  def create_dir(self, dir):
    try: os.makedirs(dir)
    except OSError as exc: # Guard against race condition
      if exc.errno != errno.EEXIST:
        raise
        
  def is_expired(self):
    try:
      from datetime import datetime, timedelta
      if os.path.isfile(self.file):
        treshold = datetime.now() - timedelta(hours=self.interval)
        modified = datetime.fromtimestamp(os.path.getmtime(self.file))
        if modified < treshold: #file is more than a day old
          return True
        return False
      else: #file does not exist, perhaps first run
        return True
    except Exception as er:
      self.log(str(er), 4)
      return True

  def get_asset(self):
    try:
      self.log('Downloading assets from url: %s' % self.url)
      f = urllib.request.urlopen(self.url)
      with open(self.file, "wb") as code:
        code.write(f.read())
        self.log("Saved in %s" % self.file)
      self.log('Assets file downloaded')
    except:
      self.handle_ex()
      
  def extract(self):
    try:
      gz = gzip.GzipFile(self.file, 'rb')
      s = gz.read()
      gz.close()
      self.file = self.file.replace('.gz', '')
      with file(self.file, 'wb') as out:
        out.write(s)
    except:
      self.handle_ex()
      
  def handle_ex(self):
    import traceback
    type, errstr = sys.exc_info()[:2]
    self.log('Unable to download assets file!\n' + str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]) + ''.join(traceback.format_stack()), 4)
    if not os.path.isfile(self.file) and os.path.isfile(self.backup_file): #if asset was never downloaded and backup exists
      self.file = self.backup_file