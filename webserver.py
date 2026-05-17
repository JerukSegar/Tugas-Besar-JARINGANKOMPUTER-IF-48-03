import os
import socket
import threading

FOLDER_KONTEN = 'HTML'

def handle_tcp_client(client_socket, client_address):
  print(f"[TCP Server] Menerima koneksi dari {client_address}")
  try:
    request_data = client_socket.recv(4096).decode("utf-8", errors="ignore")
    if not request_data:
      return

    lines = request_data.split("\r\n")
    if len(lines) > 0 and lines[0]:
      request_line = lines[0]
      print(f"[TCP Server] Request: {request_line}")

      parts = request_line.split()
      if len(parts) >= 2:
        method = parts[0]
        filename = parts[1]

        if filename == "/":
          filename = "/index.html"

        filepath = os.path.join(FOLDER_KONTEN, filename.lstrip("/"))

        if os.path.exists(filepath) and os.path.isfile(filepath):
          ext = os.path.splitext(filepath)[1].lower()
          content_type = "text/html"
          if ext == ".css":
            content_type = "text/css"
          elif ext == ".js":
            content_type = "application/javascript"
          elif ext == ".png":
            content_type = "image/png"
          elif ext == ".jpg" or ext == ".jpeg":
            content_type = "image/jpeg"
          elif ext == ".gif":
            content_type = "image/gif"

          with open(filepath, "rb") as f:
            content = f.read()

          response_line = "HTTP/1.1 200 OK\r\n"
          header = f"Content-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n"
          client_socket.sendall(response_line.encode("utf-8") + header.encode("utf-8") + content)
          print(f"[TCP Server] Mengirimkan file: {filepath} (200 OK)")
        else:
          error_body = "<html><body><h1>404 Not Found</h1></body></html>"
          content = error_body.encode("utf-8")
          response_line = "HTTP/1.1 404 Not Found\r\n"
          header = f"Content-Type: text/html\r\nContent-Length: {len(content)}\r\n\r\n"
          client_socket.sendall(response_line.encode("utf-8") + header.encode("utf-8") + content)
          print(
              f"[TCP Server] File tidak ditemukan: {filepath} (404 Not Found)"
          )
  except Exception:
    pass
  finally:
    client_socket.close()


def run_tcp_server():
  tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  tcp_socket.bind(("", 8000))
  tcp_socket.listen(5)

  while True:
    try:
      client_socket, client_address = tcp_socket.accept()
      client_thread = threading.Thread(
          target=handle_tcp_client, args=(client_socket, client_address)
      )
      client_thread.daemon = True
      client_thread.start()
    except Exception:
      break


def run_udp_server():
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udp_socket.bind(("", 9000))

  while True:
    try:
      data, address = udp_socket.recvfrom(4096)
      decoded_msg = data.decode("utf-8", errors="ignore")
      print(f'[UDP Server] Menerima paket dari {address}: "{decoded_msg}"')
      udp_socket.sendto(data, address)
      print(f"[UDP Server] Memantulkan kembali paket ke {address}")
    except Exception:
      break


if __name__ == "__main__":
  print("Web Server (Port 8000 & Port 9000) sedang berjalan...")

  tcp_thread = threading.Thread(target=run_tcp_server)
  udp_thread = threading.Thread(target=run_udp_server)

  tcp_thread.daemon = True
  udp_thread.daemon = True

  tcp_thread.start()
  udp_thread.start()

  try:
    import time

    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print("\nServer dihentikan.")