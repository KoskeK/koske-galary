from werkzeug.security import generate_password_hash, check_password_hash

answer = input("Generate or check? (g/c)> ")
if answer == "g":
    print(generate_password_hash(input("Input password> ")))
if answer == "c":
    print(check_password_hash(input("Hash> "), input("Password> ")))
else:
    print("Invalid input")