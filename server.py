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
			decodedValue = data[2:].split("\r\n")
			return True, option, path.strip(), {data2[0]: data2[1] for data2 in
												[data.split(":") for data in decodedValue if data.split(":") != ['']]}
		else:
			return False, 0, "", {}


def getFromFile(path) -> bytes:
	if ".." in path:
		response = Protocol.formatHttp(401)
	else:
		if path == "/":
			path = "/index.html"
		try:
			with open("./webroot" + path, "rb") as file:
				response = Protocol.formatFileHttp(200, path, file)
		except OSError:
			response = Protocol.formatHttp(500)
	return response


def handleRequest(data: str, conn: socket):
	response = b""
	valid, option, path, headers = checkValidity(data)
	if not valid:
		response = Protocol.formatHttp(400)
	else:
		if option == "GET":
			function = Protocol.startsWithOption(path, Protocol.functions.keys())
			if function is None:
				response = getFromFile(path)
			else:
				responseFunc = Protocol.functions[function]
				try:
					if "?" not in path:
						response = Protocol.formatHttp(200, None, str(responseFunc()).encode(Protocol.FORMAT))
					else:
						function, params_string = path.split("?")
						# create a new dictionary x=2&y=3 -> {"x":"2","y":"3"}
						params = {param.split("=")[0]: param.split("=")[1] for param in params_string.split("&")}
						response = Protocol.formatHttp(200, None, str(responseFunc(params)).encode(Protocol.FORMAT))
				except KeyError as e:
					response = Protocol.formatHttp(400)
		elif option == "POST":
			requestData = conn.recv(int(headers['Content-Length']))
			response = Protocol.formatHttp(500)
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
		print(f"[STATUS] Number of active users:{CLIENT_COUNT}")


def debugPrinting():
	pass


if __name__ == '__main__':
	setup()
	if DEBUGGING:
		debugPrinting()
	print(f"[STARTING] SERVER: {SERVER} PORT: {Protocol.PORT}")
	start()
