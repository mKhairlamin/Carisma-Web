from flask import Flask, render_template, request, send_from_directory
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK with your service account credentials
cred = credentials.Certificate('C:/Users/User/Desktop/Carisma-v2.0.1/serviceAccountKey.json')  # Replace with the path to your downloaded service account file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://carisma-bc876-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# Function to load data from Firebase Realtime Database
def load_cars_data():
    ref = db.reference('Car')
    cars_data = ref.get()

    # Handle the case where cars_data is None
    if cars_data is None:
        return pd.DataFrame()

    # Check if cars_data is a dictionary of dictionaries and convert it to DataFrame
    if isinstance(cars_data, dict):
        cars_df = pd.DataFrame.from_dict(cars_data, orient='index')
    else:
        # If cars_data is not a dictionary, assume it's a list of dictionaries
        cars_df = pd.DataFrame(cars_data)

    # Ensure that the DataFrame has the expected columns
    required_columns = ['Price', 'Car_Category', 'Seats', 'Boot_Capacity', 'Fuel_Category', 'Total_Displacement_CC']
    for col in required_columns:
        if col not in cars_df.columns:
            cars_df[col] = 0  # Add missing columns with default values

    return cars_df

# Load the cars data
cars_df = load_cars_data()

# Function to get recommendations by cosine similarity
def get_recommendations_by_cosine_similarity(user_preferences):
    if cars_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame if cars_df is empty

    car_features = cars_df[['Price', 'Car_Category', 'Seats', 'Boot_Capacity', 'Fuel_Category', 'Total_Displacement_CC']]
    
    # Normalize feature vectors
    scaler = MinMaxScaler()
    normalized_car_features = scaler.fit_transform(car_features)
    normalized_user_preferences = scaler.transform(user_preferences)
    
    # Calculate cosine similarity between user preferences and car features
    similarity_scores = cosine_similarity(normalized_car_features, normalized_user_preferences)
    
    # Convert similarity scores to DataFrame and merge with cars_df
    similarity_df = pd.DataFrame(similarity_scores * 100, columns=['Similarity'], index=cars_df.index)
    similarity_df['Similarity'] = similarity_df['Similarity'].apply(lambda x: round(x, 2))  # Round to two decimal places
    recommendations = pd.concat([cars_df, similarity_df], axis=1)
    
    # Filter out cars with similarity score of 0 or less
    recommendations_filtered = recommendations[recommendations['Similarity'] > 0]
    
    # Sort recommendations by similarity score (higher score indicates closer match)
    recommendations_sorted = recommendations_filtered.sort_values(by='Similarity', ascending=False)
    return recommendations_sorted

# Function to get recommendations based on monthly payment
def get_recommendations_by_monthly_payment(user_salary, num_years, deposit_percentage, interest_percentage):
    monthly_payment = user_salary / 3
    interest_payment = interest_percentage / 100 * cars_df['Price'] * num_years
    down_payment = deposit_percentage * cars_df['Price']
    affordable_cars = cars_df[(cars_df['Price'] + interest_payment) - down_payment <= monthly_payment * (num_years * 12)]
    return affordable_cars

# Function to get recommendations based on desired amount
def get_recommendations_by_desired_amount(desired_amount, num_years, deposit_percentage, interest_percentage):
    interest_payment = interest_percentage / 100 * cars_df['Price'] * num_years
    down_payment = deposit_percentage * cars_df['Price']
    desired_payment = cars_df[(cars_df['Price'] + interest_payment) - down_payment <= desired_amount * (num_years * 12)]
    return desired_payment

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the findCar page
@app.route('/findCar')
def find_car():
    return render_template('findCar.html')

# Route for handling form submission
@app.route('/recommendations', methods=['POST'])
def recommendations():
    try:
        user_salary = float(request.form['salary'])
        desired_amount = float(request.form['amount'])
        num_years = int(request.form['years'])
        deposit_percentage = float(request.form['deposit'])
        interest_percentage = float(request.form['interest'])
        cc = float(request.form['cc'])
        luggage = int(request.form['boot'])
        fuel_tank_capacity = float(request.form['fuel'])
        car_type = float(request.form['car_type'])
        car_seats = int(request.form['car_seat'])

        user_payment = (user_salary / 3) * (num_years * 12)

        recommendations_monthly_payment = get_recommendations_by_monthly_payment(user_salary, num_years, deposit_percentage, interest_percentage)
        recommendations_sortedbyprice = recommendations_monthly_payment.sort_values(by='Price')

        recommendations_desired_amount = get_recommendations_by_desired_amount(desired_amount, num_years, deposit_percentage, interest_percentage)
        recommendations_sortedbydesired = recommendations_desired_amount.sort_values(by='Price')
        
        user_preferences = [[user_payment, car_type, car_seats, luggage, fuel_tank_capacity, cc]]
        recommendations_by_cosine_similarity = get_recommendations_by_cosine_similarity(user_preferences)

        user_desired = [[desired_amount * (num_years * 12), car_type, car_seats, luggage, fuel_tank_capacity, cc]]
        recommendations_by_desired = get_recommendations_by_cosine_similarity(user_desired)
        
        return render_template('recommendations.html', 
                               monthly_payment=user_salary / 3,
                               total_months=num_years * 12,
                               desired_payment=desired_amount,
                               interest_payment=interest_percentage,
                               down_payment=deposit_percentage,
                               recommendations_monthly_payment=recommendations_sortedbyprice,
                               recommendations_desired_amount=recommendations_sortedbydesired,
                               recommendations_cosine_similarity=recommendations_by_cosine_similarity,
                               recommendations_desired=recommendations_by_desired)
    except Exception as e:
        return str(e), 500  # Display the error message for debugging purposes

# Route to serve images from the assets folder
@app.route('/assets/<path:filename>')
def send_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

# Route for the car details page
@app.route('/car/<int:car_id>')
def car_details(car_id):
    car = cars_df[cars_df['ID'] == car_id].iloc[0]
    return render_template('car_details.html', car=car)

@app.route('/cars/<brand>')
def brand_cars(brand):
    # Ensure brand name is properly capitalized to match your dataset
    brand = brand.capitalize()
    
    # Filter cars by the selected brand
    filtered_cars = cars_df[cars_df['Brand'] == brand]
    
    # Sort the filtered cars by price in ascending order
    filtered_cars = filtered_cars.sort_values(by='Price')
    
    # Render the car list for the selected brand
    return render_template('brand_cars.html', brand=brand, cars=filtered_cars)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
