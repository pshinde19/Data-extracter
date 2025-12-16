import pandas as pd
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import random
from faker import Faker
from datetime import datetime, timedelta

# --- Configuration ---

SCHEMA_DICT = {
    "Customers": ["CustomerID", "FirstName", "LastName", "Email", "Phone", "Age", "Address", "City", "Country", "JoinDate"],
    "Products": ["ProductID", "ProductName", "Category", "Price", "StockQuantity", "SupplierID", "Manufacturer", "Weight", "ExpiryDate", "IsActive"],
    "Orders": ["OrderID", "CustomerID", "OrderDate", "TotalAmount", "ShippingAddress", "City", "PostalCode", "Status", "PaymentMethod", "DeliveryDate"],
    "Employees": ["EmployeeID", "FirstName", "LastName", "Position", "Department", "Salary", "HireDate", "Email", "Phone", "ManagerID"],
    "Suppliers": ["SupplierID", "CompanyName", "ContactName", "Address", "City", "Country", "Phone", "Email", "ProductCategory", "Rating"],
    "Categories": ["CategoryID", "CategoryName", "Description", "ParentCategoryID", "CreatedDate", "UpdatedDate", "ImageURL", "SortOrder", "IsActive", "ProductCount"],
    "Payments": ["PaymentID", "OrderID", "PaymentDate", "Amount", "PaymentMethod", "TransactionID", "Status", "CardLastFour", "Currency", "RefundAmount"],
    "Inventory": ["InventoryID", "ProductID", "WarehouseID", "Quantity", "MinStockLevel", "ReorderPoint", "LastUpdated", "Location", "BatchNumber", "ExpiryDate"],
    "Reviews": ["ReviewID", "ProductID", "CustomerID", "Rating", "Comment", "ReviewDate", "HelpfulCount", "VerifiedPurchase", "Title", "Response"],
    "Shipments": ["ShipmentID", "OrderID", "Carrier", "TrackingNumber", "ShipDate", "EstimatedDelivery", "ActualDelivery", "ShippingCost", "Status", "DeliveryAddress"]
}

app = Flask(__name__)
CORS(app)
fake = Faker()

# --- Data Generation Logic ---

def generate_dummy_data(table_name, columns, num_rows=10):
    data = []
    
    STATUSES = ['Pending', 'Shipped', 'Delivered', 'Cancelled']
    PAYMENT_METHODS = ['Credit Card', 'PayPal', 'Transfer']
    CATEGORIES = ['Electronics', 'Books', 'Clothing', 'Home Goods']
    pk_name = columns[0] if columns else 'ID'
    
    for i in range(1, num_rows + 1):
        row = {}
        for col in columns:
            col_lower = col.lower()
            
            if 'id' in col_lower:
                if col == pk_name:
                    row[col] = i 
                elif 'customerid' in col_lower:
                    row[col] = random.randint(1001, 1100)
                elif 'productid' in col_lower:
                    row[col] = random.randint(2001, 2100)
                elif 'orderid' in col_lower:
                    row[col] = random.randint(3001, 3100)
                else:
                    row[col] = random.randint(100, 999)

            elif 'name' in col_lower or 'title' in col_lower:
                row[col] = fake.catch_phrase() if 'product' in col_lower or 'company' in col_lower else fake.name()
            elif 'first' in col_lower:
                row[col] = fake.first_name()
            elif 'last' in col_lower:
                row[col] = fake.last_name()
            elif 'email' in col_lower:
                row[col] = fake.email()
            elif 'phone' in col_lower:
                row[col] = fake.phone_number()
            elif 'address' in col_lower or 'location' in col_lower:
                row[col] = fake.street_address()
            elif 'city' in col_lower:
                row[col] = fake.city()
            elif 'country' in col_lower:
                row[col] = fake.country()
            elif 'position' in col_lower:
                row[col] = fake.job()
            elif 'department' in col_lower:
                row[col] = random.choice(['Sales', 'Marketing', 'IT', 'HR', 'Finance'])
            elif 'description' in col_lower or 'comment' in col_lower:
                row[col] = fake.sentence(nb_words=6)
            
            elif 'age' in col_lower:
                row[col] = random.randint(18, 65)
            elif 'price' in col_lower or 'amount' in col_lower or 'cost' in col_lower:
                row[col] = round(random.uniform(5.0, 500.0), 2)
            elif 'salary' in col_lower:
                row[col] = random.randint(40000, 150000)
            elif 'stock' in col_lower or 'quantity' in col_lower:
                row[col] = random.randint(0, 1000)
            elif 'rating' in col_lower:
                row[col] = round(random.uniform(1.0, 5.0), 1)
            elif 'count' in col_lower:
                 row[col] = random.randint(1, 200)

            elif 'date' in col_lower:
                if 'join' in col_lower or 'hire' in col_lower:
                    row[col] = fake.date_this_year().isoformat()
                elif 'delivery' in col_lower:
                    row[col] = (datetime.now() + timedelta(days=random.randint(1, 10))).date().isoformat()
                elif 'expiry' in col_lower:
                    row[col] = (datetime.now() + timedelta(days=random.randint(30, 365))).date().isoformat()
                else: 
                    row[col] = fake.date_this_month().isoformat()
            
            elif 'status' in col_lower:
                row[col] = random.choice(STATUSES)
            elif 'method' in col_lower:
                row[col] = random.choice(PAYMENT_METHODS)
            elif 'category' in col_lower:
                row[col] = random.choice(CATEGORIES)
            elif 'active' in col_lower:
                row[col] = random.choice([True, False])
            
            else:
                row[col] = "N/A"

        data.append(row)
    return data

# --- Routes ---

@app.route('/api/schema', methods=['GET'])
def get_schema():
    return jsonify({
        "status": "success",
        "data": SCHEMA_DICT,
    })

@app.route('/api/download/csv/<table_name>', methods=['GET'])
def download_csv(table_name):
    if table_name not in SCHEMA_DICT:
        return jsonify({
            "status": "error",
            "message": f"Table '{table_name}' not found."
        }), 404

    columns = SCHEMA_DICT[table_name]
    data_rows = generate_dummy_data(table_name, columns, num_rows=10)
    df = pd.DataFrame(data_rows, columns=columns)
    
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'{table_name}_sample_data.csv',
        mimetype='text/csv'
    )

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
