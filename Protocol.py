from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
from io import TextIOWrapper
import socket
from typing import List

FORMAT = 'utf-8'
PORT = 80
MAX_SIZE = 4096
VERSION = 1.1
responses = {
	100: ('Continue', 'Request received, please continue'),
	101: ('Switching Protocols',
		  'Switching to new protocol; obey Upgrade header'),

	200: ('OK', 'Request fulfilled, document follows'),
	201: ('Created', 'Document created, URL follows'),
	202: ('Accepted',
		  'Request accepted, processing continues off-line'),
	203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
	204: ('No Content', 'Request fulfilled, nothing follows'),
	205: ('Reset Content', 'Clear input form for further input.'),
	206: ('Partial Content', 'Partial content follows.'),

	300: ('Multiple Choices',
		  'Object has several resources -- see URI list'),
	301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
	302: ('Found', 'Object moved temporarily -- see URI list'),
	303: ('See Other', 'Object moved -- see Method and URL list'),
	304: ('Not Modified',
		  'Document has not changed since given time'),
	305: ('Use Proxy',
		  'You must use proxy specified in Location to access this '
		  'resource.'),
	307: ('Temporary Redirect',
		  'Object moved temporarily -- see URI list'),

	400: ('Bad Request',
		  'Bad request syntax or unsupported method'),
	401: ('Unauthorized',
		  'No permission -- see authorization schemes'),
	402: ('Payment Required',
		  'No payment -- see charging schemes'),
	403: ('Forbidden',
		  'Request forbidden -- authorization will not help'),
	404: ('Not Found', 'Nothing matches the given URI'),
	405: ('Method Not Allowed',
		  'Specified method is invalid for this server.'),
	406: ('Not Acceptable', 'URI not available in preferred format.'),
	407: ('Proxy Authentication Required', 'You must authenticate with '
										   'this proxy before proceeding.'),
	408: ('Request Timeout', 'Request timed out; try again later.'),
	409: ('Conflict', 'Request conflict.'),
	410: ('Gone',
		  'URI no longer exists and has been permanently removed.'),
	411: ('Length Required', 'Client must specify Content-Length.'),
	412: ('Precondition Failed', 'Precondition in headers is false.'),
	413: ('Request Entity Too Large', 'Entity is too large.'),
	414: ('Request-URI Too Long', 'URI is too long.'),
	415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
	416: ('Requested Range Not Satisfiable',
		  'Cannot satisfy request range.'),
	417: ('Expectation Failed',
		  'Expect condition could not be satisfied.'),

	500: ('Internal Server Error', 'Server got itself in trouble'),
	501: ('Not Implemented',
		  'Server does not support this operation'),
	502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
	503: ('Service Unavailable',
		  'The server cannot process the request due to a high load'),
	504: ('Gateway Timeout',
		  'The gateway server did not receive a timely response'),
	505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}

httpOptions = ["GET", "POST"]

filenameToType = {
	"pdf": "application/pdf",
	"json": "application/json",
	"xml": "application/xml",
	"zip": "application/zip",
	"gif": "image/gif",
	"jpeg": "image/jpeg",
	"jpg": "image/jpeg",
	"png": "image/png",
	"js": "text/javascript; charset=UTF-8",
	"css": "text/css",
	"csv": "text/csv",
	"html": "text/html",
	"mp4": "video/mp4",
	"ico": "image/vnd.microsoft.icon",
}


def startsWithOption(data: list | str, options: List[list] | List[str]) -> any:
	for option in options:
		try:
			if data[:len(option)] == option:
				return option
		except IndexError:
			pass
	return None


def formatHttpGet(code: int, headers: str = None, params: bytes = None) -> bytes:
	data = params if params is not None else []
	now = datetime.now()
	stamp = mktime(now.timetuple())
	response = f"HTTP/1.1 {code} {responses[code][0]}\r\nDate: {format_date_time(stamp)}\r\nContent-Length: {str(len(data))}\r\n".encode(
		FORMAT)
	if headers is not None:
		response += headers.encode(FORMAT)
	response += "\r\n".encode(FORMAT)
	if params is not None:
		response += params
	return response


def formatHttpPost(code: int, headers: str = None, params: bytes = None) -> bytes:
	data = params if params is not None else b"<div>OK</div>"
	now = datetime.now()
	stamp = mktime(now.timetuple())
	response = f"HTTP/1.1 {code} {responses[code][0]}\r\nDate: {format_date_time(stamp)}\r\nContent-Length: {str(len(data))}\r\n".encode(
		FORMAT)
	if headers is not None:
		response += headers.encode(FORMAT)
	response += "\r\n".encode(FORMAT)
	response += data
	return response


def formatFileHttp(code: int, path: str, file: TextIOWrapper) -> bytes:
	data = file.read()
	return formatHttpGet(code,
						 f"Content-Type: {filenameToType[path[path.rfind('.') + 1:]]}\r\n", data)


def calculateNext(data: dict) -> int:
	return int(data["num"]) + 1


def calculateArea(data: dict) -> int:
	return int(float(data["width"])) * int(float(data["height"])) // 2


def upload(data, params):
	with open("./webroot/" + data["file-name"], "wb") as f:
		f.write(params)
	return


functions = {"/calculate-next": lambda data: calculateNext(data), "/calculate-area": lambda data: calculateArea(data),
			 "/upload": lambda data, params: upload(data, params)}
