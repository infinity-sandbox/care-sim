from fastapi import Depends, FastAPI, File, HTTPException, Header, Request, UploadFile
from fastapi.responses import JSONResponse
import jwt
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import json
from fastapi import APIRouter
from app.core.config import logger_settings
logger = logger_settings.get_logger(__name__)
import aiomysql
import asyncio

from app.services.auth_service import AuthDatabaseService
insight_router = APIRouter()

# Define Pydantic models for input data
class RevenueSource(BaseModel):
    id: Optional[str] = None
    sourceName: str
    monthlyAmount: float
    tag: str

class EmployeeExpense(BaseModel):
    id: Optional[str] = None
    expenseName: str
    monthlyAmount: float
    type: str
    hoursPerMonth: Optional[float] = None
    
class FacilityExpense(BaseModel):
    id: Optional[str] = None
    expenseName: str
    monthlyAmount: float
    type: str

class Classroom(BaseModel):
    id: Optional[str] = None
    name: str
    capacity: int
    ratio: float
    avgStudents: int

class OperatingDetail(BaseModel):
    operatingHours: float
    operatingDays: float

    
class Administrative(BaseModel):
    id: Optional[str] = None
    expenseName: str
    monthlyAmount: float
    type: str

class Supplies(BaseModel):
    id: Optional[str] = None
    expenseName: str
    monthlyAmount: float
    type: str
    
class Goals(BaseModel):
    id: Optional[str] = None
    goal: str
    targetPercentage: float

class DaycareInput(BaseModel):
    businessName: Optional[str] = "Unamed Daycare"
    revenueSources: List[RevenueSource] = []
    employees: List[EmployeeExpense] = []
    facilities: List[FacilityExpense] = []
    administrative: List[FacilityExpense] = []
    supplies: List[FacilityExpense] = []
    classrooms: List[Classroom] = []
    operatingHours: Optional[float] = 0.0  # Default operating hours
    operatingDays: Optional[float] = 0.0  # Default operating days
    # operatingDetails: List[OperatingDetail] = []
    goals: List[Goals] = []

    
# Function to generate insights using OpenAI
async def generate_daycare_insights(data: DaycareInput) -> dict:
    # Prepare the prompt
    prompt = f"""
    You are a financial and operations analyst for daycare centers. Analyze the following daycare center data and provide insights in the specified JSON format:

    Daycare Name: {data.businessName}

    REVENUE SOURCES:
    {json.dumps([src.dict() for src in data.revenueSources], indent=2)}

    EXPENSES:
    - Employees: {json.dumps([emp.dict() for emp in data.employees], indent=4)}
    - Facilities: {json.dumps([fac.dict() for fac in data.facilities], indent=4)}
    - Administrative: {json.dumps([adm.dict() for adm in data.administrative], indent=4)}
    - Supplies: {json.dumps([sup.dict() for sup in data.supplies], indent=4)}

    CLASSROOM DETAILS:
    {json.dumps([cls.dict() for cls in data.classrooms], indent=2)}

    OPERATING DETAILS:
    {json.dumps({"operatingHours": data.operatingHours, "operatingDays": data.operatingDays}, indent=2)}

    BUSINESS GOALS:
    {json.dumps([goal.dict() for goal in data.goals], indent=2)}

    Provide your analysis in the following JSON format:
    (Return the following format as valid JSON **only**, without any extra text or explanation)

    {{
      "net_monthly_income": {{
        "value": number,
        "currency": "USD",
        "calculation": "string explaining the calculation",
        "note": "brief interpretation"
      }},
      "break_even_enrollment": {{
        "value": number,
        "unit": "students",
        "calculation": "string explaining the calculation",
        "note": "brief interpretation"
      }},
      "largest_expense": {{
        "category": "string",
        "percentage_of_total_expenses": number,
        "calculation": "string explaining the calculation"
      }},
      "capacity_utilization": {{
        "value": number,
        "unit": "percent",
        "calculation": "string explaining the calculation",
        "note": "brief interpretation"
      }},
      "executive_summary": {{
        "financial_overview": "string",
        "profitability_status": "string",
        "enrollment_status": "string",
        "recommendations": ["string", "string", "string", "string"]
      }}
    }}

    Key calculations to include:
    1. Net Monthly Income = Total Revenue - Total Expenses
    2. Break-Even Enrollment = Total Fixed Costs / Average Revenue per Student
    3. Largest Expense Category = Expense category with highest percentage of total expenses
    4. Capacity Utilization = (Total Enrolled Students / Total Capacity) * 100

    Make all calculations based on monthly figures. Provide realistic, actionable insights.
    """
    
    try:
        client = openai.AsyncOpenAI(api_key=logger_settings.OPENAI_API_KEY)
        model = "gpt-4-turbo"  # or "gpt-4-turbo" if available
        messages=[
                {"role": "system", "content": "You are a financial analyst specializing in daycare center operations."},
                {"role": "user", "content": prompt}
            ]
        print(f"Generating insights for {data.businessName}...")
    
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1500,
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        # Extract the actual content from the response
        insights_content = response.choices[0].message.content
        
        # Parse the JSON content
        insights_data = json.loads(insights_content)
        print(f"Insights content: \n\n{insights_data}")
        return insights_data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Problematic content: {insights_content}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse OpenAI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"OpenAI API error: {str(e)}"
        )
    
async def verify_token(authorization: str = Header(...)):
    """Dependency to verify and extract token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, logger_settings.JWT_SECRET_KEY, algorithms=[logger_settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
        
        
# Endpoint to generate insights
@insight_router.post("/generate-insights")
async def get_insights(input_data: DaycareInput,
            request: Request,
            token_payload: dict = Depends(verify_token),
            db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    
    try:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Check if the user exists based on email
            await cursor.execute(
                "SELECT * FROM auth_users WHERE id = %s",
                (token_payload.get("sub"),)
            )
        user = await cursor.fetchone()  # Fetch the first matching user
        logger.info(f"User: {user['email']}")
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: user ID not found"
            )
        # Example usage
        data = {
            "net_monthly_income": {
                "value": 3000,
                "currency": "USD",
                "calculation": "Total Revenue (45.0) - Total Expenses (3785.0)",
                "note": "The daycare center is currently operating at a loss, indicating a need to either increase revenue or reduce expenses."
            },
            "break_even_enrollment": {
                "value": 1,
                "unit": "students",
                "calculation": "Total Fixed Costs (3785.0) / Average Revenue per Student (45.0)",
                "note": "To cover its expenses, the daycare would need to enroll approximately 84 students, which exceeds its current capacity."
            },
            "largest_expense": {
                "category": "Supplies",
                "percentage_of_total_expenses": 30.7,
                "calculation": "(Food Expense 3434.0 / Total Expenses 3785.0) * 100"
            },
            "capacity_utilization": {
                "value": 40,
                "unit": "percent",
                "calculation": "(Total Enrolled Students 34 / Total Capacity 34) * 100",
                "note": "The daycare is fully utilizing its capacity, which is a positive indicator for enrollment management."
            },
            "executive_summary": {
                "financial_overview": "The daycare center is currently facing financial challenges with a significant monthly loss.",
                "profitability_status": "Not profitable, operating at a loss.",
                "enrollment_status": "Fully enrolled at current capacity.",
                "recommendations": [
                    "Consider increasing revenue through additional services or programs.",
                    "Review and reduce supply costs to improve overall profitability.",
                    "Review and reduce supply costs to improve overall profitability.",
                    "Review and reduce supply costs to improve overall profitability.",
                    "Consider increasing revenue through additional services or programs."
                ]
            }
        }
        insight = await generate_daycare_insights(input_data)
        conn = await AuthDatabaseService.connection()
        try:
            async with conn.cursor() as cursor:
                # Convert Pydantic model to dict, then to JSON string
                data_json = json.dumps(insight)
                
                await cursor.execute(
                    "INSERT INTO insights_data (user_email, data) VALUES (%s, %s)",
                    (user["email"], data_json)
                )
                await conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving insight: {e}")
        finally:
            conn.close()
        # In a real implementation, you would save to a database
        logger.info("Insights saved successfully")
        return insight
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to save inputs (optional)
@insight_router.post("/save-inputs")
async def save_inputs(input_data: DaycareInput,
                      request: Request,
                      token_payload: dict = Depends(verify_token),
                      db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)
                    ):
    """
    Save the entire DaycareInput payload as JSON into the input_data table
    """
    # Token payload contains decoded JWT claims
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # Check if the user exists based on email
        await cursor.execute(
            "SELECT * FROM auth_users WHERE id = %s",
            (token_payload.get("sub"),)
        )
    user = await cursor.fetchone()  # Fetch the first matching user
    logger.info(f"User: {user['email']}")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: user ID not found"
        )
    conn = await AuthDatabaseService.connection()
    try:
        async with conn.cursor() as cursor:
            # Convert Pydantic model to dict, then to JSON string
            data_json = json.dumps(input_data.dict())
            
            # Insert user email and input JSON into the table
            await cursor.execute(
                "INSERT INTO input_data (user_email, data) VALUES (%s, %s)",
                (user["email"], data_json)
            )
            await conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving input: {e}")
    finally:
        conn.close()
    # In a real implementation, you would save to a database
    return {"status": "success", "message": "Inputs saved successfully"}


# Endpoint for file upload (optional)
# @insight_router.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     # In a real implementation, you would save the file
#     return {"status": "success", "filename": file.filename}

@insight_router.get("/fetch-inputs")
async def fetch_inputs(token_payload: dict = Depends(verify_token),
                       db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    pass

@insight_router.get("/recommendations")
async def recommendation(token_payload: dict = Depends(verify_token),
                       db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    # Token payload contains decoded JWT claims
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # Check if the user exists based on email
        await cursor.execute(
            "SELECT * FROM auth_users WHERE id = %s",
            (token_payload.get("sub"),)
        )
    user = await cursor.fetchone()  # Fetch the first matching user
    logger.info(f"User: {user['email']}")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: user ID not found"
        )
    
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # Fetch the latest input_data row for the user
        await cursor.execute(
            """
            SELECT id, user_email, data, created_at 
            FROM insights_data 
            WHERE user_email = %s 
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user['email'],)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No insights found for this user.")
        try:
            insights = json.loads(row['data'])
            recommendations = insights.get('executive_summary', {}).get('recommendations', [])
        except Exception:
            recommendations = []

        return {"recommendations": recommendations}
        