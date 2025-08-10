from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid
import jwt
import smtplib
from pydantic import ValidationError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, Depends
from app.core.security import get_password, verify_password
import pymongo
import json
import random
from urllib.parse import urlencode
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from app.core.security import create_access_token

class UserService:
    @staticmethod
    async def send_email(email: str, reset_link):
        try:
            # Email details
            sender_email = logger_settings.MY_EMAIL
            receiver_email = email
            subject = "PASSWORD RESET LINK REQUEST: Applicare AI"
            body = f"Password Reset Link:\n{reset_link}"

            # Create the email message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            # Convert the message to a string
            email_string = message.as_string()

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(logger_settings.MY_EMAIL, logger_settings.EMAIL_APP_PASSWORD)
            server.sendmail(logger_settings.MY_EMAIL, email, email_string)
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
        finally:
            server.quit()

    # @staticmethod
    # async def _send_email_request(email: str, problem: str, timestamps: list):
    #     logger.debug(f"Sending email to {email} with problem: {problem}")
    #     user = await UserService.get_user_by_email(email)
    #     if not user:
    #         raise pymongo.errors.OperationFailure(
    #             "User not found or this email is not registered!")
    
    #     access_token = create_access_token(email)
    #     logger.debug(f'Access token from email:\n{access_token}')
    #     # Construct the URL with the problem as a query parameter
    #     query_params = {
    #         'token': access_token,
    #         'problem': problem
    #     }
    #     # Encode the query parameters
    #     encoded_params = urlencode(query_params)
    #     # Construct the final link
    #     link = f"{logger_settings.FRONTEND_API_URL}/dashboard?{encoded_params}"
    #     # Send the reset link to the user's email
    #     logger.debug(f"Dashboard Link: {link}")
    #     status = await UserService._send_email(email, problem, link, timestamps)
    #     if status:
    #         return logger.debug("Password reset email sent!")
    #     else:
    #         return logger.debug("Password reset email not sent!")

    @staticmethod
    async def _send_email(email: str, problem: str, link: str, timestamp: list):
        try:
            # Email details
            logger.info(f'Prepared to send email ...')
            sender_email = logger_settings.MY_EMAIL
            receiver_email = email
            subject = "Current Issue Detected in Your OS System"
            body = (
                "Dear Client,\n\n"
                "We have identified a potential issue that is currently affecting your OS system.\n\n"
                "Details of the identified problem:\n"
                f"{problem}\n\n"
                "Please monitor your dashboard for updates and take any necessary actions to address the issue.\n\n"
                "Thank you for your attention to this matter.\n\n"
                "Best regards,\n"
                "Applicare OS AI Team"
            )
            
            # Create the email message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            # Convert the message to a string
            email_string = message.as_string()

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(logger_settings.MY_EMAIL, logger_settings.EMAIL_APP_PASSWORD)
            server.sendmail(logger_settings.MY_EMAIL, email, email_string)
            logger.warning(f"Email sent to: {email}")
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
        finally:
            logger.debug(f"Closing the server connection.")
            server.quit()
            