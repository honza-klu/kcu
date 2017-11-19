import network
try:
  import urequests
except:
  print("Can't import urequests")

#import auto_connect;auto_connect.auto_connect()
cred = {"dd-wrt": "KockaLezeDirouPesOknem", "dobeso": "cestASila", "Lenovo P1ma40": "armada123"}

def auto_connect():
  sta_if = network.WLAN(network.STA_IF)
  sta_if.active(True)
  scanned_ap = sta_if.scan()
  found = False
  for ap in scanned_ap:
    print("checking %s" % (ap[0]))
    if(ap[0].decode('ascii') in cred):
      found = ap[0].decode('ascii')
      print("Known AP found %s %s" % (found, cred[found]))
      break
  if(found):
    sta_if.connect(found, cred[found])
    sta_if.isconnected()
  else:
    print("No AP found!")

def con_test():
  if not 'urequests' in locals():
    return None
  try:
    response = urequests.get('http://klusacek.tk')
    pass
  except Exception:
    return False
  return True
