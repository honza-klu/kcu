# This file is executed on every boot (including wake-boot from deepsleep)
try:
  print("BOOT START")
  import machine
  import time
  import auto_connect
  import uftpserver
  import _thread
  
  auto_connect.auto_connect()
  time.sleep(5)
  auto_connect.auto_connect()
  #if(auto_connect.con_test()):
  #  print("WIFI OK")
  #else:
#    print("WIFI KO!")
  
  def ftp_thread_entry(parm):
    print("STARTING FTP")
    uftpserver.run_ftp()
    print("FTP TERMINATED")
  ftp_thread = _thread.start_new_thread(ftp_thread_entry, (None,))
except Exception as e:
  print("Unhandled exception:%s" % (str(e),))
  print("Boot encountered. Restarting in 10s")
  time.sleep(10.0)
  print("Restarting now!")
  machine.reset()
print("BOOT END")