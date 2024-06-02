import socket
import cv2
import threading
 
 
def send_video(client_socket, stop_event):
   cap = cv2.VideoCapture(0)
   try:
       while not stop_event.is_set():
           ret, frame = cap.read()
           if not ret:
               break
 
 
           _, frame_encoded = cv2.imencode('.jpg', frame)
           frame_data = frame_encoded.tobytes()
 
 
           length = len(frame_data)
           client_socket.sendall(length.to_bytes(4, byteorder='big') + frame_data)
   except Exception as e:
       print(f"Error sending video: {e}")
   finally:
       cap.release()
 
 
def client_program():
   host = '127.0.0.1'  # Replace with the server's IP address
   port = 65432
 
 
   client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
       client_socket.connect((host, port))
       print("Connected to server. Waiting for commands...")
 
 
       stop_event = threading.Event()
       video_thread = None
 
 
       while True:
           try:
               command = client_socket.recv(1024).decode()
               if command == 'start':
                   stop_event.clear()
                   video_thread = threading.Thread(target=send_video, args=(client_socket, stop_event))
                   video_thread.start()
               elif command == 'stop':
                   stop_event.set()
                   if video_thread and video_thread.is_alive():
                       video_thread.join()
               elif command == 'quit':
                   stop_event.set()
                   if video_thread and video_thread.is_alive():
                       video_thread.join()
                   break
           except Exception as e:
               print(f"Error receiving command: {e}")
               break
   except Exception as e:
       print(f"Connection error: {e}")
   finally:
       client_socket.close()
 
 
if __name__ == "__main__":
   client_program()
