# ⚙️ Uploader Setup — sirf ek baar karna hai

Ye uploader tere haath se banaye videos ko YouTube pe **auto-upload** karta hai.
(youtube_bot se alag, uska proven upload logic use karke — usko chhue bina.)

---

## 🔑 STEP 1 — Google Cloud OAuth (10 min, ek hi baar)

1. Jao: https://console.cloud.google.com/
2. Naya project banao (naam kuch bhi, e.g. "kahani-uploader")
3. Search karo **"YouTube Data API v3"** → **Enable** karo
4. Left menu → **APIs & Services → OAuth consent screen**
   - User type: **External** → app naam daalo → Save
   - **Test users** me apna Gmail (channel wala) add karo
5. Left menu → **Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app** → Create
   - **Download JSON** → us file ka naam badal ke `client_secret.json` rakho
6. Us file ko yahan rakho:
   ```
   kahani-shorts/uploader/credentials/client_secret.json
   ```

---

## 📦 STEP 2 — Packages install (ek baar)

```bash
cd kahani-shorts/uploader
pip install -r requirements.txt
```

(Ya youtube_bot ka venv use kar sakta hai — usme ye packages already hain.)

---

## ▶️ STEP 3 — Chalao

**Pehli baar:** browser khulega → apne channel se login → "Allow" → ho gaya
(token.json auto-save, dobara login nahi karna padega)

### Tarika A — Queue se (recommended, batch)
1. `ready-to-upload/upload_queue.json` me apne videos likho (example file dekho)
2. Chalao:
   ```bash
   python upload.py --queue
   ```
   Saare "pending" videos upload honge. Har ek "done" mark hoga → **duplicate upload nahi hoga.**

### Tarika B — Ek video seedha
```bash
python upload.py "../ready-to-upload/aakhri-bus.mp4" "Aakhri Bus 🚌 #shorts" "hindi kahani,horror,shorts" "Description yahan"
```

---

## 🔒 Zaroori (security)

- `credentials/` folder (client_secret.json + token.json) **kabhi GitHub pe push mat karo**
- `.gitignore` me ye already blocked hai ✅ — bas dhyan rahe

---

## ⚙️ Settings (upload.py ke top me)

| Setting | Default | Matlab |
|---|---|---|
| `PRIVACY` | `private` | Pehle private (tu review kare), phir `public` |
| `CATEGORY_ID` | `24` | Entertainment (horror/kahani ke liye sahi) |

**Tip:** Pehle 1-2 video `private` me upload karke YouTube pe dekh le sab theek hai — phir `public` kar dena.
