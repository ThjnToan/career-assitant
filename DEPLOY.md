# Deployment Guide - Share CareerAssistant With Others

This guide shows you how to share CareerAssistant Pro so other people can use it too.

---

## Option 1: Share on Your Local Network (Easiest)

By default, the app runs on `0.0.0.0:5000`, which means anyone on your WiFi network can access it.

### Step 1: Find Your Computer's IP Address

Open Command Prompt and run:
```bash
ipconfig
```

Look for "IPv4 Address" under your WiFi adapter. It will look like:
```
IPv4 Address. . . . . . . . . . . : 192.168.1.105
```

### Step 2: Start the Server

```bash
python run.py
```

### Step 3: Share the Link

Tell your friends to open:
```
http://192.168.1.105:5000
```
(Replace with your actual IP)

**Limitation:** They can only access it while:
- Your computer is on
- The server is running
- You're all on the same WiFi network

---

## Option 2: Deploy to the Internet (Free)

### Using PythonAnywhere (Recommended for Beginners)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) and create a free account
2. Upload your `CareerAssistant` folder
3. Create a new web app (Flask)
4. Point it to your `run.py` file
5. Your app will be live at `yourname.pythonanywhere.com`

### Using Render (Free Tier)

1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub repository (push this folder to GitHub first)
3. Create a new Web Service
4. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Your app will be live at `your-app-name.onrender.com`

**Note:** Add `gunicorn` to your `requirements.txt`:
```
gunicorn>=21.0.0
```

### Using Railway

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Deploy automatically
4. Get a public URL

---

## Option 3: Run on a Raspberry Pi (Always-On Home Server)

If you have a Raspberry Pi or old computer:

1. Install Python and dependencies
2. Copy the CareerAssistant folder
3. Run `python run.py`
4. Set up port forwarding on your router (port 5000)
5. Use a free dynamic DNS service (like No-IP) to get a domain name
6. Your app is accessible from anywhere, 24/7

---

## Security Notes

**Before sharing publicly:**

1. **Change the secret key** in `app/__init__.py`:
```python
app.config['SECRET_KEY'] = 'your-random-secret-key-here'
```
Generate a random key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

2. **Use HTTPS** if deploying publicly (PythonAnywhere and Render provide this automatically)

3. **Set strong passwords** for user accounts

4. **Don't expose debug mode** in production:
```python
# In run.py, change:
app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## Making It Even Better

### Add a Custom Domain
- Buy a domain from Namecheap or Cloudflare
- Point it to your server's IP
- Free SSL with Cloudflare

### Auto-Start on Boot (Linux/Raspberry Pi)
Create a systemd service so the app starts automatically when the server reboots.

### Database Upgrade
For multiple users, switch from SQLite to PostgreSQL:
```python
# In app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/careerassistant'
```

---

## Summary

| Method | Difficulty | Cost | Best For |
|--------|-----------|------|----------|
| Local Network | Easy | Free | Friends on same WiFi |
| PythonAnywhere | Easy | Free | Small groups, beginners |
| Render | Medium | Free | Serious sharing |
| Raspberry Pi | Medium | One-time | 24/7 home server |

---

Need help? Check the PythonAnywhere or Render documentation, or ask the community.
