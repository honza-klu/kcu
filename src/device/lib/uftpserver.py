import usocket as socket
import network
import os

DATA_PORT = 13333

ftpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
datasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ftpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
datasocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ftpsocket.bind(socket.getaddrinfo("0.0.0.0", 21)[0][4])
datasocket.bind(socket.getaddrinfo("0.0.0.0", DATA_PORT)[0][4])

ftpsocket.listen(1)
datasocket.listen(1)
#datasocket.settimeout(10)

dataclient = None

def remove_dots(path):
    """This function removes .. parts (and preceding dir) from paths"""
    if path == "":
      return ""
    if path == "/":
      return "/"
    parts = path.split("/")
    for idx in range(len(parts)):
        if parts[idx] == "..":
          parts[idx] = None
          #search for previous not deleted part and remove it
          for i in reversed(range(idx)):
              if parts[i] != None:
                parts[i] = None
                break
          else:
            raise Exception("Invalid path %s" % (path))
    parts = [part for part in parts if part!=None and part!=""]
    out = "/".join(parts)
    if path[0] == "/":
        out = "/" + out
    if path[-1] == "/":
        out = out + "/"
    if len(parts) == 0:
      return "/" if path[0]=="/" else ""
    return out

#print(remove_dots("/"))
#print(remove_dots(""))
#print(remove_dots("/a/../"))
#print(remove_dots("b/../"))
#print(remove_dots("/a/b/../"))
#print(remove_dots("a/b/../"))
#print(remove_dots("a/b/.."))
#print(remove_dots("a/b/../../"))
#print(remove_dots("a/b/../../.."))

def send_list_data(cwd, dataclient):
    for file in os.listdir(cwd):
        stat = os.stat(get_absolute_path(cwd, file))
        file_permissions = "drwxr-xr-x" if (stat[0] & 0o170000 == 0o040000) else "-rw-r--r--"
        file_size = stat[6]
        description = "{}    1 owner group {:>13} Jan 1  1980 {}\r\n".format(file_permissions, file_size, file)
        dataclient.sendall(description)
        
def send_file_data(path, dataclient):
    with open(path) as file:
        chunk = file.read(128)
        while len(chunk) > 0:
            dataclient.sendall(chunk)
            chunk = file.read(128)

def save_file_data(path, dataclient):
    with open(path, "w") as file:
        print("Start receiving")
        chunk = dataclient.recv(128)
        print("Read first part:")
        while len(chunk) > 0:
            print("Write to file")
            file.write(chunk)
            print("Receive more")
            chunk = dataclient.recv(128)
            print("Read again")
        print("Received all")
    with open(path, "r") as file:
        print(file.read())

def get_absolute_path(cwd, payload):
    # if it doesn't start with / consider
    # it a relative path
    if not payload.startswith("/"):
        payload = cwd.rstrip("/") + "/" + payload
    # and don't leave any trailing / except for single /
    return payload.rstrip("/") if payload != "/" else "/"

def run_ftp():
    try:
        dataclient = None
        while True:
            cwd = "/"
            print("Wait for connection:")
            cl, remote_addr = ftpsocket.accept()
            cl.settimeout(300)
            try:
                print("FTP connection from:", remote_addr)
                cl.sendall("220 Hello, this is the ESP8266.\r\n")
                while True:
                    data = cl.readline().decode("utf-8").replace("\r\n", "")
                    if len(data) <= 0:
                        print("Client is dead")
                        break
                    
                    command, payload =  (data.split(" ") + [""])[:2]
                    command = command.upper()
                    
                    print("Command={}, Payload={}".format(command, payload))
                    
                    if command == "USER":
                        cl.sendall("230 Logged in.\r\n")
                    elif command == "SYST":
                        cl.sendall("215 ESP8266 MicroPython\r\n")
                    elif command == "SYST":
                        cl.sendall("502\r\n")
                    elif command == "PWD":
                        cl.sendall('257 "{}"\r\n'.format(cwd))
                    elif command == "CWD":
                        path = remove_dots(get_absolute_path(cwd, payload))
                        try:
                            files = os.listdir(path)
                            try:
                                cwd = os.path.normpat(path)
                            except:
                                print("cwd = os.path.normpat(path) failed! Using fallback")
                                cwd = path
                            cl.sendall('250 Directory changed successfully\r\n')
                        except:
                            cl.sendall('550 Failed to change directory\r\n')
                    elif command == "EPSV":
                        cl.sendall('502\r\n')
                    elif command == "TYPE":
                        # probably should switch between binary and not
                        cl.sendall('200 Transfer mode set\r\n')
                    elif command == "SIZE":
                        path = get_absolute_path(cwd, payload)
                        try:
                            size = os.stat(path)[6]
                            cl.sendall('213 {}\r\n'.format(size))
                        except:
                            cl.sendall('550 Could not get file size\r\n')
                    elif command == "QUIT":
                        cl.sendall('221 Bye.\r\n')
                    elif command == "PASV":
                        addr = network.WLAN().ifconfig()[0]
                        cl.sendall('227 Entering Passive Mode ({},{},{}).\r\n'.format(addr.replace('.',','), DATA_PORT>>8, DATA_PORT%256))
                        dataclient, data_addr = datasocket.accept()
                        print("FTP Data connection from:", data_addr)
                    elif command == "LIST":
                        try:
                            send_list_data(cwd, dataclient)
                            dataclient.close()
                            cl.sendall("150 Here comes the directory listing.\r\n")
                            cl.sendall("226 Listed.\r\n")
                        except:
                            cl.sendall('550 Failed to list directory\r\n')
                        finally:
                            dataclient.close()
                    elif command == "RETR":
                        try:
                            send_file_data(get_absolute_path(cwd, payload), dataclient)
                            dataclient.close()
                            cl.sendall("150 Opening data connection.\r\n")
                            cl.sendall("226 Transfer complete.\r\n")
                        except:
                            cl.sendall('550 Failed to send file\r\n')
                        finally:
                            dataclient.close()
                    elif command == "STOR":
                        try:
                            cl.sendall("150 Ok to send data.\r\n")
                            print("START DATA RECEIVE")
                            save_file_data(get_absolute_path(cwd, payload), dataclient)
                            print("DATA RECEIVED")
                            dataclient.close()
                            print("Data connection closed")
                            cl.sendall("226 Transfer complete.\r\n")
                        except:
                            cl.sendall('550 Failed to send file\r\n')
                        finally:
                            dataclient.close()
                    elif command == "DELE":
                        try:
                            os.remove(get_absolute_path(cwd, payload))
                            cl.sendall("250 Requested file deleted okay, completed.\r\n") #250 #450, 550 #500, 501, 502, 421, 530
                        except:
                            cl.sendall("550 Requested file deleted failed, completed.\r\n") #250 #450, 550 #500, 501, 502, 421, 530
##                        finally:
##                            dataclient.close()
                    elif command == "MKD":
                        try:
                            os.mkdir(get_absolute_path(cwd, payload))
                            cl.sendall("257 Requested directory created okay, completed.\r\n")
                        except:
                            cl.sendall("550 Requested directory creation failed, completed.\r\n")
#                        finaly()
                    elif command == "RMD":
                        try:
                            os.rmdir(get_absolute_path(cwd, payload))
                            cl.sendall("250 Requested directory deleted okay, completed.\r\n") #250 #450, 550 #500, 501, 502, 421, 530
                        except:
                            cl.sendall("550 Requested directory deleted failed, completed.\r\n") #250 #450, 550 #500, 501, 502, 421, 530
##                        finally:
##                            dataclient.close()
                    else:
                        cl.sendall("502 Unsupported command.\r\n")
                        print("Unsupported command {} with payload {}".format(command, payload))
                        
            finally:
                cl.close()
    finally:
        datasocket.close()
        ftpsocket.close()
        if dataclient is not None:
            dataclient.close()