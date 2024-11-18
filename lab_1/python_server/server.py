import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Type
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psycopg2
import os
import time

DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ.get('DB_NAME', 'mydatabase')
DB_USER = os.environ.get('DB_USER', 'myuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mypassword')

def connect_to_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Połączono z bazą danych")
            return conn
        except psycopg2.OperationalError:
            print("Błąd połączenia z bazą danych, ponawianie za 5 sekund...")
            time.sleep(5)

conn = connect_to_db()
cursor = conn.cursor()

class SimpleRequestHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
       
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    #retrieving data from server
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        users = [dict(zip(column_names,row)) for row in rows]
        self.wfile.write(json.dumps(users).encode())
        conn.commit()


    #sending data to server
    def do_POST(self) -> None:
        content_length: int = int(self.headers['Content-Length'])
        post_data: bytes = self.rfile.read(content_length)
        received_data: dict = json.loads(post_data.decode())
        first_name = received_data.get("first_name")
        last_name = received_data.get("last_name")
        role = received_data.get("role")
        
        cursor.execute("INSERT INTO users(first_name, last_name, role) VALUES(%s,%s,%s)", (first_name,last_name,role))
        conn.commit()
        response: dict = {
            "message": "Item adder successfuly",
            "username": first_name  #zrobic tak aby wyswietlalo wszystkie dane uzytkownika
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    #deleting data from
    def do_DELETE(self) -> None:
        user_id = self.path.split('/')[-1]  


        cursor.execute('SELECT * FROM users where id = %s', (user_id,))
        rows = cursor.fetchall()
        
        if(len(rows) != 0):
            cursor.execute('DELETE from users where id = %s', (user_id,))
            response = {
                "message": f"User with ID {user_id} was deleted",
                #"deleted_item": user_to_delete,
                #"updated_list": self.user_list
            }
            self.send_response(200)
        else:
            response = {
                "message": "User not found. Operation failed",
                #"current_list": self.user_list
            }
            self.send_response(400)

        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


def run(
        server_class: Type[HTTPServer] = HTTPServer,
        handler_class: Type[BaseHTTPRequestHandler] = SimpleRequestHandler,
        port: int = 8000
) -> None:
    # Define the server address.
    # '' means it will bind to all available network interfaces on the machine, and the port is specified.
    server_address: tuple = ('', port)

    # Create an instance of HTTPServer with the specified server address and request handler.
    httpd: HTTPServer = server_class(server_address, handler_class)

    # Print a message to the console indicating that the server is starting and which port it will listen on.
    print(f"Starting HTTP server on port {port}...")

    # Start the server and make it continuously listen for requests.
    # This method will block the program and keep running until interrupted.
    httpd.serve_forever()


# If this script is executed directly (not imported as a module), this block runs.
# It calls the `run()` function to start the server.
if __name__ == '__main__':
    run()


