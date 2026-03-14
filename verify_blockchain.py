
import json
import hashlib
import os

BLOCKCHAIN_FILE = "blockchain.json"

def calculate_hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def verify_chain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        print("Blockchain file not found (yet).")
        return

    with open(BLOCKCHAIN_FILE, 'r') as f:
        chain = json.load(f)

    print(f"Loaded chain with {len(chain)} blocks.")
    
    valid = True
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i-1]
        
        # Check link
        if current['previous_hash'] != previous['hash']:
            print(f"❌ INVALID LINK at block {i}")
            print(f"   Current Previous Hash: {current['previous_hash']}")
            print(f"   Actual Previous Hash:  {previous['hash']}")
            valid = False
            
        # Check integrity (Optional: requires re-hashing logic matching app.py exactly)
        # We can try to re-hash if we strip the 'hash' field
        temp = current.copy()
        stored_hash = temp.pop('hash')
        recalculated_hash = calculate_hash(temp)
        
        if stored_hash != recalculated_hash:
             print(f"❌ INVALID HASH at block {i}")
             print(f"   Stored:       {stored_hash}")
             print(f"   Recalculated: {recalculated_hash}")
             valid = False

    if valid:
        print("✅ Blockchain is VALID.")
    else:
        print("❌ Blockchain is INVALID.")

if __name__ == "__main__":
    verify_chain()
