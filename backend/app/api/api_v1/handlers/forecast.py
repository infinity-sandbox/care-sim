import asyncio
import json
from fastapi import APIRouter, HTTPException, Header, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from app.services.multivariate_timeseries import MultivariateTimeSeries
from fastapi.responses import JSONResponse
from app.core.config import logger_settings, Settings
from app.services.user_service import UserService
from app.schemas.forcaster_schema import PredictionRequest, ForecastResponse, DropdownItem
from typing import List

api = APIRouter()
logger = logger_settings.get_logger(__name__)

@api.post("/forecaster")
async def forecast(request: PredictionRequest):
    predictions, causes, train, test = await MultivariateTimeSeries.forecast(request.column, request.days)
    return ForecastResponse(predictions=predictions, causes=causes, train=train, test=test)

@api.get("/dropdown_data", response_model=List[DropdownItem])
async def get_dropdown_data():
    dropdowns, columns = await MultivariateTimeSeries.get_dropdowns()
    return dropdowns

@api.websocket("/forecast/loop")
async def forecaster_loop(websocket: WebSocket, background_tasks: BackgroundTasks):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            authorization = message.get("authorization")
            refresh_token = message.get("refresh_token")

            if not authorization or not refresh_token:
                raise WebSocketDisconnect(code=403)

            user = await UserService.decode_token(authorization, refresh_token)
            
            # Start the forecasting in a background task
            background_tasks.add_task(run_forecasting_task, user.email)

            # Acknowledge that the task is running
            await websocket.send_text("Forecasting process has started in the background")
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

async def run_forecasting_task(user_email: str):
    try:
        dropdowns, columns = await MultivariateTimeSeries.get_dropdowns()
        
        while True:
            problem_found = False
            try:
                problem = await MultivariateTimeSeries.forecast_loop()
                logger.warning(f"Problem: {problem}")
                pr = MultivariateTimeSeries.has_empty_lists_or_none_values(problem)
                logger.warning(f"Problematic bool: {pr}")

                if not pr:
                    problem_found = True
                    problematic_columns_with_timestamps = {
                        col: timestamps for col, timestamps in problem.items() if timestamps
                    }
                    logger.warning(f"Problematic columns with timestamps: {problematic_columns_with_timestamps}")

                    for problematic, timestamps in problematic_columns_with_timestamps.items():
                        await UserService._send_email_request(user_email, problematic, timestamps)
                        logger.info(f"Found an issue: {problematic}. Sending an email to {user_email}...")
                else:
                    problem_found = False
                    logger.warning("No issues were found for the upcoming day.")
                
                await asyncio.sleep(180)  # Adjust the sleep duration as necessary

            except Exception as e:
                problem_found = False
                logger.error(f"{e}")

    except Exception as e:
        logger.error(f"Error in forecasting task: {e}")