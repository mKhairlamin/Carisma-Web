from flask import Flask, render_template, request, send_from_directory
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os
import csv

app = Flask(__name__)

# Load the cars data
def load_cars_data(file_path):
    cars_df = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                row['Price (RM)'] = float(row['Price (RM)'])
                row['ID'] = int(row['ID'])
                row['Fuel_Consumption'] = float(row['Fuel_Consumption'])
                row['Seats'] = int(row['Seats'])
                row['Boot_Capacity'] = int(row['Boot_Capacity'])
                row['Total Displacement (CC)'] = int(row['Total Displacement (CC)'])
                row['Fuel_Tank'] = float(row['Fuel_Tank'])
                cars_df.append(row)
            except ValueError:
                continue
    return cars_df

cars_df = load_cars_data('Malaysian_Dataset_final.csv')

# Function to get recommendations by cosine similarity
def get_recommendations_by_cosine_similarity(user_preferences):
    if not cars_df:
        return []  # Return an empty list if cars_df is empty

    car_features = [
        [car['Price (RM)'], car['Fuel_Consumption'], car['Seats'], car['Boot_Capacity'], car['Total Displacement (CC)'], car['Fuel_Tank']]
        for car in cars_df
    ]
    
    # Normalize feature vectors
    scaler = MinMaxScaler()
    normalized_car_features = scaler.fit_transform(car_features)
    normalized_user_preferences = scaler.transform(user_preferences)
    
    # Calculate cosine similarity between user preferences and car features
    similarity_scores = cosine_similarity(normalized_car_features, normalized_user_preferences)
    
    # Create recommendations list with similarity score added
    recommendations = []
    for car, score in zip(cars_df, similarity_scores):
        car['Similarity'] = round(score[0] * 100, 2)  # Multiply by 100 to get percentage and round to 2 decimal places
        if car['Similarity'] > 0:
            recommendations.append(car)

    # Sort recommendations by similarity score (higher score indicates closer match)
    recommendations_sorted = sorted(recommendations, key=lambda x: x['Similarity'], reverse=True)
    return recommendations_sorted

# Function to get recommendations based on monthly payment
def get_recommendations_by_monthly_payment(user_salary, num_years, deposit_percentage, interest_percentage):
    monthly_payment = user_salary / 3
    affordable_cars = []
    for car in cars_df:
        interest_payment = interest_percentage / 100 * car['Price (RM)'] * num_years
        down_payment = deposit_percentage * car['Price (RM)']
        if (car['Price (RM)'] + interest_payment - down_payment) <= monthly_payment * (num_years * 12):
            affordable_cars.append(car)
    return affordable_cars

# Function to get recommendations based on desired amount
def get_recommendations_by_desired_amount(desired_amount, num_years, deposit_percentage, interest_percentage):
    affordable_cars = []
    for car in cars_df:
        interest_payment = interest_percentage / 100 * car['Price (RM)'] * num_years
        down_payment = deposit_percentage * car['Price (RM)']
        if (car['Price (RM)'] + interest_payment - down_payment) <= desired_amount * (num_years * 12):
            affordable_cars.append(car)
    return affordable_cars

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/findCar')
def find_car():
    return render_template('findCar.html')

@app.route('/recommendations', methods=['POST'])
def recommendations():
    user_salary = float(request.form['salary'])
    desired_amount = float(request.form['amount'])
    num_years = int(request.form['years'])
    deposit_percentage = float(request.form['deposit'])
    interest_percentage = float(request.form['interest'])
    cc = float(request.form['cc'])
    luggage = int(request.form['Boot_Capacity'])
    fuel_tank_capacity = float(request.form['Fuel_Tank'])
    fuel_consumption = float(request.form['Fuel_Consump'])
    car_seats = int(request.form['CarSeater'])

    user_payment = (user_salary / 3) * (num_years * 12)
    
    recommendations_monthly_payment = get_recommendations_by_monthly_payment(user_salary, num_years, deposit_percentage, interest_percentage)
    recommendations_monthly_payment_sorted = sorted(recommendations_monthly_payment, key=lambda x: x['Price (RM)'])
    
    recommendations_desired_amount = get_recommendations_by_desired_amount(desired_amount, num_years, deposit_percentage, interest_percentage)
    recommendations_desired_amount_sorted = sorted(recommendations_desired_amount, key=lambda x: x['Price (RM)'])

    user_preferences = [[user_payment, fuel_consumption, car_seats, luggage, cc, fuel_tank_capacity]]
    recommendations_by_cosine_similarity = get_recommendations_by_cosine_similarity(user_preferences)

    return render_template('recommendations.html',
                           monthly_payment=user_salary / 3,
                           total_months=num_years * 12,
                           desired_payment=desired_amount,
                           interest_payment=interest_percentage,
                           down_payment=deposit_percentage,
                           recommendations_monthly_payment=recommendations_monthly_payment_sorted,
                           recommendations_desired_amount=recommendations_desired_amount_sorted,
                           recommendations_cosine_similarity=recommendations_by_cosine_similarity)

@app.route('/assets/<path:filename>')
def send_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

@app.route('/car/<int:car_id>')
def car_details(car_id):
    car = next((car for car in cars_df if car['ID'] == car_id), None)
    return render_template('car_details.html', car=car)

@app.route('/cars/<brand>')
def brand_cars(brand):
    brand = brand.capitalize()
    filtered_cars = [car for car in cars_df if car['Brand'] == brand]
    filtered_cars_sorted = sorted(filtered_cars, key=lambda x: x['Price (RM)'])
    return render_template('brand_cars.html', brand=brand, cars=filtered_cars_sorted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
