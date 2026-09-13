from werkzeug.security import generate_password_hash, check_password_hash

input("Generate or check? (g/c)> ")
if input == "g":
    print(generate_password_hash(input("Input password> ")))
if input == "c":
    print(check_password_hash(input("Hash> "), input("Password> ")))
else:
    print("Invalid input")