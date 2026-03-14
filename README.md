# Eye Biometric Voting System

This is a secure, blockchain-based voting system with biometric authentication.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will start on `http://127.0.0.1:5000`.

## Features
- **Biometric Authentication**: Uses webcam to verify voters via face/eye patterns (Client-side scanning).
- **Blockchain**: All votes are recorded on a local blockchain (`blockchain.json`) for immutability.
- **Database**: Voter registration and status is stored in `Voting.db`.
- **Admin Panel**: View results and verify the blockchain ledger.
- **Dynamic UI**: 
  - Cinematic **Intro Animation** with particle effects and "hashing" decode sequence.
  - **Cyber Hexagon** interactive background for voting interface.
  - **Success Branding** animation that reinforces company identity after actions.

## Usage Guide

### 1. Register a Voter
- Go to the home page.
- Enter a Voter ID (Format: `CS001`, `CS002`, ..., `CS400`).
- Click **Register**.
- Look at the camera to capture your biometric data.

### 2. Cast a Vote
- Go to the **Login** section.
- Enter your registered Voter ID.
- Look at the camera for biometric verification.
- Once verified, select your candidate and submit your vote.

### 3. Admin Access
- Go to `/admin` or click "Admin Login".
- Use password: `admin123`
- View live results and the blockchain ledger.

## Troubleshooting
- If you see `database is locked`, the app automatically retries. If it persists, restart the app.
- Ensure only one instance of the app is running.