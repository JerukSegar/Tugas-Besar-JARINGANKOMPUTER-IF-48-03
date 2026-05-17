import socket
import threading

SERVER_HOST = 'localhost'
SERVER_PORT_TCP = 8000
SERVER_PORT_UDP = 9000
PROXY_HOST = ''
PROXY_PORT = 8080

cache_penyimpanan = {}

def tangani_klien_tcp(soket_klien, alamat_klien):
    try:
        permintaan = soket_klien.recv(4096)
        if not permintaan:
            return
            
        teks_permintaan = permintaan.decode('utf-8', errors='ignore')
        baris_pertama = teks_permintaan.split('\r\n')[0]
        print(f"[Proxy] Menerima request dari client: {baris_pertama}")
        
        bagian = baris_pertama.split()
        if len(bagian) >= 2:
            nama_file = bagian[1]
            
            if nama_file in cache_penyimpanan:
                print("[Proxy] [Cache HIT] Berkas ditemukan di cache lokal. Mengirim langsung ke client.")
                soket_klien.sendall(cache_penyimpanan[nama_file])
            else:
                print("[Proxy] [Cache MISS] Berkas tidak ditemukan di cache lokal.")
                print(f"[Proxy] Menghubungi Web Server di ('{SERVER_HOST}', {SERVER_PORT_TCP})...")
                
                soket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soket_server.connect((SERVER_HOST, SERVER_PORT_TCP))
                soket_server.sendall(permintaan)
                
                data_balasan = b""
                while True:
                    data = soket_server.recv(4096)
                    if len(data) > 0:
                        data_balasan += data
                    else:
                        break
                
                if len(data_balasan) > 0:
                    print("[Proxy] Menerima data dari Web Server (200 OK). Menyimpan ke cache.")
                    cache_penyimpanan[nama_file] = data_balasan
                    print("[Proxy] Meneruskan respons ke client.")
                    soket_klien.sendall(data_balasan)
                
                soket_server.close()
    except Exception:
        pass
    finally:
        soket_klien.close()

def jalankan_proxy_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(5)
    
    while True:
        try:
            soket_klien, alamat_klien = server.accept()
            utas = threading.Thread(target=tangani_klien_tcp, args=(soket_klien, alamat_klien))
            utas.daemon = True
            utas.start()
        except Exception:
            break

def jalankan_proxy_udp():
    soket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soket_udp.bind((PROXY_HOST, PROXY_PORT))
    soket_server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        try:
            data, alamat_klien = soket_udp.recvfrom(4096)
            print(f"[UDP Proxy] Meneruskan paket dari client {alamat_klien} ke Server ('{SERVER_HOST}', {SERVER_PORT_UDP})")
            soket_server_udp.sendto(data, (SERVER_HOST, SERVER_PORT_UDP))
            
            soket_server_udp.settimeout(2.0)
            try:
                data_balasan, alamat_server = soket_server_udp.recvfrom(4096)
                print(f"[UDP Proxy] Meneruskan kembali respons server ke client {alamat_klien}")
                soket_udp.sendto(data_balasan, alamat_klien)
            except socket.timeout:
                pass
        except Exception:
            break

if __name__ == '__main__':
    print("Proxy Server sedang berjalan di port 8080...")
    utas_tcp = threading.Thread(target=jalankan_proxy_tcp)
    utas_udp = threading.Thread(target=jalankan_proxy_udp)
    utas_tcp.daemon = True
    utas_udp.daemon = True
    utas_tcp.start()
    utas_udp.start()
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProxy dihentikan.")