# 🛡️ ChurnGuard AI - An AI Agent for E-commerce Customer Retention  

**ChurnGuard AI** is a powerful web application that functions as an intelligent agent to help e-commerce businesses proactively identify and retain customers at risk of churning. It combines a robust machine learning model for prediction with a Large Language Model (LLM) to generate personalized, actionable retention strategies.  

---

## ✨ Features  

### 🤖 Dual-AI System  
- **Predictive ML Model**: Utilizes a pre-trained **XGBoost model** to accurately predict the likelihood of a customer churning based on their data.  
- **Generative AI Strategist**: Leverages a powerful **LLM (`openai/gpt-oss-20b`)** to generate creative and personalized retention strategies for at-risk customers.  

### 👤 Single Customer Analysis  
- Enter the details of a single customer to get an instant churn prediction and tailored AI-powered recommendations.  

### 📁 Batch File Processing  
- Upload a `.csv` or `.xlsx` file containing data for multiple customers to efficiently identify all potential churners in a single operation.  

### 🔑 User-Provided API Keys  
- Users must provide their own **Groq API key**, ensuring the security and privacy of the developer's credentials.  

### 🎨 Interactive & Responsive UI  
- Sleek, modern interface built with **HTML, Tailwind CSS, and vanilla JavaScript**.  
- Resizable and collapsible sidebar for a flexible user experience.  
- Dynamic charts and result cards to beautifully visualize the analysis output.  

---

## 🛠️ Architecture  

The application is built with a **decoupled frontend and backend architecture**.  

### Frontend  
- **`index.html`**: A single-page application serving as the user interface.  
- **Styling**: Tailwind CSS for a modern, utility-first design.  
- **Logic**: Vanilla JavaScript handles user interactions, API calls to the backend, and dynamic rendering of results.  

### Backend  
- **Framework**: FastAPI provides a high-performance asynchronous API.  
- **Prediction Model**: An **XGBoost classifier (`xgb_churn_model.pkl`)** trained for churn prediction. A **StandardScaler (`scalar.joblib`)** is used for data preprocessing.  
- **AI Recommendations**: Integrates with the **Groq API** to get personalized retention strategies from the `openai/gpt-oss-20b` model.  
- **Dependencies**: All required Python packages are listed in `requirements.txt`.  

---

## 🚀 Getting Started  

Follow these instructions to set up and run the project locally.  

### Prerequisites  
- Python **3.8+**  
- A web browser (e.g., Chrome, Firefox)  
- A **Groq API key** for generating AI recommendations  

### 1. Clone the Repository  
```bash
git clone https://github.com/Kalyan9639/churnguard-ai.git
cd churnguard-ai
```


### 2. Set Up the Backend

Create and activate a virtual environment:

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

⚠️ Important: Place the model and scaler files (xgb_churn_model.pkl and scalar.joblib) inside a churn_prediction_api/ directory at the root of the project.

### 3. Running the Application

Start the Backend Server:
```bash
uvicorn ai_model:app --reload
```

The backend will now be running at: http://127.0.0.1:8000

**Launch the Frontend:**
Simply open the ```index.html``` file in your web browser.
---
## 📖 How to Use

1. **Open the Application**  
   Launch `index.html` in your browser.

2. **Enter Your API Key**  
   In the top-left corner, enter your valid **Groq API key**.

3. **Choose an Analysis Method**
   - **Single Customer**: Fill in the customer's details in the form → click **"Analyze Churn Risk"**.
   - **Batch File**: Click the **"Batch File"** tab → upload a `.csv` or `.xlsx` file → click **"Process Batch File"**.

4. **View the Results**
   - Predictions will appear on the right-hand side.
   - If a customer is likely to churn, the AI provides **personalized retention strategies**.

---

## 📝 API Endpoints

### `POST /predict`
- **Description**: Predicts churn for a single customer and returns AI recommendations if churn is likely.  
- **Body**: JSON object containing the customer's feature data and `api_key`.

```json
{
  "api_key": "YOUR_GROQ_API_KEY",
  "customer_id": "12345",
  "tenure": 12,
  "avg_order_value": 45.67,
  "num_orders": 3
}
```

### POST /predict-file

- **Description**: Predicts churn for a batch of customers from an uploaded file.
- **Body**: multipart/form-data request with a .csv or .xlsx file (include api_key as a form field).
