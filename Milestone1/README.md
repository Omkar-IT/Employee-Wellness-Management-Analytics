# Employee Wellness Management Analytics - Milestone 1

## Project Objective
This project implements a secure, production-ready User Authentication Module for the Employee Wellness Management Analytics platform. It provides a complete workflow including user registration, secure login, password recovery via OTP, and session management. 

## Technologies Used
* **Frontend UI:** Streamlit
* **Language:** Python
* **Database:** Neon PostgreSQL 
* **Security & Authentication:** `bcrypt` (password hashing), JSON Web Tokens (JWT) for session state
* **Email Service:** Google SMTP (OTP delivery)
* **Environment:** Google Colaboratory

## Google Colab Setup Instructions
1. Open `Authentication.ipynb` in Google Colab.
2. Run the first cell to install required dependencies: `!pip install streamlit psycopg2-binary bcrypt pyjwt`.
3. Add your **Neon PostgreSQL connection string**, **Google Email**, and **App Password** into the designated variables in the script.
4. Run the cell containing the Streamlit app code (which uses `%%writefile app.py`).
5. Run the final cell to execute `!npx localtunnel --port 8501`. 
6. Click the generated localtunnel URL and enter the endpoint IP password provided in the Colab output to view the live web application.
