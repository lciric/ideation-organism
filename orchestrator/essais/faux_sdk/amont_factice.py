"""Amont factice (v6) : un serveur local qui joue l'interface de programmation derrière le relais, pour les essais du relais
et la répétition générale. Il exige la **clé factice** `CLE_FACTICE` (jamais une vraie clé) et rend soit un message JSON
avec son usage, soit un flux d'événements si la requête demande `stream`. Aucun modèle, aucun réseau."""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CLE_FACTICE = "cle-factice-essai-123"
USAGE = {"input_tokens": 1000, "output_tokens": 200}


class AmontFactice:
    def __init__(self):
        self.requetes = []
        amont = self

        class Gestionnaire(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def _json(self, statut, objet):
                reponse = json.dumps(objet).encode()
                self.send_response(statut)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reponse)))
                self.end_headers()
                self.wfile.write(reponse)

            def do_POST(self):
                longueur = int(self.headers.get("content-length") or 0)
                corps = json.loads(self.rfile.read(longueur) or b"{}")
                amont.requetes.append({"chemin": self.path, "cle": self.headers.get("x-api-key"),
                                       "en_tetes": dict(self.headers), "corps": corps})
                if self.headers.get("x-api-key") != CLE_FACTICE:
                    return self._json(401, {"erreur": "clé refusée par l'amont"})
                modele = corps.get("model", "claude-opus-5-5")
                if corps.get("stream"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Transfer-Encoding", "chunked")
                    self.end_headers()
                    evenements = [
                        {"type": "message_start", "message": {"model": modele, "usage": {"input_tokens": USAGE["input_tokens"],
                                                                                         "output_tokens": 1}}},
                        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "bonjour"}},
                        {"type": "message_delta", "usage": {"output_tokens": USAGE["output_tokens"]}},
                        {"type": "message_stop"},
                    ]
                    for e in evenements:
                        morceau = f"event: {e['type']}\ndata: {json.dumps(e)}\n\n".encode()
                        self.wfile.write(b"%x\r\n%s\r\n" % (len(morceau), morceau))
                        self.wfile.flush()
                        time.sleep(0.02)
                    self.wfile.write(b"0\r\n\r\n")
                    return
                return self._json(200, {"id": "msg", "model": modele, "content": [{"type": "text", "text": "bonjour"}],
                                        "usage": dict(USAGE)})

        self.serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
        self.url = f"http://127.0.0.1:{self.serveur.server_address[1]}"
        self.fil = threading.Thread(target=self.serveur.serve_forever, daemon=True)
        self.fil.start()

    def arreter(self):
        self.serveur.shutdown()
        self.serveur.server_close()
