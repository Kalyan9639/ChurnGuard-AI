import os
import io
import httpx
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# 1. Load the model and the scaler
try:
    # Ensure the model and scaler are in a subdirectory as specified
    model_path = os.path.join("models", "xgb_churn_model.pkl")
    scaler_path = os.path.join("models", "scalar.joblib")
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
except FileNotFoundError as e:
    raise RuntimeError(f"Model or scaler file not found. Please ensure '{os.path.basename(e.filename)}' is in the 'churn_prediction_api' directory.") from e

# Define the feature names in the correct order
FEATURE_NAMES = [
    'Tenure', 'PreferredLoginDevice', 'CityTier', 'WarehouseToHome',
    'PreferredPaymentMode', 'Gender', 'HourSpendOnApp', 'NumberOfDeviceRegistered',
    'PreferedOrderCat', 'SatisfactionScore', 'MaritalStatus', 'NumberOfAddress',
    'Complain', 'OrderAmountHikeFromlastYear', 'CouponUsed', 'OrderCount',
    'DaySinceLastOrder', 'CashbackAmount'
]

# --- Determine Top 10 Most Important Features from the Model ---
try:
    importances = model.feature_importances_
    top_10_indices = np.argsort(importances)[::-1][:10]
    TOP_10_FEATURES = [FEATURE_NAMES[i] for i in top_10_indices]
    print(f"Top 10 features for personalized recommendations: {TOP_10_FEATURES}")
except Exception as e:
    print(f"Could not determine feature importances, using default list. Error: {e}")
    TOP_10_FEATURES = ['Tenure', 'Complain', 'SatisfactionScore', 'DaySinceLastOrder', 'OrderCount', 'CashbackAmount', 'WarehouseToHome', 'HourSpendOnApp', 'CouponUsed', 'PreferedOrderCat']

# 2. Define a data model for single customer input
class Customer(BaseModel):
    api_key: str = Field(..., description="The user's Groq API key for AI recommendations.")
    Tenure: float
    PreferredLoginDevice: int
    CityTier: int
    WarehouseToHome: float
    PreferredPaymentMode: int
    Gender: int
    HourSpendOnApp: float
    NumberOfDeviceRegistered: int
    PreferedOrderCat: int
    SatisfactionScore: int
    MaritalStatus: int
    NumberOfAddress: int
    Complain: int
    OrderAmountHikeFromlastYear: float
    CouponUsed: float
    OrderCount: float
    DaySinceLastOrder: float
    CashbackAmount: float

# Mapping dictionaries
PreferredLoginDevice_map = {'Mobile Phone': 0, 'Phone': 0, 'Computer': 1}
PreferredPaymentMode_map = {'Debit Card': 1, 'UPI': 1, 'CC': 1, 'Cash on Delivery': 0, 'E wallet': 1, 'COD': 0, 'Credit Card': 1}
Gender_map = {'Female': 0, 'Male': 1}
PreferredOrderCat_map = {'Laptop & Accessory': 0, 'Mobile Phone': 0, 'Others': 3, 'Fashion': 1, 'Grocery': 2}
MaritalStatus_map = {'Single': 1, 'Divorced': 0, 'Married': 2}


# Initialize the FastAPI app
app = FastAPI(
    title="Customer Churn Prediction API",
    description="An API to predict customer churn and provide AI-powered retention strategies."
)

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- AI Recommendation Helper Function ---
async def get_retention_recommendations(customer_data: pd.DataFrame, api_key: str):
    if not api_key:
        return "Error: API key was not provided in the request."
    
    customer_profile = customer_data[TOP_10_FEATURES].to_dict(orient='records')[0]
    prompt = f"""
    You are a world-class e-commerce retention strategist. A customer with the following profile is predicted to churn.
    Provide a list of 5-8 concrete, actionable, and personalized bullet points to prevent them from churning.
    Your response must only contain the bulleted list of recommendations.

    Customer Profile:
    """
    for feature, value in customer_profile.items():
        prompt += f"- {feature}: {value}\n"
    prompt += "\nRecommendations:"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-20b", # Using the specified model
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500 # Adjusted for concise recommendations
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            recommendations = [rec.strip().lstrip('-* ').capitalize() for rec in content.split('\n') if rec.strip()]
            return recommendations
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "Error: Authentication failed. The provided API key is invalid or has expired."
        elif e.response.status_code == 429:
             return "Error: Rate limit exceeded for the API key. Please try again later."
        return f"Error: The AI service returned an error (Status {e.response.status_code}). Please check the server logs."
    except httpx.RequestError:
        return "Error: Could not connect to the AI recommendation service. Please check your network connection."
    except Exception:
        return "Error: An unexpected error occurred while generating AI recommendations."

@app.get("/")
def read_root():
    return {"message": "Welcome to the Customer Churn Prediction API!"}

@app.post("/predict")
async def predict_churn(customer_data: Customer):
    # API key is now a required field in the Customer model
    api_key = customer_data.api_key
    
    # Exclude the api_key before creating the DataFrame for the model
    df = pd.DataFrame([customer_data.model_dump(exclude={'api_key'})])
    df = df[FEATURE_NAMES] # Ensure column order
    
    df_scaled = scaler.transform(df)
    prediction = model.predict(df_scaled)[0]
    
    response_data = {}
    if prediction == 1:
        response_data["prediction"] = "The customer is likely to churn."
        recommendations = await get_retention_recommendations(df, api_key=api_key)
        response_data["retention_recommendations"] = recommendations
    else:
        response_data["prediction"] = "The customer is not likely to churn."
        response_data["retention_recommendations"] = "This customer appears loyal. Continue providing excellent service!"
        
    return response_data

@app.post("/predict-file")
async def predict_churn_from_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .csv or .xlsx file.")
    try:
        contents = await file.read()
        file_buffer = io.BytesIO(contents)

        df = pd.read_csv(file_buffer) if file.filename.endswith('.csv') else pd.read_excel(file_buffer)

        if 'CustomerID' not in df.columns:
            raise HTTPException(status_code=400, detail="The uploaded file must contain a 'CustomerID' column.")
        
        customer_ids = df['CustomerID']
        
        # Data Cleaning and Preprocessing
        for col in ['WarehouseToHome', 'CouponUsed', 'OrderCount', 'DaySinceLastOrder', 'CashbackAmount']:
            if col in df.columns:
                df[col].fillna(df[col].median(), inplace=True)
        
        df['PreferredLoginDevice'] = df['PreferredLoginDevice'].str.title().map(PreferredLoginDevice_map)
        df['PreferredPaymentMode'] = df['PreferredPaymentMode'].str.title().map(PreferredPaymentMode_map)
        df['Gender'] = df['Gender'].str.title().map(Gender_map)
        df['PreferedOrderCat'] = df['PreferedOrderCat'].str.title().map(PreferredOrderCat_map)
        df['MaritalStatus'] = df['MaritalStatus'].str.title().map(MaritalStatus_map)

        df_features = df[FEATURE_NAMES]
        df_scaled = scaler.transform(df_features)
        predictions = model.predict(df_scaled)
        
        churn_ids = customer_ids[predictions == 1].tolist()
        
        return {"no_of_customers_to_churn": len(churn_ids), "customers_likely_to_churn": churn_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during file processing: {str(e)}")

