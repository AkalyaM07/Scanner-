import pickle

# 🔴 Hardcoded secret
password = "admin123"

# 🔴 Unsafe eval usage
user_input = input("Enter something: ")
result = eval(user_input)
print("Eval result:", result)

# 🔴 Unsafe deserialization
with open("data.pkl", "rb") as f:
    data = pickle.load(f)

print("Loaded data:", data)