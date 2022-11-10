import socket
from threading import Thread
import os

import Protocol

# green terminal:
os.system('color a')
# create socket (works out of main. if you make a server you want this to run always)
DEBUGGING = True
CLIENT_COUNT = 0
SERVER = '127.0.0.1'
ADDR = (SERVER, Protocol.PORT)
server = socket.socket()


# functions


def setup():
	global server
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(ADDR)


def ReceiveRequest(conn: socket) -> bool:
	"""
	:param conn: client sending message
	:return: bytearray of data
	"""
	shouldStay = True
	try:
		data = conn.recv(Protocol.MAX_SIZE).decode(Protocol.FORMAT)
	# print("<<<<" + repr(data) + "<END>")
	except (socket.error, UnicodeDecodeError):
		return False

	if len(data) != 0:
		response = handleRequest(data, conn)
		# print(">>>>>" + repr(response) + "<END>")
		conn.sendall(response)
	else:
		shouldStay = False
	return shouldStay


def checkValidity(data: str) -> tuple[bool, int, str, dict[str, str]]:
	option = Protocol.startsWithOption(data, Protocol.httpOptions)
	if option is None:
		return False, 0, "", {}
	data = data.strip(option)
	path = data[:data.index("HTTP/1.1")]
	data = data[len(path):]
	if data[:8] != "HTTP/1.1":
		return False, 0, "", {}
	else:
		data = data[8:]
		if data[:1] != "\r\n":
			return True, option, path.strip(), Protocol.dictify(data[2:-4],":","\r\n")
		else:
			return False, 0, "", {}


def getFromFile(path) -> bytes:
	if ".." in path:
		response = Protocol.formatHttpGet(401)
	else:
		if path == "/":
			path = "/index.html"
		try:
			with open("./webroot" + path, "rb") as file:
				response = Protocol.formatFileHttp(200, path, file)
		except OSError:
			response = Protocol.formatHttpGet(500)
	return response


def handleRequest(data: str, conn: socket):
	response = b""
	valid, option, path, headers = checkValidity(data)
	if not valid:
		response = Protocol.formatHttpGet(400)
	else:

		function = Protocol.startsWithOption(path, Protocol.functions.keys())
		if function is None:
			response = getFromFile(path)
		else:
			responseFunc = Protocol.functions[function]
			try:
				function, params_string = path.split("?")
				params = Protocol.dictify(params_string,"=","&")
				if option == "GET":
					response = Protocol.formatHttpGet(200, None, str(responseFunc(params)).encode(Protocol.FORMAT))
				elif option == "POST":
					requestData = conn.recv(int(headers['Content-Length']))
					responseFunc(params, requestData)
					response = Protocol.formatHttpPost(200)
					print(response)
			except KeyError as e:
				if option == "GET":
					response = Protocol.formatHttpGet(400)
				elif option == "POST":
					response = Protocol.formatHttpPost(400)
	return response


def handleClient(conn: socket):
	global CLIENT_COUNT
	"""
	:param conn: the client socket
	:return: None
	"""
	STAY = True
	print(f"[RECEIVED REQUEST]")
	while STAY:
		STAY = ReceiveRequest(conn)
		if not STAY:
			CLIENT_COUNT -= 1
			conn.close()
			print(f"[FINISHED REQUEST]")
	exit()


def start():
	global server
	global CLIENT_COUNT
	while True:
		server.listen()
		conn = server.accept()[0]
		Thread(target=handleClient, args=(conn,), daemon=True).start()
		CLIENT_COUNT += 1
		print(f"[STATUS] Number of active requests:{CLIENT_COUNT}")


def debugPrinting():
	pass


if __name__ == '__main__':
	setup()
	if DEBUGGING:
		debugPrinting()
	print(f"[STARTING] SERVER: {SERVER} PORT: {Protocol.PORT}")
	start()
