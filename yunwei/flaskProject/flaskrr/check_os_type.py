import socket

def check_ssh_port(ip,port):
  try:
    with socket.create_connection((ip,port),timeout=1) as sock:
     #print(f"Connection to {ip}{port} port succeeded~")
      return True
  except Exception as e:
    print(f"Connection to {ip} {port} port failed!: {e}")
    return False
def check_os_type(ip):
  if check_ssh_port(ip,22):
     #print(f"{ip} is likely to be a linux machine.")
     template_id="10001"
  else:
     #print(f"{ip} may be a Windows machine.")
     template_id = "10081"

  return template_id
