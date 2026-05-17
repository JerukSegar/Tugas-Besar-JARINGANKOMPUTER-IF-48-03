import socket
import time

PROXY_HOST = 'localhost'
PROXY_PORT = 8080

def jalankan_klien_http():
    nama_file = input("Masukkan nama file yang ingin diminta (contoh: /index.html): ")
    if not nama_file.startswith('/'):
        nama_file = '/' + nama_file
        
    soket_klien = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soket_klien.connect((PROXY_HOST, PROXY_PORT))
    
    permintaan = f"GET {nama_file} HTTP/1.1\r\nHost: {PROXY_HOST}\r\n\r\n"
    soket_klien.sendall(permintaan.encode('utf-8'))
    
    data_balasan = b""
    while True:
        data = soket_klien.recv(4096)
        if len(data) > 0:
            data_balasan += data
        else:
            break
            
    print("\nRespons dari server:")
    print(data_balasan.decode('utf-8', errors='ignore'))
    soket_klien.close()

def jalankan_klien_udp():
    jumlah_paket = int(input("Masukkan jumlah paket ping: "))
    soket_klien = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soket_klien.settimeout(1.0)
    
    daftar_waktu = []
    paket_hilang = 0
    
    for i in range(1, jumlah_paket + 1):
        pesan = f"Ping Paket-{i}"
        waktu_mulai = time.time()
        soket_klien.sendto(pesan.encode('utf-8'), (PROXY_HOST, PROXY_PORT))
        
        try:
            data, alamat = soket_klien.recvfrom(4096)
            waktu_selesai = time.time()
            waktu_tempuh = (waktu_selesai - waktu_mulai) * 1000
            daftar_waktu.append(waktu_tempuh)
            print(f"Balasan dari {alamat}: {data.decode('utf-8')} waktu={waktu_tempuh:.2f} ms")
        except socket.timeout:
            paket_hilang += 1
            print(f"Request timeout untuk paket {i}")
            
    soket_klien.close()
    
    print("\nStatistik Ping:")
    if len(daftar_waktu) > 0:
        waktu_minimal = min(daftar_waktu)
        waktu_maksimal = max(daftar_waktu)
        waktu_rata_rata = sum(daftar_waktu) / len(daftar_waktu)
        
        variasi_waktu = 0
        if len(daftar_waktu) > 1:
            selisih_waktu = [abs(daftar_waktu[j] - daftar_waktu[j-1]) for j in range(1, len(daftar_waktu))]
            variasi_waktu = sum(selisih_waktu) / len(selisih_waktu)
            
        print(f"Minimum RTT: {waktu_minimal:.2f} ms")
        print(f"Maximum RTT: {waktu_maksimal:.2f} ms")
        print(f"Average RTT: {waktu_rata_rata:.2f} ms")
        print(f"Jitter: {variasi_waktu:.2f} ms")
    else:
        print("Tidak ada paket yang berhasil diterima.")
        
    persentase_hilang = (paket_hilang / jumlah_paket) * 100
    print(f"Packet Loss: {persentase_hilang:.1f}%")

if __name__ == '__main__':
    print("Pilih mode:")
    print("1. HTTP Client (TCP)")
    print("2. UDP Pinger (Penguji Kualitas Jaringan)")
    pilihan = input("Masukkan pilihan (1/2): ")
    
    if pilihan == '1':
        jalankan_klien_http()
    elif pilihan == '2':
        jalankan_klien_udp()