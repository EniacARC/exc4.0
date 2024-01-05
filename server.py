"""
 HTTP Server Shell
 Author: Barak Gonen and Nir Dweck
 Purpose: Provide a basis for Ex. 4
 Note: The code is written in a simple way, without classes, log files or
 other utilities, for educational purpose
 Usage: Fill the missing functions and constants
"""
import os
import re
import socket

# TO DO: import modules

# TO DO: set constants

CONTENT_TYPE_DICT = {
    "html": "text/html;charset=utf-8",
    "jpg": "image/jpeg",
    "css": "text/css",
    "js": "text/javascript; charset=UTF-8",
    "txt": "text/plain",
    "ico": "image/x-icon",
    "gif": "image/jpeg",
    "png": "image/png"
}

INDEX_URL = "/index.html"
HTTP_PROTOCOL_NAME = "HTTP/1.1"
EXCEPTED_METHODS = ["GET"]

REDIRECTED_LIST = ["/moved"]
REDIRECTED_CODE = "302 TEMPORARILY MOVED"
REDIRECTED_HEADER = "Location: /"

FORBIDDEN_LIST = ["/forbidden"]
FORBIDDEN_CODE = "403 FORBIDDEN"

ERROR_LIST = ["/error"]
ERROR_CODE = "500 INTERNAL SERVER ERROR"

BAD_REQUEST_CODE = "400 BAD REQUEST"

DOESNT_EXIST_CODE = "404 NOT FOUND"
DOESNT_EXIST_CONTENT = "/404.html"
OK_CODE = "200 OK"

WEBROOT = "C:/Users/Yonatan/PycharmProjects/exc4.0/webroot"
QUEUE_SIZE = 10
MAX_PACKET = 1024
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """
    ext = os.path.splitext(file_name)[1][1:]
    try:
        if "text" in CONTENT_TYPE_DICT[ext]:
            with open(file_name, 'r') as file:
                # Read the content of the file
                file_data = file.read().encode()
                return file_data
        else:
            with open(file_name, 'rb') as file:
                file_data = file.read()
                return file_data
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")
        return ""


def get_file_data_raw(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in bytes
    """
    try:
        with open(file_name, 'rb') as file:
            # Read the content of the file
            file_data = file.read()
            return file_data
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return b''
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")
        return b''


def create_data_params(resource, data):
    file_extension = os.path.splitext(resource)[1][1:]
    headers = "Content-Type: " + CONTENT_TYPE_DICT[file_extension] + "\r\n"
    headers += "Content-Length: " + str(len(data)) + "\r\n"
    return headers


def handle_bad_request():
    res_line = HTTP_PROTOCOL_NAME + " " + BAD_REQUEST_CODE + "\r\n\r\n"
    return res_line


def handle_redirect():
    res_line = HTTP_PROTOCOL_NAME + " " + REDIRECTED_CODE + "\r\n"
    headers = REDIRECTED_HEADER + "\r\n\r\n"
    return res_line + headers


def handle_forbidden():
    res_line = HTTP_PROTOCOL_NAME + " " + FORBIDDEN_CODE + "\r\n\r\n"
    return res_line


def handle_error():
    res_line = HTTP_PROTOCOL_NAME + " " + ERROR_CODE + "\r\n\r\n"
    return res_line


def handle_not_found(data):
    res = HTTP_PROTOCOL_NAME + " " + DOESNT_EXIST_CODE + "\r\n"
    res += create_data_params(DOESNT_EXIST_CONTENT, data) + "\r\n"
    return res


def handle_ok(resource, data):
    res = HTTP_PROTOCOL_NAME + " " + OK_CODE + "\r\n"
    res += create_data_params(resource, data) + "\r\n"
    return res


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """

    if resource == "":
        res = handle_bad_request()
        res = res.encode()
    elif resource in REDIRECTED_LIST:
        res = handle_redirect()
        print(res)
        res = res.encode()
    elif resource in ERROR_LIST:
        res = handle_error()
        res = res.encode()
    elif resource in FORBIDDEN_LIST:
        res = handle_forbidden()
        res = res.encode()
    elif not os.path.exists(WEBROOT + resource):
        data = get_file_data(WEBROOT + DOESNT_EXIST_CONTENT)
        res = handle_not_found(data)
        # if "text" in CONTENT_TYPE_DICT[os.path.splitext(resource)[1]]:
        #
        #    data.encode()
        res = res.encode() + data
    else:
        if resource == '/':
            filepath = WEBROOT + INDEX_URL
        else:
            filepath = WEBROOT + resource
        print(filepath)
        data = get_file_data(filepath)
        res = handle_ok(filepath, data)
        # if "text" in CONTENT_TYPE_DICT[os.path.splitext(filepath)[1][1:]]:
        #    print("text")
        #    data.encode()
        #    res += data
        #    res.encode()
        res = res.encode() + data
    client_socket.send(res)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    r_value = False, ""
    lines = re.split('\r\n', request)
    if len(lines) >= 2:
        req_line = lines[0].split(" ")
        if len(req_line) == 3:
            method, resource, protocol = req_line
            if protocol == HTTP_PROTOCOL_NAME:
                if method in EXCEPTED_METHODS:
                    if resource.startswith("/"):
                        r_value = True, resource
    return r_value


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        # TO DO: insert code that receives client request
        client_request = ""
        while not re.search('\r\n\r\n', client_request):
            packet = client_socket.recv(MAX_PACKET).decode()
            if packet == '':
                break
            client_request += packet
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            print('Error: Not a valid HTTP request')
            break
    print('Closing connection')


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
