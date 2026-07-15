import socket
import os
import struct
import time
import sys
import subprocess
import threading
from collections import defaultdict

# Terminal Colors (ANSI escape codes)
RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
B_RED = '\033[41m\033[97m' # Background Red, White Text
RESET = '\033[0m'

# Traffic tracker & Process Mapper
ip_packet_count = defaultdict(int)
ALERT_THRESHOLD = 50 
port_to_process_map = {}

def fetch_system_process_mapping():
    """Background thread that maps local ports to active Application Names using native OS tools."""
    global port_to_process_map
    while True:
        try:
            pid_to_name = {}
            # 1. Get all running processes and their PIDs
            task_out = subprocess.check_output('tasklist /fo csv /nh', shell=True, text=True, errors='ignore')
            for line in task_out.strip().split('\n'):
                if ',' in line:
                    parts = line.replace('"', '').split(',')
                    if len(parts) >= 2:
                        pid_to_name[parts[1].strip()] = parts[0].strip()

            # 2. Get active network connections and map local ports to Process Names
            net_out = subprocess.check_output('netstat -ano', shell=True, text=True, errors='ignore')
            temp_map = {}
            for line in net_out.split('\n'):
                parts = line.split()
                if len(parts) >= 4:
                    proto = parts[0]
                    local_addr = parts[1]
                    pid = parts[-1]
                    if proto in ['TCP', 'UDP'] and ':' in local_addr:
                        port = local_addr.split(':')[-1]
                        if pid in pid_to_name:
                            temp_map[port] = pid_to_name[pid]
            
            port_to_process_map = temp_map
        except Exception:
            pass
        time.sleep(1.5) # Refresh mapping every 1.5 seconds in background

def show_loading_animation():
    """Displays a spinning loading icon in the middle while initializing the backend."""
    animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    print("\n\n")
    for i in range(25):
        time.sleep(0.08)
        current_char = animation_chars[i % len(animation_chars)]
        sys.stdout.write(f"\r\t\t{YELLOW}[{current_char}] Hooking Process Tables & Resolving Application Port Bindings...{RESET}")
        sys.stdout.flush()
    
    # Completely clear the loading icon line once successfully loaded so it becomes invisible
    sys.stdout.write("\r" + " " * 95 + "\r") 
    print(f"\t\t{GREEN}[✓] App-Layer Telemetry Radar Online & Protected!{RESET}\n")
    time.sleep(0.5)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CYAN}{'='*105}\n     HYBRID CYBER-DEFENSE ENGINE v5.0 (PROCESS-LEVEL APPLICATION PACKET RADAR)\n{'='*105}{RESET}")
    
    # Start the background process mapper thread before animation so it's ready
    if os.name == 'nt':
        threading.Thread(target=fetch_system_process_mapping, daemon=True).start()
        
    show_loading_animation()

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    last_reset_time = time.time()
    
    try:
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sniffer.bind((local_ip, 0))
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        
        # New Expanded UI Grid Header with Application tracking
        print(f"{CYAN}{'APPLICATION/TOOL':<20} | {'SOURCE IP:PORT':<23} -> {'DESTINATION IP:PORT':<23} | {'PROTO':<6} | {'STATUS'}{RESET}")
        print("-" * 105)

        while True:
            current_time = time.time()
            if current_time - last_reset_time >= 1.0:
                ip_packet_count.clear()
                last_reset_time = current_time

            raw_buffer = sniffer.recvfrom(65565)[0]
            
            # Unpack IP Header
            ip_header = raw_buffer[0:20]
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            
            protocol_type = iph[6]
            s_addr = socket.inet_ntoa(iph[8])
            d_addr = socket.inet_ntoa(iph[9])
            
            source_port = ""
            dest_port = ""
            proto_name = "UNK"
            
            # Extract Protocol and Ports
            if protocol_type == 1:
                proto_name = "ICMP"
            elif protocol_type == 2:
                proto_name = "IGMP"
            elif protocol_type == 6:
                proto_name = "TCP"
                tcp_header = raw_buffer[20:24]
                if len(tcp_header) == 4:
                    source_port, dest_port = struct.unpack('!HH', tcp_header)
            elif protocol_type == 17:
                proto_name = "UDP"
                udp_header = raw_buffer[20:24]
                if len(udp_header) == 4:
                    source_port, dest_port = struct.unpack('!HH', udp_header)

            # Core Logic: Identify which app is responsible by checking local bound ports
            app_name = "System/Network"
            if os.name == 'nt':
                str_src_port = str(source_port)
                str_dst_port = str(dest_port)
                
                if s_addr == local_ip and str_src_port in port_to_process_map:
                    app_name = port_to_process_map[str_src_port]
                elif d_addr == local_ip and str_dst_port in port_to_process_map:
                    app_name = port_to_process_map[str_dst_port]

            src_display = f"{s_addr}:{source_port}" if source_port else s_addr
            dst_display = f"{d_addr}:{dest_port}" if dest_port else d_addr
            
            # Smart Color formatting for popular tools
            app_color = PURPLE if app_name != "System/Network" else RESET
            app_display = f"{app_color}{app_name}{RESET}"

            ip_packet_count[s_addr] += 1
            current_rate = ip_packet_count[s_addr]
            
            if current_rate > ALERT_THRESHOLD:
                status = f"{B_RED}[ALERT] Flood ({current_rate} P/s){RESET}"
            else:
                status = f"{GREEN}Normal ({current_rate} P/s){RESET}"
            
            print(f"{app_display:<29} | {src_display:<23} -> {dst_display:<23} | {proto_name:<6} | {status}")
            
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Engine stopped securely by operator.{RESET}")
    except PermissionError:
        print(f"\n{RED}[!] Error: Run as Administrator!{RESET}")
    finally:
        if os.name == 'nt' and 'sniffer' in locals():
            try:
                sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            except:
                pass

if __name__ == "__main__":
    main()