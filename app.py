import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import numpy as np
import os
import json
import hashlib
import time
from contextlib import closing

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for sessions
DB_PATH = "Voting.db"
BLOCKCHAIN_FILE = "blockchain.json"

# --- Blockchain Implementation ---
class Blockchain:
    def __init__(self):
        self.chain = []
        if os.path.exists(BLOCKCHAIN_FILE):
            try:
                with open(BLOCKCHAIN_FILE, 'r') as f:
                    self.chain = json.load(f)
            except:
                self.chain = []
    
    def calculate_hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, voter_id, candidate):
        previous_hash = self.chain[-1]['hash'] if self.chain else "0"
        block = {
            'index': len(self.chain) + 1,
            'voter_id': voter_id,
            'candidate': candidate,
            'timestamp': time.time(),
            'previous_hash': previous_hash
        }
        block['hash'] = self.calculate_hash(block)
        self.chain.append(block)
        self.save_chain()

    def save_chain(self):
        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump(self.chain, f, indent=4)
            
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current['previous_hash'] != previous['hash']:
                return False
        return True

blockchain = Blockchain()

# --- Database Helper ---
def get_db_connection():
    # Helper to get connection with timeout and dictionary row output
    conn = sqlite3.connect(DB_PATH, timeout=20)
    # conn.row_factory = sqlite3.Row # Optional, but good for robust access
    return conn

# --- Database Setup ---
def init_db():
    try:
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS voters (
                        cs_id TEXT PRIMARY KEY,
                        face_data BLOB,
                        vote TEXT,
                        has_voted INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")

init_db()

# --- Eye Biometric Capture ---
def capture_eye_biometric():
    cam = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    start_time = time.time()
    captured_face = None
    
    while True:
        ret, frame = cam.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            # If at least 2 eyes are detected, we consider it a valid biometric capture
            if len(eyes) >= 2:
                captured_face = cv2.resize(gray, (100, 100))
                break
        
        if captured_face is not None:
            break
            
        # Timeout after 10 seconds
        if time.time() - start_time > 10:
            break
            
    cam.release()
    return captured_face

# Check if face/eye data matches existing voter
def face_exists(new_face):
    match_found = False
    try:
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT face_data FROM voters")
                rows = cursor.fetchall()
                
                for row in rows:
                    if row[0]:
                        stored_face = np.frombuffer(row[0], dtype=np.uint8).reshape((100, 100))
                        diff = np.linalg.norm(stored_face - new_face)
                        if diff < 5000:  # Increased threshold to 5000 for more lenient matching
                            match_found = True
                            break
    except Exception as e:
        print(f"Face Check Error: {e}")
        
    return match_found

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

import base64

# ... (existing imports)

# New Route to serve the Client-Side Scanning Page
@app.route("/register_page", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        cs_id = request.form.get("voter_id") # Note: register.html uses 'voter_id'
        eye_image_b64 = request.form.get("eye_image")

        # 1. Validate ID
        if not cs_id:
            return "ID is required", 400
        identifier = cs_id.lower().strip()
        
        # 2. Process Image
        if not eye_image_b64:
             return "Biometric data missing", 400
             
        try:
            # Decode Base64
            encoded_data = eye_image_b64.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            face_data = cv2.resize(img, (100, 100))
        except Exception as e:
            return f"Image processing error: {e}", 400

        # 3. Check Duplicates (ID and Face)
        if face_exists(face_data):
            return "Biometric data already registered!", 400
            
        try:
            with closing(get_db_connection()) as conn:
                with closing(conn.cursor()) as cursor:
                    # Check ID existence
                    cursor.execute("SELECT 1 FROM voters WHERE cs_id=?", (identifier,))
                    if cursor.fetchone():
                         return "ID already exists!", 400

                    cursor.execute(
                        "INSERT INTO voters (cs_id, face_data) VALUES (?, ?)",
                        (identifier, face_data.tobytes())
                    )
                    conn.commit()
            return render_template("success.html", message=f"Registration successful for {identifier}!")
        except Exception as e:
            return f"Database Error: {e}", 500

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    cs_id = request.form.get("cs_id")
    
    # 1. Validate ID Format
    if not cs_id:
        return render_template("index.html", error="CS ID is required!")
        
    identifier = cs_id.lower().strip()
    if not identifier.startswith("cs"):
        return render_template("index.html", error="ID must start with 'cs'!")
        
    try:
        num_part = int(identifier[2:])
        if not (1 <= num_part <= 400):
            return render_template("index.html", error="ID must be between cs001 and cs400!")
    except ValueError:
        return render_template("index.html", error="Invalid ID format! Use cs001-cs400.")

    # 2. Capture Biometrics
    print("Starting Eye Capture...")
    face_data = capture_eye_biometric()
    if face_data is None:
        return render_template("index.html", error="Eye detection failed! Please look closely at the camera.")

    if face_exists(face_data):
        return render_template("index.html", error="Biometric data already registered!")

    # 3. Save to DB
    try:
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO voters (cs_id, face_data) VALUES (?, ?)",
                    (identifier, face_data.tobytes())
                )
                conn.commit()
        return render_template("success.html", message=f"Registration successful for {identifier}!")
    except sqlite3.IntegrityError:
        return render_template("index.html", error="CS ID already registered!")
    except Exception as e:
        return render_template("index.html", error=f"Database Error: {e}")

@app.route("/vote/<cs_id>", methods=["GET", "POST"])
def vote_page(cs_id):
    cs_id = cs_id.lower().strip() # Normalize ID
    try:
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT has_voted FROM voters WHERE cs_id=?", (cs_id,))
                row = cursor.fetchone()
                
                if not row:
                    return render_template("index.html", error="CS ID not found!")
                if row[0]:
                    return render_template("index.html", error="This ID has already voted!")
                    
                if request.method == "POST":
                    vote = request.form.get("candidate")
                    
                    # Update DB
                    cursor.execute("UPDATE voters SET vote=?, has_voted=1 WHERE cs_id=?", (vote, cs_id))
                    conn.commit()
                    
                    # Add to Blockchain (after DB success)
                    blockchain.add_block(cs_id, vote)
                    
                    return render_template("success.html", message="Vote cast successfully! Recorded on Blockchain.")
            
        return render_template("vote.html", cs_id=cs_id)
    except Exception as e:
        return render_template("index.html", error=f"System Error: {e}")

@app.route("/login_page", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        cs_id = request.form.get("cs_id")
        eye_image_b64 = request.form.get("eye_image")

        if not cs_id or not eye_image_b64:
             return render_template("login_scan.html", error="ID and Scan Required")

        # Decode Image
        try:
            encoded_data = eye_image_b64.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            current_face = cv2.resize(img, (100, 100))
        except Exception as e:
            return f"Image processing failed: {e}"

        # Get Stored Face
        row = None
        try:
            with closing(get_db_connection()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("SELECT face_data FROM voters WHERE cs_id=?", (cs_id.lower().strip(),))
                    row = cursor.fetchone()
        except:
            return "Database Error"
        
        if not row:
             return "ID not registered."
             
        # Biometric Verification
        stored_face = np.frombuffer(row[0], dtype=np.uint8).reshape((100, 100))
        dist = np.linalg.norm(stored_face - current_face)
        
        # DEBUG: Print distance
        print(f"Login Attempt for {cs_id}: Distance = {dist}")
        
        # RELAXED THRESHOLD FOR DEMO
        if dist < 35000:  
            return redirect(url_for('vote_page', cs_id=cs_id))
        else:
            return f"Biometric mismatch! Distance: {int(dist)} (Threshold: 35000). Try better lighting."

    return render_template("login_scan.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Keep old server-side logic as fallback, but relax threshold there too
        cs_id = request.form.get("cs_id")
        
        row = None
        try:
            with closing(get_db_connection()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("SELECT face_data FROM voters WHERE cs_id=?", (cs_id,))
                    row = cursor.fetchone()
        except Exception as e:
             return render_template("index.html", error=f"DB Error: {e}")
        
        if not row:
             return render_template("index.html", error="ID not registered.")
             
        # Biometric Verification
        current_face = capture_eye_biometric()
        if current_face is None:
             return render_template("index.html", error="Face/Eye detection failed (Server Cam).")
             
        stored_face = np.frombuffer(row[0], dtype=np.uint8).reshape((100, 100))
        dist = np.linalg.norm(stored_face - current_face)
        print(f"Server-Side Login Distance: {dist}")
        
        if dist < 35000: 
            return redirect(url_for('vote_page', cs_id=cs_id))
        else:
            return render_template("index.html", error=f"Biometric mismatch! Dist: {int(dist)}")
            
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123":
            session['admin_logged_in'] = True
            return redirect(url_for('results'))
        else:
            return render_template("admin_login.html", error="Invalid Password")
    return render_template("admin_login.html")

@app.route("/results")
def results():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    try:
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT vote, COUNT(*) FROM voters WHERE vote IS NOT NULL GROUP BY vote")
                vote_counts = cursor.fetchall()
        
        return render_template("results.html", vote_counts=vote_counts, chain=blockchain.chain)
    except Exception as e:
        return f"Error loading results: {e}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)