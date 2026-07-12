# -*- coding: utf-8 -*-
"""
Render.com kabi hostinglar "Web Service" turidagi loyihalardan PORT'ni
tinglab turishni talab qiladi, aks holda xizmatni "ishlamayapti" deb
hisoblab to'xtatib qo'yadi. Bu modul shunchaki portni tinglab, har qanday
so'rovga "OK" deb javob beradigan juda yengil serverni orqa fonda
(alohida thread'da) ishga tushiradi — asosiy Telegram bot esa unga
xalaqit bermasdan parallel ishlayveradi.
"""

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bot ishlayapti ✅".encode("utf-8"))

    def log_message(self, format, *args):  # noqa: A002
        # Konsolni keraksiz HTTP loglar bilan to'ldirmaslik uchun jim turadi.
        pass


def start_health_server() -> None:
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Health-check server {port}-portda ishga tushdi.")
