import socket
import cv2
import numpy as np
import threading
 
 
def receive_video(conn, video_writer, stop_event):
   while not stop_event.is_set():
       try:
           data = conn.recv(4)
           if not data:
               break
 
 
           length = int.from_bytes(data, byteorder='big')
           frame_data = b""
           while len(frame_data) < length:
               packet = conn.recv(length - len(frame_data))
               if not packet:
                   break
               frame_data += packet
 
 
           if len(frame_data) != length:
               break
 
 
           frame = np.frombuffer(frame_data, dtype=np.uint8)
           frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
           if frame is None:
               break
 
 
           video_writer.write(frame)
 
 
           cv2.imshow('Receiving Video', frame)
           if cv2.waitKey(1) & 0xFF == ord('q'):
               break
       except Exception as e:
           print(f"Error receiving video: {e}")
           break
 
 
   if video_writer:
       video_writer.release()
   cv2.destroyAllWindows()
 
 
def server_program():
   host = '127.0.0.1'
   port = 65432
 
 
   server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server_socket.bind((host, port))
   server_socket.listen(1)
 
 
   print(f"Server listening on {host}:{port}")
   conn, addr = server_socket.accept()
   print(f"Connected by {addr}")
 
 
   video_writer = None
   stop_event = threading.Event()
   video_thread = None
 
 
   try:
       while True:
           command = input("Enter command (start/stop/quit): ").strip().lower()
           if command in ('start', 'stop', 'quit'):
               conn.send(command.encode())
               if command == 'start':
                   if video_writer is None:
                       video_writer = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
                   stop_event.clear()
                   video_thread = threading.Thread(target=receive_video, args=(conn, video_writer, stop_event))
                   video_thread.start()
               elif command == 'stop':
                   stop_event.set()
                   if video_thread and video_thread.is_alive():
                       video_thread.join()
                   video_writer = None  # Reset video_writer to create a new file on next start command
               elif command == 'quit':
                   stop_event.set()
                   if video_thread and video_thread.is_alive():
                       video_thread.join()
                   break
   except Exception as e:
       print(f"Error: {e}")
   finally:
       if video_writer:
           video_writer.release()
       conn.close()
       server_socket.close()
       cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
   server_program()
