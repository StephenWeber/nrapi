from os.path import isfile, join

class FileCache:
  def __init__(self, path):
    self.path = path

  def get(self, name):
    filename = join(self.path, name)
    if isfile(filename):
      with open(filename, 'r') as fp:
        data = fp.read()
        return data
    return None

  def set(self, name, data):
    filename = join(self.path, name)
    if isfile(filename):
      with open(filename, 'w') as fp:
        fp.write(data)
