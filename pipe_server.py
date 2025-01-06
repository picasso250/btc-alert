import win32pipe
import win32file
import pywintypes

def pipe_server():
    pipe_name = r'\\.\pipe\test_pipe'
    
    try:
        print("Creating named pipe...")
        pipe = win32pipe.CreateNamedPipe(
            pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536, 0, None)
        
        print("Waiting for client to connect...")
        win32pipe.ConnectNamedPipe(pipe, None)
        
        while True:
            print("Waiting for message...")
            result, data = win32file.ReadFile(pipe, 65536)
            if result == 0:
                message = data.decode('utf-8')
                print(f"Received: {message}")
                
                # Send response
                response = f"Python received: {message}"
                win32file.WriteFile(pipe, response.encode('utf-8'))
                
                if message.lower() == "exit":
                    break
        
        print("Closing pipe")
        win32file.CloseHandle(pipe)
        
    except pywintypes.error as e:
        print(f"Error: {e}")
        if pipe:
            win32file.CloseHandle(pipe)

if __name__ == '__main__':
    pipe_server()
