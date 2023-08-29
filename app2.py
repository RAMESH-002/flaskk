# 1. Import Libraries and Initialize App
import os
import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 2. Global variables and utility functions
users_file = "C:\\Users\\Ramesh\\Desktop\\user_details.csv"

# Create users_file if it doesn't exist
if not os.path.exists(users_file):
    with open(users_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'name', 'email', 'phone', 'age', 'password_hash'])

# Averages for Heart Disease (1) and No Heart Disease (0)
averages = {
    "Age": [58.4, 52.2],
    "Chest Pain": [1.5, 1],
    "BP": [167.5, 140.8],
    "Cholesterol": [234, 203.9],
    "Fasting Blood Sugar": [143.4, 79.9],
    "Resting ECG": [1.17, 1.42],
    "Thalach": [171.3, 139.5],
    "Exang": [0.78, 0],
    "Oldpeak": [2.8, 0],
    "Slope": [1.33, 1.17],
    "Ca": [1, 0.22],
    "Thal": [1.22, 0.78]
}
columns = ["Age", "Gender"] + [col for col in averages if col != "Age"]

data = pd.read_csv("C:\\Users\\Ramesh\\Desktop\\heart2.csv")
X = data.iloc[:, :-1]  
y = data.iloc[:, -1]

# Find-S algorithm
def find_s(training_data, target):
    hypothesis = ['0'] * len(training_data[0])
    for i, instance in enumerate(training_data):
        if target[i] == "Yes":
            for j, attr in enumerate(instance):
                if hypothesis[j] == '0':
                    hypothesis[j] = attr
                elif hypothesis[j] != attr:
                    hypothesis[j] = '?'
    return hypothesis


def predict(instance):
    attributes_without_gender = [instance[i] for i, col in enumerate(columns) if col in averages]
    
    diff_heart_disease = sum([abs(val - averages[col][0]) for col, val in zip(averages, attributes_without_gender)])
    diff_no_heart_disease = sum([abs(val - averages[col][1]) for col, val in zip(averages, attributes_without_gender)])
    
    if diff_heart_disease < diff_no_heart_disease:
        return "Yes"
    else:
        return "No"
    # ... Your predict function here

# 3. Routes and their functions

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    age = request.form['age']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if passwords match
    if password != confirm_password:
        flash("Passwords do not match!")
        return redirect(url_for('welcome'))

    # Check if user already exists
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == username:
                flash("User already exists!")
                return redirect(url_for('welcome'))

    # Add user to CSV
    with open(users_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, name, email, phone, age, password])  # Storing plain password

    flash("User registered successfully!")
    return redirect(url_for('welcome'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"Logging in with: {username}, {password}")  # DEBUG

    # Check user credentials
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            print(f"Checking against: {row[0]}, {row[5]}")  # DEBUG
            if row and row[0] == username and row[5] == password: 
                session['user'] = username
                return redirect(url_for('predict'))

    flash("Invalid credentials!")
    return redirect(url_for('welcome'))

@app.before_request
def check_user():
    # Check if user is accessing protected route
    if request.endpoint in ['predict', 'result']:
        if 'user' not in session:
            return "Please log in first!"
app.secret_key = 'your_secret_key'

@app.route('/predict', methods=['GET', 'POST'])
def index():
    prediction = None

    if request.method == 'POST':
        new_instance = [float(request.form[col]) if col in averages else request.form[col] for col in columns]
        prediction = predict(new_instance)

    return render_template('index.html', columns=columns, averages=averages, prediction=prediction)

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        new_instance = [float(request.form[col]) if col in averages else request.form[col] for col in columns]
        prediction = predict(new_instance)
        return render_template('result.html', prediction=prediction)

# 4. Main Execution
if __name__ == '__main__':
    app.run(debug=True)
