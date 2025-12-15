import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='gemao_db'
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, email, otp, created_at, expires_at, verified, NOW() as server_time FROM otp_verification ORDER BY created_at DESC LIMIT 5")
rows = cursor.fetchall()

print("\n=== Recent OTP Records ===")
for row in rows:
    print(f"\nID: {row['id']}")
    print(f"Email: {row['email']}")
    print(f"OTP: {row['otp']}")
    print(f"Created: {row['created_at']}")
    print(f"Expires: {row['expires_at']}")
    print(f"Verified: {row['verified']}")
    print(f"Server Time: {row['server_time']}")
    expired = row['expires_at'] < row['server_time']
    print(f"Is Expired: {expired}")

conn.close()
