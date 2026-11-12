"""Appel d'un modèle d'une autre famille pour la course 2 (Kimi par l'API compatible OpenAI de Moonshot, Gemini par l'API
generateContent). Aucune clé dans ce fichier : elles sont lues dans l'environnement et jamais écrites. Aucun outil n'est donné
au modèle. Garde reprise de l'organisme : le modèle servi doit être le modèle demandé, sinon refus ; une réponse coupée par la
borne de sortie est une erreur, pas un résultat. Chaque appel écrit sa réponse brute et son compte de jetons.
Usage : python3 appeler.py <kimi|gemini> <fichier consigne> <fichier sortie> <max jetons de sortie>"""
import json, os, sys, time, hashlib, urllib.request, urllib.error

MODELES = {"kimi": "kimi-k3.1-pro", "gemini": "gemini-4-argon"}

def poster(url, entetes, corps, delai):
    req = urllib.request.Request(url, data=json.dumps(corps).encode(), headers={"Content-Type": "application/json", **entetes})
    with urllib.request.urlopen(req, timeout=delai) as r:
        return json.loads(r.read())

def appeler(famille, consigne, max_sortie, delai=1500):
    modele = MODELES[famille]
    if famille == "kimi":
        d = poster("https://api.moonshot.ai/v1/chat/completions", {"Authorization": "Bearer " + os.environ["KIMI_API_KEY"]},
                   {"model": modele, "messages": [{"role": "user", "content": consigne}], "max_tokens": max_sortie}, delai)
        servi, ch = d.get("model", ""), d["choices"][0]
        texte, fin = ch["message"].get("content") or "", ch.get("finish_reason")
        u = d.get("usage", {}); jetons = {"entree": u.get("prompt_tokens"), "sortie": u.get("completion_tokens")}
        coupe = fin == "length"
    else:
        d = poster(f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent",
                   {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
                   {"contents": [{"role": "user", "parts": [{"text": consigne}]}], "generationConfig": {"maxOutputTokens": max_sortie}}, delai)
        servi, c = d.get("modelVersion", ""), d["candidates"][0]
        texte = "".join(p.get("text", "") for p in c.get("content", {}).get("parts", []) if not p.get("thought"))
        fin = c.get("finishReason"); u = d.get("usageMetadata", {})
        jetons = {"entree": u.get("promptTokenCount"), "sortie": (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0)}
        coupe = fin == "MAX_TOKENS"
    if not servi.startswith(modele):
        raise SystemExit(f"refus : modèle servi {servi!r} différent du modèle demandé {modele!r}")
    if coupe:
        raise SystemExit(f"erreur : réponse coupée par la borne de sortie ({jetons})")
    if not texte.strip():
        raise SystemExit(f"erreur : réponse vide (fin = {fin}, {jetons})")
    return texte, {"famille": famille, "modele_demande": modele, "modele_servi": servi, "fin": fin, "jetons": jetons}

if __name__ == "__main__":
    famille, f_consigne, f_sortie, max_sortie = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    consigne = open(f_consigne, encoding="utf-8").read()
    for essai in range(1, 5):
        try:
            texte, meta = appeler(famille, consigne, max_sortie); break
        except urllib.error.HTTPError as e:
            corps = e.read()[:300].decode("utf8", "replace")
            print(f"essai {essai} : HTTP {e.code} {corps}", file=sys.stderr)
            if e.code not in (429, 500, 502, 503, 504) or essai == 4: raise SystemExit(f"arrêt : HTTP {e.code}")
            time.sleep(30 * essai)
    meta.update({"consigne_sha256": hashlib.sha256(consigne.encode()).hexdigest(), "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    open(f_sortie, "w", encoding="utf-8").write(texte)
    open(f_sortie + ".meta.json", "w", encoding="utf-8").write(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps(meta, ensure_ascii=False))
