import pandas as pd

test_data = {
    "Date": ["2025-07-01", "2025-07-02", "2025-07-02", "2025-07-03", "2025-07-03"],
    "Category": ["Food", "Transport", "Entertainment", "Food", "Utilities"],
    "Amount": [12.50, 3.20, 15.00, 8.90, 45.00],
    "Note": ["Lunch", "Bus fare", "Movie", "Dinner", "Electric bill"]
}

df = pd.DataFrame(test_data)
df.to_csv("expenses.csv", index=False)
print("Test data saved to 'expense_file'.")