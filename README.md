# zapinit

Start a WhatsApp conversation with any phone number — no need to save the contact first.

Enter a phone number, click **Open on WhatsApp**, and you're redirected straight to a chat in WhatsApp Web.

## Stack

- **Backend:** FastAPI + Jinja2
- **Frontend:** Tailwind CSS + intl-tel-input
- **Language:** Python 3.11+

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## License

MIT
