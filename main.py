import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import os
                                  
# Simulated customer data
customers = {
    'CustomerID': [1, 2, 3, 4, 5],
    'CreditScore': [700, 650, 800, 720, 680],
    'Salary': [45000, 60000, 120000, 80000, 55000],
    'Age': [25, 34, 45, 29, 40],
    'ExistingLoans': [1, 2, 0, 1, 1],
}

# Simulated product data
products = {
    'ProductID': [101, 102, 103],
    'ProductName': ['Credit Card', 'Personal Loan', 'Investment Account'],
    'MinCreditScore': [600, 650, 750],
    'MinSalary': [30000, 40000, 70000],
    'IdealAgeRange': ['18-60', '25-55', '30-65'],  # Represented as strings
    'Category': ['Credit', 'Loan', 'Investment'],  # Product type
}

# Load data into DataFrames
customers_df = pd.DataFrame(customers)
products_df = pd.DataFrame(products)


# Convert 'IdealAgeRange' to numeric bounds
def extract_age_bounds(row):
    return list(map(int, row.split('-')))


products_df[['MinAge', 'MaxAge']] = products_df['IdealAgeRange'].apply(extract_age_bounds).to_list()

# Normalize customer data for compatibility with product requirements
scaler = MinMaxScaler()
normalized_customers = customers_df[['CreditScore', 'Salary', 'Age', 'ExistingLoans']]
normalized_customers = pd.DataFrame(
    scaler.fit_transform(normalized_customers),
    columns=['CreditScore', 'Salary', 'Age', 'ExistingLoans']
)
normalized_customers['CustomerID'] = customers_df['CustomerID']


# Function to match products to customers with percentage and descriptive categories
def match_products_to_customers(customers, products, top_n=2):
    recommendations = []
    for _, customer in customers.iterrows():
        customer_id = customer['CustomerID']
        scores = []

        for _, product in products.iterrows():
            # Calculate compatibility score based on product requirements
            score = 0
            if customer['CreditScore'] >= product['MinCreditScore'] / 850:  # Normalize credit score range
                score += 0.4  # Higher weight for credit score match
            if customer['Salary'] >= product['MinSalary'] / 150000:  # Normalize salary range
                score += 0.3
            if product['MinAge'] <= customer['Age'] * 100 <= product['MaxAge']:  # Check age range match
                score += 0.2
            if product['Category'] == 'Loan' and customer['ExistingLoans'] < 3:  # Limit loans
                score += 0.1

            # Convert score to percentage
            percentage_score = round(score * 100, 1)

            # Assign descriptive category
            if percentage_score >= 80:
                category = "Excellent Match"
            elif percentage_score >= 60:
                category = "Good Match"
            elif percentage_score >= 40:
                category = "Moderate Match"
            else:
                category = "Low Match"

            scores.append((product['ProductID'], product['ProductName'], percentage_score, category))

        # Sort scores and get top N
        top_recommendations = sorted(scores, key=lambda x: x[2], reverse=True)[:top_n]
        recommendations.append({'CustomerID': customer_id, 'Recommendations': top_recommendations})

    return recommendations


# Generate recommendations
recommendations = match_products_to_customers(normalized_customers, products_df)

# Display recommendations
for rec in recommendations:
    print(f"\nCustomer {rec['CustomerID']} Recommendations:")
    for product in rec['Recommendations']:
        print(f"  - {product[1]}: {product[2]}% ({product[3]})")


# Ensure the 'visualizations' directory exists
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# Customer Attribute Distribution: Salary and Credit Score
def plot_customer_attributes(customers_df):
    # Plot salary distribution
    plt.figure(figsize=(8, 5))
    plt.bar(customers_df['CustomerID'], customers_df['Salary'], color='skyblue')
    plt.title('Customer Salary Distribution')
    plt.xlabel('CustomerID')
    plt.ylabel('Salary')
    plt.xticks(customers_df['CustomerID'])
    plt.savefig('visualizations/salary_plot.png')  # Save the chart
    plt.show()  # Show the chart

    # Plot credit score distribution
    plt.figure(figsize=(8, 5))
    plt.bar(customers_df['CustomerID'], customers_df['CreditScore'], color='lightgreen')
    plt.title('Customer Credit Score Distribution')
    plt.xlabel('CustomerID')
    plt.ylabel('Credit Score')
    plt.xticks(customers_df['CustomerID'])
    plt.savefig('visualizations/credit_score_plot.png')  # Save the chart
    plt.show()  # Show the chart

# Product Recommendation Distribution
def plot_recommendation_distribution(recommendations):
    product_counts = {}
    for rec in recommendations:
        for product in rec['Recommendations']:
            product_name = product[1]
            product_counts[product_name] = product_counts.get(product_name, 0) + 1

    # Plot pie chart
    labels = list(product_counts.keys())
    sizes = list(product_counts.values())
    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['gold', 'lightblue', 'lightcoral'])
    plt.title('Recommended Product Distribution')
    plt.axis('equal')
    plt.savefig('visualizations/recommendation_pie.png')  # Save the chart
    plt.show()  # Show the chart

# Generate visualizations
plot_customer_attributes(customers_df)
plot_recommendation_distribution(recommendations)