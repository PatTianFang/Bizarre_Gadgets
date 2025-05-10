def ping_ip(ip):
    import os
    response = os.system(f"ping -n 1 {ip} >nul 2>&1")
    return response == 0

def ping_range(start_ip, end_ip):
    reachable_ips = []
    start = list(map(int, start_ip.split('.')))
    end = list(map(int, end_ip.split('.')))
    
    for i in range(start[2], end[2] + 1):
        for j in range(start[3], end[3] + 1):
            ip = f"{start[0]}.{start[1]}.{i}.{j}"
            if ping_ip(ip):
                reachable_ips.append(ip)
    
    return reachable_ips