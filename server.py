"""
HTTP Server Shell
Author: Barak Gonen and Nir Dweck
Purpose: Provide a basis for Ex. 4
Note: The code is written in a simple way, without classes, log files, or
other utilities, for educational purposes
Usage: Fill the missing functions and constants
"""
import logging
import os
import re
import socket

# define log constants
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/loggerServer.log'

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
OK_CODE = "200 OK"

DOESNT_EXIST_CONTENT = "/404.html"
WEBROOT = "C:/Users/Yonatan/PycharmProjects/exc4.0/webroot"
QUEUE_SIZE = 10
MAX_PACKET = 1024
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2


def get_file_data(file_name):
    """
    Get data from file

    :param file_name: Name of the file.
    :type file_name: str

    :return: The file data in binary.
    :rtype: bytes
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
        logging.error(f"File '{file_name}' not found.")
        print(f"File '{file_name}' not found.")
        return ""
    except Exception as e:
        logging.error(f"Error reading file '{file_name}': {e}")
        print(f"Error reading file '{file_name}': {e}")
        return ""


def create_data_headers(resource, data):
    """
    Create data headers.

    :param resource: The resource.
    :type resource: str

    :param data: The data.
    :type data: bytes

    :return: The headers.
    :rtype: str
    """
    file_extension = os.path.splitext(resource)[1][1:]
    headers = "Content-Type: " + CONTENT_TYPE_DICT[file_extension] + "\r\n"
    headers += "Content-Length: " + str(len(data)) + "\r\n"
    return headers


def handle_bad_request():
    """
    Handle bad request.

    :return: The response line.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + BAD_REQUEST_CODE + "\r\n\r\n"
    logging.debug(f"returning - {res_line}")
    return res_line


def handle_redirect():
    """
    Handle redirect.

    :return: The response line and headers.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + REDIRECTED_CODE + "\r\n"
    headers = REDIRECTED_HEADER + "\r\n\r\n"
    logging.debug(f"returning - {res_line}+{headers}")
    return res_line + headers


def handle_forbidden():
    """
    Handle forbidden.

    :return: The response line.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + FORBIDDEN_CODE + "\r\n\r\n"
    logging.debug(f"returning - {res_line}")
    return res_line


def handle_error():
    """
    Handle error.

    :return: The response line.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + ERROR_CODE + "\r\n\r\n"
    logging.debug(f"returning - {res_line}")
    return res_line


def handle_not_found(data):
    """
    Handle not found.

    :param data: The data.
    :type data: bytes

    :return: The response.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + DOESNT_EXIST_CODE + "\r\n"
    headers = create_data_headers(DOESNT_EXIST_CONTENT, data) + "\r\n"
    logging.debug(f"returning - {res_line}+{headers}")
    return res_line + headers


def handle_ok(resource, data):
    """
    Handle OK.

    :param resource: The resource.
    :type resource: str

    :param data: The data.
    :type data: bytes

    :return: The response.
    :rtype: str
    """
    res_line = HTTP_PROTOCOL_NAME + " " + OK_CODE + "\r\n"
    headers = create_data_headers(resource, data) + "\r\n"
    logging.debug(f"returning - {res_line}+{headers}")
    return res_line + headers


def handle_client_request(resource):
    """
    Check the required resource, generate proper HTTP response, and send to client.

    :param resource: The required resource.
    :type resource: str

    :return: if the request was a valid http request, the response line + headers and the response body if exists
    :rtype tuple(bool, str, bytes)
    """
    res, data = "", b''
    valid = True
    if resource == "":
        logging.warning("invalid http request")
        print("Invalid HTTP Request")
        valid = False
        res = handle_bad_request()
    elif resource in REDIRECTED_LIST:
        res = handle_redirect()
    elif resource in ERROR_LIST:
        res = handle_error()
    elif resource in FORBIDDEN_LIST:
        res = handle_forbidden()
    elif not os.path.exists(WEBROOT + resource):
        data = get_file_data(WEBROOT + DOESNT_EXIST_CONTENT)
        res = handle_not_found(data)
    else:
        if resource == '/':
            filepath = WEBROOT + INDEX_URL
        else:
            filepath = WEBROOT + resource
        data = get_file_data(filepath)
        res = handle_ok(filepath, data)

    return valid, res, data


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and return TRUE/FALSE and the requested URL.

    :param request: The request received from the client.
    :type request: str

    :return: the requested resource
    :rtype: str
    """
    r_value = ""
    lines = re.split('\r\n', request)
    if len(lines) >= 2:
        req_line = lines[0].split(" ")
        if len(req_line) == 3:
            method, resource, protocol = req_line
            if protocol == HTTP_PROTOCOL_NAME:
                if method in EXCEPTED_METHODS:
                    if resource.startswith("/"):
                        r_value = resource
    return r_value


def send_data(client_socket, res, data):
    """
    :param client_socket: A socket for communication with the client.
    :type client_socket: socket.socket\

    :param res: the response line + headers
    :type res: str

    :param data: the response body
    :type data: bytes

    :return: if the data was sent successfully
    :rtype: bool
    """
    was_sent = False
    try:
        sent = 0
        to_sent = res.encode() + data
        while sent < len(to_sent):
            sent += client_socket.send(to_sent)
        was_sent = True
    except socket.error as err:
        logging.error(f"error while sending to client: {err}")
    return was_sent


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
                client_request = ''
                break
            client_request += packet
        resource = validate_http_request(client_request)
        valid, res, data = handle_client_request(resource, client_socket)
        if not valid:
            break
        if not send_data(client_socket, res, data):
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
    # make sure we have a logging directory and configure the logging
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    r1 = validate_http_request("GET / HTTP/1.1\r\n\r\n")
    assert "/" == r1 and OK_CODE in handle_client_request(r1)[1]

    r = validate_http_request("GET /moved HTTP/1.1\r\n\r\n")
    assert "/moved" == r and REDIRECTED_CODE in handle_client_request(r)[1]

    r = validate_http_request("GET /forbidden HTTP/1.1\r\n\r\n")
    assert "/forbidden" == r and FORBIDDEN_CODE in handle_client_request(r)[1]

    r = validate_http_request("GET /error HTTP/1.1\r\n\r\n")
    assert "/error" == r and ERROR_CODE in handle_client_request(r)[1]

    r = validate_http_request("GET /nonexistent HTTP/1.1\r\n\r\n")
    assert "/nonexistent" == r and DOESNT_EXIST_CODE in handle_client_request(r)[1]
    # Call the main handler function
    main()
