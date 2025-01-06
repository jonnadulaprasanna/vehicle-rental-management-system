import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime
import base64


# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["vehicle_rental_system"]

# Collections
users = db["Users"]
customers = db["Customers"]
vehicles = db["Vehicles"]
rentals = db["Rentals"]
suppliers = db["Suppliers"]
payments = db["Payments"]

# Authentication
def authenticate(username, password):
    user = users.find_one({"username": username, "password": password})
    return user


# Admin: Manage Customers
def manage_customers():
    #add customer
    st.subheader("Add Customer")

    # Input fields for customer details
    customer_id = st.text_input("Customer ID (Unique)", key="customer_id")
    name = st.text_input("Customer Name", key="name")
    email = st.text_input("Customer Email", key="email")
    phone = st.text_input("Phone Number", key="phone")

    if st.button("Add Customer"):
        # Validation to ensure no empty fields
        if not customer_id or not name or not email or not phone:
            st.error("All fields are required. Please fill out all fields before submitting.")
        elif customers.find_one({"customer_id": customer_id}):
            st.error("A customer with this ID already exists.")
        else:
            # Insert into MongoDB
            customers.insert_one({
                "customer_id": customer_id,
                "name": name,
                "email": email,
                "phone": phone
            })
            st.success("Customer added successfully!")

    # Delete Customer
    st.write("### Delete Customer")
    cust_email_to_delete = st.text_input("Customer Email to Delete")
    if st.button("Delete Customer"):
        result = customers.delete_one({"email": cust_email_to_delete})
        if result.deleted_count > 0:
            st.success("Customer deleted successfully!")
        else:
            st.error("Customer not found.")
    # Update Customer
    st.write("### Update Customer Information")
    cust_email_to_update = st.text_input("Customer Email to Update")
    
    if cust_email_to_update:
        # Fetch customer by email to pre-fill fields for editing
        customer_to_update = customers.find_one({"email": cust_email_to_update})
        
        if customer_to_update:
            # Pre-fill the input fields with current customer data
            new_name = st.text_input("New Customer Name", value=customer_to_update["name"])
            new_email = st.text_input("New Customer Email", value=customer_to_update["email"])
            new_phone = st.text_input("New Phone Number", value=customer_to_update["phone"])

            if st.button("Update Customer"):
                # Update the customer in MongoDB
                updated_data = {}
                if new_name != customer_to_update["name"]:
                    updated_data["name"] = new_name
                if new_email != customer_to_update["email"]:
                    updated_data["email"] = new_email
                if new_phone != customer_to_update["phone"]:
                    updated_data["phone"] = new_phone

                if updated_data:
                    customers.update_one({"email": cust_email_to_update}, {"$set": updated_data})
                    st.success("Customer information updated successfully!")
                else:
                    st.warning("No changes were made.")
        else:
            st.error("Customer not found.")
    # View Customers in Table Format
    st.write("### All Customers")
    customers_data = list(customers.find({}, {"_id": 0}))  # Fetch data without the MongoDB ID field
    if customers_data:
        st.table(customers_data)  # Display data in table format
    else:
        st.write("No customers found.")

# Admin: Manage Vehicles
def manage_vehicles():
    st.subheader("Manage Vehicles")

    # Add Vehicle
    st.write("### Add Vehicle")
    vehicle_id = st.text_input("Vehicle ID (Unique)")
    vehicle_name = st.text_input("Vehicle Name")
    vehicle_type = st.text_input("Vehicle Type (e.g., car, truck)")
    vehicle_brand = st.text_input("Brand")
    availability_status = st.selectbox("Availability Status", ["Available", "Unavailable"])
    if st.button("Add Vehicle"):
        if vehicles.find_one({"vehicle_id": vehicle_id}):
            st.error("A vehicle with this ID already exists.")
        else:
            vehicles.insert_one({
                "vehicle_id": vehicle_id,
                "vehicle_name": vehicle_name,
                "type": vehicle_type,
                "brand": vehicle_brand,
                "availability_status": availability_status
            })
            st.success("Vehicle added successfully!")

    # Update Vehicle Availability
    st.write("### Update Vehicle Availability")
    update_vehicle_id = st.text_input("Enter Vehicle ID to Update Availability")
    new_status = st.selectbox("New Availability Status", ["Available", "Unavailable"])
    if st.button("Update Vehicle Availability"):
        result = vehicles.update_one(
            {"vehicle_id": update_vehicle_id},
            {"$set": {"availability_status": new_status}}
        )
        if result.matched_count > 0:
            st.success("Vehicle availability updated successfully!")
        else:
            st.error("Vehicle not found.")

    # Delete Vehicle
    st.write("### Delete Vehicle")
    vehicle_id_to_delete = st.text_input("Vehicle ID to Delete")
    if st.button("Delete Vehicle"):
        result = vehicles.delete_one({"vehicle_id": vehicle_id_to_delete})
        if result.deleted_count > 0:
            st.success("Vehicle deleted successfully!")
        else:
            st.error("Vehicle not found.")
    #view tables
    st.write("### All Vehicles")
    vehicles_data = list(vehicles.find({}, {"_id": 0}))  # Exclude MongoDB ID from the output
    if vehicles_data:
        st.table(vehicles_data)  # Display vehicles in table format
    else:
        st.write("No vehicles found.")

# Admin: Manage Rentals
def manage_rentals():
    st.subheader("Add Rental Information")
    rental_id = st.text_input("Rental ID")
    customer_id = st.text_input("Customer ID")
    vehicle_id = st.text_input("Vehicle ID")
    no_of_days_rented = st.number_input("Number of Days Rented", min_value=1, step=1)

    if st.button("Add Rental"):
        if not rental_id or not customer_id or not vehicle_id:
            st.error("All fields are required.")
        if not customers.find_one({"customer_id": customer_id}):
            st.error("Customer ID does not exist. Please add the customer first.")
        elif not vehicles.find_one({"vehicle_id": vehicle_id}):
            st.error("Vehicle ID does not exist. Please add the vehicle first.")
        else:
            rental_data = {
                "rental_id": rental_id,
                "customer_id": customer_id,
                "vehicle_id": vehicle_id,
                "no_of_days_rented": no_of_days_rented
            }
            rentals.insert_one(rental_data)
            st.success("Rental information added successfully!")
    # View Rental Information
    st.subheader("View Rental Information")
    rentals_ = list(rentals.find())
    if rentals_:
        # Convert MongoDB records to a pandas DataFrame for better visualization
        rental_df = pd.DataFrame(rentals_)
        rental_df["_id"] = rental_df["_id"].astype(str)  # Convert ObjectId to string for display
        st.dataframe(rental_df)
    else:
        st.info("No rental records found.")
    # Update Rental Information
    st.subheader("Update Rental Information")
    rental_id_to_update = st.text_input("Enter Rental ID to Update")
    
    if rental_id_to_update:
        rental = rentals.find_one({"rental_id": rental_id_to_update})
        
        if rental:
            # Pre-fill the rental details in input fields for update
            new_customer_id = st.text_input("New Customer ID", value=rental["customer_id"])
            new_vehicle_id = st.text_input("New Vehicle ID", value=rental["vehicle_id"])
            new_no_of_days_rented = st.number_input("New Number of Days Rented", min_value=1, value=rental["no_of_days_rented"], step=1)

            if st.button("Update Rental"):
                # Update rental information in MongoDB
                updated_data = {}
                if new_customer_id != rental["customer_id"]:
                    updated_data["customer_id"] = new_customer_id
                if new_vehicle_id != rental["vehicle_id"]:
                    updated_data["vehicle_id"] = new_vehicle_id
                if new_no_of_days_rented != rental["no_of_days_rented"]:
                    updated_data["no_of_days_rented"] = new_no_of_days_rented

                if updated_data:
                    rentals.update_one({"rental_id": rental_id_to_update}, {"$set": updated_data})
                    st.success("Rental information updated successfully!")
                else:
                    st.warning("No changes were made to the rental information.")
        else:
            st.error(f"No rental found with ID '{rental_id_to_update}'.")
    # Delete Rental Information
    st.subheader("Delete Rental Information")
    delete_rental_id = st.text_input("Enter Rental ID to Delete")
    if st.button("Delete Rental"):
        if not delete_rental_id:
            st.error("Rental ID is required.")
        else:
            result = rentals.delete_one({"rental_id": delete_rental_id})
            if result.deleted_count > 0:
                st.success(f"Rental with ID '{delete_rental_id}' deleted successfully!")
            else:
                st.error(f"No rental found with ID '{delete_rental_id}'.")

# Admin: Manage Suppliers
def manage_suppliers():
    st.subheader("Manage Suppliers")

    # Add Supplier
    st.write("### Add Supplier")
    supplier_id = st.text_input("Supplier ID (Unique)")
    supplier_name = st.text_input("Supplier Name")
    contact_info = st.text_input("Contact Info (Phone Number)")
    email = st.text_input("Email Address")
    vehicle_id = st.text_input("Vehicle ID Provided by Supplier")

    if st.button("Add Supplier"):
        # Validate input fields
        if not supplier_id or not supplier_name or not contact_info or not email or not vehicle_id:
            st.error("All fields are required.")
        elif suppliers.find_one({"supplier_id": supplier_id}):
            st.error("A supplier with this ID already exists.")
        else:
            # Insert into MongoDB
            suppliers.insert_one({
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "contact_info": contact_info,
                "email": email,
                "vehicle_id": vehicle_id
            })
            st.success("Supplier added successfully!")

    # View Suppliers
    st.write("### All Suppliers")
    suppliers_data = list(suppliers.find({}, {"_id": 0}))  # Exclude MongoDB ID from the output
    if suppliers_data:
        st.table(suppliers_data)  # Display suppliers in table format
    else:
        st.write("No suppliers found.")
    #update
    st.write("### Update Supplier Information")
    supplier_id_to_update = st.text_input("Enter Supplier ID to Update")
    
    if supplier_id_to_update:
        supplier = suppliers.find_one({"supplier_id": supplier_id_to_update})
        
        if supplier:
            # Pre-fill the supplier details in input fields for update
            new_supplier_name = st.text_input("New Supplier Name", value=supplier["supplier_name"])
            new_contact_info = st.text_input("New Contact Info (Phone Number)", value=supplier["contact_info"])
            new_email = st.text_input("New Email Address", value=supplier["email"])
            new_vehicle_id = st.text_input("New Vehicle ID Provided by Supplier", value=supplier["vehicle_id"])

            if st.button("Update Supplier"):
                # Update supplier information in MongoDB
                updated_data = {}
                if new_supplier_name != supplier["supplier_name"]:
                    updated_data["supplier_name"] = new_supplier_name
                if new_contact_info != supplier["contact_info"]:
                    updated_data["contact_info"] = new_contact_info
                if new_email != supplier["email"]:
                    updated_data["email"] = new_email
                if new_vehicle_id != supplier["vehicle_id"]:
                    updated_data["vehicle_id"] = new_vehicle_id

                if updated_data:
                    suppliers.update_one({"supplier_id": supplier_id_to_update}, {"$set": updated_data})
                    st.success("Supplier information updated successfully!")
                else:
                    st.warning("No changes were made to the supplier information.")
        else:
            st.error(f"No supplier found with ID '{supplier_id_to_update}'.")
    # Delete Supplier
    st.write("### Delete Supplier")
    supplier_id_to_delete = st.text_input("Supplier ID to Delete")
    if st.button("Delete Supplier"):
        result = suppliers.delete_one({"supplier_id": supplier_id_to_delete})
        if result.deleted_count > 0:
            st.success("Supplier deleted successfully!")
        else:
            st.error("Supplier not found.")

def manage_payments():

    st.subheader("Manage Payments")

    # Add Payment
    st.write("### Add Payment")
    payment_id = st.text_input("Payment ID (Unique)")
    rental_id = st.text_input("Rental ID", key="rental_id_input")
    customer_id = st.text_input("Customer ID",key="customer_id_input")
    amount = st.number_input("Payment Amount", min_value=0.0, step=0.01)
    payment_date = st.date_input("Payment Date")
    payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "PayPal", "Cash"])
    status = st.selectbox("Payment Status", ["Paid", "Pending"])

    if st.button("Add Payment"):
        if payments.find_one({"payment_id": payment_id}):
            st.error("A payment with this ID already exists.")
        if not customers.find_one({"customer_id": customer_id}):
            st.error("Customer ID does not exist. Please add the customer first.")
        elif not rentals.find_one({"rental_id": rental_id}):
            st.error("Rental ID does not exist. Please add the rental first.")
        else:
            payments.insert_one({
                "payment_id": payment_id,
                "rental_id": rental_id,
                "customer_id": customer_id,
                "amount": amount,
                "payment_date": str(payment_date),
                "payment_method": payment_method,
                "status": status
            })
            st.success("Payment added successfully!")

    # View Payments
    st.write("### All Payments")
    payments_data = list(payments.find({}, {"_id": 0}))  # Fetch all payment data
    if payments_data:
        st.table(payments_data)  # Display payments in table format
    else:
        st.write("No payments found.")


    # Update Payment Status
    st.write("### Update Payment Status")
    update_payment_id = st.text_input("Enter Payment ID to Update Status")
    new_status = st.selectbox("New Payment Status", ["Paid", "Pending"], key="status_update")
    if st.button("Update Payment Status"):
        result = payments.update_one(
            {"payment_id": update_payment_id},
            {"$set": {"status": new_status}}
        )
        if result.matched_count > 0:
            st.success("Payment status updated successfully!")
        else:
            st.error("Payment not found.")
    # Delete Payment
    st.write("### Delete Payment")
    payment_id_to_delete = st.text_input("Payment ID to Delete", key="delete_payment")
    if st.button("Delete Payment"):
        result = payments.delete_one({"payment_id": payment_id_to_delete})
        if result.deleted_count > 0:
            st.success("Payment deleted successfully!")
        else:
            st.error("Payment not found.")


# Function to show total payments over time
def total_payments_over_time():
    payments_data = list(payments.find({}, {"_id": 0, "payment_date": 1, "amount": 1}))
    df = pd.DataFrame(payments_data)

    # Convert payment_date to datetime format
    df['payment_date'] = pd.to_datetime(df['payment_date'], format="ISO8601")
    

    # Group by date and sum payments
    daily_payments = df.groupby(df['payment_date'].dt.date)['amount'].sum().reset_index()

    # Plotting
    fig = px.line(daily_payments, x='payment_date', y='amount', title="Total Payments Over Time")
    st.plotly_chart(fig)

# Function to show supplier distribution (count of suppliers by vehicle)
def supplier_distribution():
    suppliers_data = list(suppliers.find({}, {"_id": 0, "vehicle_id": 1}))
    vehicle_ids = [supplier['vehicle_id'] for supplier in suppliers_data]

    # Get vehicle names
    vehicles_data = list(vehicles.find({"vehicle_id": {"$in": vehicle_ids}}, {"_id": 0, "vehicle_name": 1}))
    vehicle_names = [vehicle['vehicle_name'] for vehicle in vehicles_data]

    # Create DataFrame for plotting
    df = pd.DataFrame(vehicle_names, columns=["Vehicle Name"])

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Vehicle Name', order=df['Vehicle Name'].value_counts().index)
    plt.xticks(rotation=45)
    plt.title('Supplier Distribution by Vehicle')
    st.pyplot(plt)


def fetch_customer_details(email):
    # Fetch the customer from the 'Customers' collection using the email
    customer = customers.find_one({"email": email})
    
    if customer:
        # Fetch the rental details based on customer_id (assuming customer rents only one vehicle for simplicity)
        rental = rentals.find_one({"customer_id": customer["customer_id"]})
        
        if rental:
            # Fetch the payment details for the rental
            payment = payments.find_one({"rental_id": rental["rental_id"]})
            vehicle = vehicles.find_one({"vehicle_id": rental["vehicle_id"]})  # Fetch vehicle details from rental's vehicle_id
            
            if vehicle:
                # Fetch supplier details based on vehicle's supplier_id
                supplier = suppliers.find_one({"vehicle_id": vehicle["vehicle_id"]})
            
            return customer, rental, payment, vehicle, supplier
    
    # Return None for each variable if no data is found
    return None, None, None, None, None



def customer_dashboard():
    # Customer Dashboard UI
    st.title("Customer Dashboard")

    # Get the logged-in customer's email (stored in session state after login)
    #Query3 and Query4
    customer_email = st.session_state.get("username", None)  # Assuming email is stored in session state
    if customer_email:
        customer, rental, payment, vehicle, supplier = fetch_customer_details(customer_email)

        if customer:
            # Display customer details
            st.subheader(f"Customer Details for {customer['name']}")
            st.write(f"Customer ID: {customer['customer_id']}")
            st.write(f"Name: {customer['name']}")
            st.write(f"Email: {customer['email']}")
            st.write(f"Phone: {customer['phone']}")

            # Create tabs for different sections
            tabs = ["Rental and Payment Details", "Rented Vehicle and Supplier Details"]
            selected_tab = st.radio("Select a tab", tabs)

            if selected_tab == "Rental and Payment Details":
                if rental and payment:
                    # Display rental details
                    st.subheader(f"Rental Details for Rental ID {rental['rental_id']}")
                    st.write(f"Rental ID: {rental['rental_id']}")
                    st.write(f"No. of Days Rented: {rental['no_of_days_rented']}")

                    # Display payment details
                    st.subheader(f"Payment Details for Rental ID {rental['rental_id']}")
                    st.write(f"Payment ID: {payment['payment_id']}")
                    st.write(f"Amount: ${payment['amount']}")
                    st.write(f"Payment Date: {payment['payment_date']}")
                    st.write(f"Payment Status: {payment['status']}")
                else:
                    st.write("No rental or payment history found .")
            
            elif selected_tab == "Rented Vehicle and Supplier Details":
                if rental:
                    if vehicle:
                        # Display rented vehicle details
                        st.subheader(f"Rented Vehicle Details for Rental ID {rental['rental_id']}")
                        st.write(f"Vehicle ID: {vehicle['vehicle_id']}")
                        st.write(f"Vehicle Name: {vehicle['vehicle_name']}")
                        st.write(f"Vehicle Type: {vehicle['type']}")
                        st.write(f"Vehicle Brand: {vehicle['brand']}")
                        st.write(f"availability status: {vehicle['availability_status']}")

                    if supplier:
                        # Display supplier details
                        st.subheader(f"Supplier Details for Rental ID {rental['rental_id']}")
                        st.write(f"Supplier ID: {supplier['supplier_id']}")
                        st.write(f"Supplier Name: {supplier['supplier_name']}")
                        st.write(f"Supplier Contact: {supplier['contact_info']}")
                        st.write(f"Supplier Email: {supplier['email']}")
                else:
                    st.write("No rental history found .")
        else:
            st.write("You don't have any rentals.")
    else:
        st.write("Please log in to view your details.")

#Query3
def view_pending_payments():
    """
    Display all pending payments along with customer and vehicle details.
    """
    st.subheader("Pending Payments with Customer and Vehicle Details")

    # Fetch pending payments
    pending_payments = list(payments.find({"status": "Pending"}))
    
    if pending_payments:
        # Initialize list to store results with customer and vehicle details
        pending_payment_details = []

        for payment in pending_payments:
            # Fetch customer details
            customer = customers.find_one({"customer_id": payment["customer_id"]})
            # Fetch rental information to get vehicle ID
            rental = rentals.find_one({"rental_id": payment["rental_id"]})
            # Fetch vehicle details using vehicle ID from rental
            vehicle = vehicles.find_one({"vehicle_id": rental["vehicle_id"]}) if rental else None

            if customer and vehicle:
                pending_payment_details.append({
                    "Payment ID": payment["payment_id"],
                    "Customer Name": customer["name"],
                    "Customer Email": customer["email"],
                    "Vehicle Name": vehicle["vehicle_name"],
                    "Amount": payment["amount"],
                    "Payment Date": payment["payment_date"],
                    "Payment Status": payment["status"]
                })

        # Display the pending payments with customer and vehicle details
        if pending_payment_details:
            st.table(pending_payment_details)
        else:
            st.write("No pending payments found.")
    else:
        st.write("No pending payments found.")
#Query4
def customers_rented_specific_vehicle():
    """
    Display customers who rented a specific vehicle along with their payment details.
    """
    st.subheader("Customers Who Rented a Specific Vehicle")

    # Input for vehicle_id to filter by
    vehicle_id_input = st.text_input("Enter Vehicle ID")

    if vehicle_id_input:
        # Fetch all rentals that include the given vehicle_id
        rentals_with_vehicle = rentals.find({"vehicle_id": vehicle_id_input})
        
        # Initialize list to store the customer and payment details
        customer_payment_details = []

        for rental in rentals_with_vehicle:
            # Fetch the payment details for each rental
            payments_for_rental = payments.find({"rental_id": rental["rental_id"]})
            
            for payment in payments_for_rental:
                # Fetch customer details using customer_id from payment
                customer = customers.find_one({"customer_id": payment["customer_id"]})
                
                if customer:
                    customer_payment_details.append({
                        "Customer Name": customer["name"],
                        "Customer Email": customer["email"],
                        "Rental ID": rental["rental_id"],
                        "Payment Amount": payment["amount"],
                        "Payment Status": payment["status"],
                        "Payment Date": payment["payment_date"],
                    })
        # Display the results
        if customer_payment_details:
            st.table(customer_payment_details)
        else:
            st.write("No customers found for this vehicle or no payments made yet.")
#Query 5
def get_vehicle_and_supplier_details():
    """
    Fetch and display vehicle and supplier details for a specific rental ID.
    """
    st.subheader("Vehicle and Supplier Details for Rental")

    # Input for Rental ID
    rental_id_input = st.text_input("Enter Rental ID to Fetch Details")

    if rental_id_input:
        # Fetch rental details using the Rental ID
        rental = rentals.find_one({"rental_id": rental_id_input})
        
        if rental:
            # Fetch vehicle details using vehicle_id from rental
            vehicle = vehicles.find_one({"vehicle_id": rental["vehicle_id"]}) if "vehicle_id" in rental else None
            # Fetch supplier details using supplier_id from rental
            supplier = suppliers.find_one({"vehicle_id": rental["vehicle_id"]}) if "vehicle_id" in rental else None

            # Display vehicle details
            if vehicle:
                st.write("### Vehicle Details")
                st.write(f"**Vehicle ID**: {vehicle.get('vehicle_id', 'N/A')}")
                st.write(f"**Vehicle Name**: {vehicle.get('vehicle_name', 'N/A')}")
                st.write(f"**Type**: {vehicle.get('type', 'N/A')}")
                st.write(f"**Brand**: {vehicle.get('brand', 'N/A')}")
                st.write(f"**Availability Status**: {vehicle.get('availability_status', 'N/A')}")
            else:
                st.write("No vehicle details found for this rental.")

            # Display supplier details
            if supplier:
                st.write("### Supplier Details")
                st.write(f"**Supplier ID**: {supplier.get('supplier_id', 'N/A')}")
                st.write(f"**Supplier Name**: {supplier.get('supplier_name', 'N/A')}")
                st.write(f"**Supplier Contact**: {supplier.get('contact_info', 'N/A')}")
                st.write(f"**Supplier Email**: {supplier.get('email', 'N/A')}")
            else:
                st.write("No supplier details found for this rental.")
        else:
            st.error("Rental ID not found. Please check and try again.")


def admin_dashboard():
    st.title("Admin Dashboard")
    st.write("Welcome, Admin!")
    # Tabs for managing collections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Manage Customers", "Manage Vehicles", "Manage Rentals", "Manage Supplier", "Manage Payments","Pending Payments", "Rental Specific Info", "Vizualisations"])
    with tab1:
        manage_customers()
    with tab2:
        manage_vehicles()
    with tab3:
        manage_rentals()
    with tab4:
        manage_suppliers()
    with tab5:
        manage_payments()
    with tab6:
        view_pending_payments()
    with tab7:
        customers_rented_specific_vehicle()
        get_vehicle_and_supplier_details()
    with tab8:
        total_payments_over_time()
        supplier_distribution() 
        
def set_background_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpeg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            height: 100vh;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Registration function
def register_user(username, password, role, email=None):
    # Check if the username (email) already exists
    if users.find_one({"username": username}):
        return "User already exists."
    # Insert new user into the database
    if role == "customer":
        # Insert only email and password for customers
        users.insert_one({"username": username, "password": password, "role": role, "email": email})
    else:
        users.insert_one({"username": username, "password": password, "role": role})
    return "User registered successfully!"

# Login page
def login():
    set_background_image("./background.jpg")
    st.title("Vehicle Rental Management System - Login")

    # Tabs for Login and Register
    tab1, tab2 = st.tabs(["Login", "Register"])

    # Login Tab
    with tab1:
        st.subheader("Login")
        username = st.text_input("Email", key="login_email")  # Use email for customer login
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = authenticate(username, password)
            if user:
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.success(f"Welcome {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials!")


    # Register Tab
    with tab2:
        st.subheader("Register")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("New Password", type="password", key="register_password")
        role = st.selectbox("Role", ["customer", "admin"], key="register_role")

        if st.button("Register"):
            if not new_email or not new_password:
                st.error("Email and Password are required.")
            else:
                result = register_user(new_email, new_password, role, new_email)
                if "successfully" in result:
                    st.success(result)
                else:
                    st.error(result)

# Main Application
def main():
    if "username" not in st.session_state:
        login()
    else:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
        role = st.session_state["role"]
        if role == "admin":
            admin_dashboard()
        elif role == "customer":
            customer_dashboard()
        else:
            st.error("Unknown role!")

if __name__ == "__main__":
    main()
