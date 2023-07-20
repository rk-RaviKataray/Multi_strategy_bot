from UltraDict import UltraDict
other = UltraDict(recurse = True, name='ravi_',create=False,auto_unlink=False)
other['nested']['counter'] += 1

print(other)

#secret!!!!!!!!!!!!!