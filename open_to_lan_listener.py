import socket
import subprocess
import re
import time

MINECRAFT_PORT=25565

# Minecraft multi-cast address and port
MCAST_ADDR = "224.0.2.60"
MCAST_PORT = 4445

# Socket polling timeout
POLL_TIMEOUT_SEC = 5

ANY = "0.0.0.0"

class OpenToLanListener:
    def __init__(self, addr):
        self.addr = addr
        self.local_addr = None
        self.current_port = None
        self.sock = None
        self.is_running = False
        self.request_shutdown = False

    def setup(self):
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Allow multiple sockets to use the same PORT number
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to the port that we know will receive multicast data
        self.sock.bind((ANY,MCAST_PORT))

        # Tell the kernel that we want to add ourselves to a multicast group
        # The address for the multicast group is the third param
        self.sock.setsockopt(socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton(MCAST_ADDR) + socket.inet_aton(self.addr))

        self.sock.settimeout(POLL_TIMEOUT_SEC)

    def shutdown(self):
        print("Open to lan listener: Shutting down")

        # Signal that we are requesting shutdown
        self.request_shutdown = True

        # Wait for shutdown
        max_wait = POLL_TIMEOUT_SEC
        start_time = time.time()
        while self.is_running and (time.time() - start_time) < max_wait:
            time.sleep(0.1)

        if (self.is_running):
            print("Timed out waiting to shutdown")
        else:
            print("Shut down")

    def run(self, status_callback):
        self.is_running = True
        while True:
            # Break out if shutdown is requested
            if (self.request_shutdown):
                print("Shutdown requested")
                break

            try:
                # Poll socket
                data, addr = self.sock.recvfrom(1024)
            except socket.timeout as e:
                self.__delete_port_proxy()
                status_callback("Not connected", False)
                pass
            except socket.error as e:
                print("Error: %s" % (e))
                self.__delete_port_proxy()
                status_callback("Error: %s" % (e), False)
            else:
                str_data = data.decode('utf-8')
                local_addr = addr[0]
                print("Received %s: %s" % (local_addr, str_data))

                # Data is a string of the form
                #  [MOTD]Player - Demo World[/MOTD][AD]port#[/AD]
                match = re.search('\[AD\](\d+?)\[/AD\]', str_data)

                if match:
                    new_port = match.group(1)
                    if (new_port != self.current_port):
                        # Map port proxy via netsh command
                        cmd = "netsh interface portproxy set v4tov4 listenport=%s listenaddress=%s connectport=%s connectaddress=%s" % (MINECRAFT_PORT, local_addr, new_port, local_addr)
                        try:
                            p = subprocess.run(cmd, shell=True, check=True, capture_output=True)
                        except subprocess.CalledProcessError as err:
                            print("Error executing command %s: %s" % (cmd, err))
                            self.__delete_port_proxy()
                            if ("Run as administrator" in str(err.output)):
                                status_callback("Error: Restart app as administrator", False)
                            else:
                                status_callback("Error: netsh returned code %d"  % (err.returncode), False)
                        else:
                            self.local_addr = local_addr
                            self.current_port = new_port
                            print("Found new open to lan on port: %s" % (self.current_port))
                            status_callback("Mapping port: %s" % (self.current_port), True)
                    else:
                        print("Open to lan on port: %s" % (self.current_port))
        self.__delete_port_proxy()
        self.is_running = False
    
    def __delete_port_proxy(self):
        # Clean up port proxy entry
        if (self.local_addr is not None):
            cmd = "netsh interface portproxy delete v4tov4 listenport=%s listenaddress=%s" % (MINECRAFT_PORT, self.local_addr)

            try:
                p = subprocess.run(cmd, shell=True, check=True, capture_output=True)
                print("Deleted port proxy")
            except subprocess.CalledProcessError as err:
                print("Error executing command %s: %s" % (cmd, err))
        self.local_addr = None
        self.current_port = None
