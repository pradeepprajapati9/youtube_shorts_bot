"""
Kahani Shorts — Automatic YouTube Uploader (FREE, YouTube Data API v3)

Ye tere haath se banaye videos ko YouTube pe auto-upload karta hai.
youtube_bot ko chhue bina — ye alag standalone uploader hai.

────────────────────────────────────────────────────────────
ONE-TIME SETUP (sirf pehli baar):
  1. Google Cloud project banao → "YouTube Data API v3" enable karo
  2. OAuth client (Desktop app) banao → download → yahan rakho:
        uploader/credentials/client_secret.json
  3. Pehli baar chalao → browser khulega → apne channel se login/allow
     → token.json auto-save ho jaayega (dobara login nahi karna padega)
────────────────────────────────────────────────────────────

CHALANA:
  # Ek video upload:
  python upload.py "../ready-to-upload/aakhri-bus.mp4" "Title yahan" "tag1,tag2" "Description yahan"

  # Ya queue se saare pending videos ek saath (recommended):
  python upload.py --queue
────────────────────────────────────────────────────────────
"""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CRED_DIR = BASE_DIR / "credentials"
CLIENT_SECRET_FILE = CRED_DIR / "client_secret.json"
TOKEN_FILE = CRED_DIR / "token.json"
QUEUE_FILE = BASE_DIR.parent / "ready-to-upload" / "upload_queue.json"

# private = draft (sirf tu dekhe) | public = sabko | unlisted = link wale
PRIVACY = "private"   # pehle "private" rakho, review ke baad "public"
CATEGORY_ID = "24"    # 24 = Entertainment (horror/kahani ke liye sahi)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CRED_DIR.mkdir(parents=True, exist_ok=True)


def _get_service():
    """OAuth se YouTube service banata hai (pehli baar browser se authorize)."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as ex:
            print(f"[upload] token.json kharab ({ex}); dobara authorize karenge.")
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                raise FileNotFoundError(
                    f"\n[!] {CLIENT_SECRET_FILE} nahi mila.\n"
                    "    Google Cloud se OAuth client_secret.json download karke\n"
                    "    uploader/credentials/ me rakho (SETUP.md dekho).\n"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), "utf-8")
    return build("youtube", "v3", credentials=creds)


def upload_one(youtube, video_path: str, title: str, description: str,
               tags: list, privacy: str = PRIVACY) -> str:
    """Ek video YouTube pe upload karta hai. Video ka URL return karta hai."""
    from googleapiclient.http import MediaFileUpload

    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video nahi mila: {video_path}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4900],
            "tags": [t.strip() for t in tags if t.strip()][:15],
            "categoryId": CATEGORY_ID,
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"[upload] {int(status.progress() * 100)}%")
    url = f"https://youtu.be/{resp['id']}"
    print(f"[upload] DONE -> {url}")
    return url


def run_queue():
    """upload_queue.json me se saare 'pending' videos upload karta hai.
    Har upload ke baad usko 'done' mark kar deta -> DUPLICATE upload nahi hoga."""
    if not QUEUE_FILE.exists():
        print(f"[!] Queue nahi mila: {QUEUE_FILE}")
        print("    ready-to-upload/upload_queue.json banao (example dekho).")
        return

    queue = json.loads(QUEUE_FILE.read_text("utf-8"))
    pending = [v for v in queue if v.get("status") != "done"]
    if not pending:
        print("[queue] Koi pending video nahi. Sab upload ho chuke ✅")
        return

    youtube = _get_service()
    for item in pending:
        vpath = item["video"]
        # relative path ko ready-to-upload/ se resolve karo
        if not Path(vpath).is_absolute():
            vpath = str((QUEUE_FILE.parent / vpath).resolve())
        try:
            print(f"\n[queue] Uploading: {item['title']}")
            url = upload_one(youtube, vpath, item["title"],
                             item.get("description", ""), item.get("tags", []),
                             item.get("privacy", PRIVACY))
            item["status"] = "done"
            item["url"] = url
            # har success ke baad turant save (crash ho to bhi progress bache)
            QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), "utf-8")
        except Exception as ex:
            print(f"[!] Fail: {item['title']} -> {ex}")
            item["status"] = "error"
            item["error"] = str(ex)
            QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), "utf-8")

    print("\n[queue] Ho gaya. Status upload_queue.json me update ho gaya.")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--queue":
        run_queue()
        return
    # single upload: video title tags description
    if len(args) < 2:
        print("Usage: python upload.py <video> <title> [tags] [description]")
        return
    video = args[0]
    title = args[1]
    tags = args[2].split(",") if len(args) > 2 else []
    description = args[3] if len(args) > 3 else ""
    youtube = _get_service()
    upload_one(youtube, video, title, description, tags)


if __name__ == "__main__":
    main()
