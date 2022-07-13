import datetime
import struct

import pytz

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route


class Logfile:
    def decode_head(self, i, buf):
        ENCODING = "utf_8"
        header = dict()
        header["logfile_version"] = struct.unpack_from("<H", buf, i)[0]
        i += 2
        mac_bytes = struct.unpack_from("<BBBBBB", buf, i)
        header["mac"] = ":".join([f"{x:02x}" for x in mac_bytes])
        i += 6
        header["interval"] = struct.unpack_from("<I", buf, i)[0]
        i += 4
        tz_len = struct.unpack_from("<B", buf, i)[0]
        i += 1
        header["timezone"] = buf[i : i + tz_len].decode(ENCODING)
        i += tz_len
        metadata_len = struct.unpack_from("<I", buf, i)[0]
        i += 4
        metadata = buf[i : i + metadata_len].decode(ENCODING)
        i += metadata_len
        header["metadata"] = metadata
        return i, header

    def decode_body(self, i, buf):
        entries = list()
        while i < len(buf):
            (a, b, c) = struct.unpack_from("<iHH", buf, i)
            st = datetime.fromtimestamp(a, tz=pytz.UTC)
            i += 8
            j = i + c
            rssis = []
            while i < j:
                (rssi,) = struct.unpack_from("<b", buf, i)
                i += 1
                rssis.append(rssi)
            entries.append((st, b, c, rssis))
        return i, entries

    def decode(self, buf: bytes):
        i = 0
        i, header = self.decode_head(i, buf)
        i, entries = self.decode_body(i, buf)
        return header, entries


async def api_v1(request):
    api_key = request.query_params["api_key"]
    body = await request.body()
    header, entries = Logfile().decode(body)
    return PlainTextResponse("")


app = Starlette(
    debug=True,
    routes=[
        Route("/data-server/api/v1/upload", api_v1, methods=["POST"]),
    ],
)
