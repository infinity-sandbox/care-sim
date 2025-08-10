import random
from locust import HttpUser, task, between, constant
import string

# to run locust use the following command: 
# locust -f load_test_runner.py --host=http://localhost:8000
class LoadTestUser(HttpUser):
    # wait_time = between(1, 2)  # You can adjust wait time if needed between requests
    wait_time = constant(0)

    # Define the 3 user credentials
    credentials = [
        {"username": "abelmgetnet@gmail.com", "password": "ABELabel20192020"},
        {"username": "abel@arcturustech.com", "password": "admin1"}
    ]
    
    email = [
        {"email": "abelmgetnet@gmail.com"},
        {"email": "abel@arcturustech.com"}
    ]
    
    chat_payload = [
        {
        "query": "what is abel's email",
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session4",
        },
        {
        "query": "what is abel's email",
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session5",
        },
        {
        "query": "what is abel's email",
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session6",
        }
    ]
    
    regen_payload = [
        {
        "query": "what is your name?",
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session1",
        "messageId": "f91c56988ab5721472b1f9c4abf924b525564335a4cd2294c330b57ee690db92"
        },
        {
        "query": "who developed you?",
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session2",
        "messageId": "f91c56988ab5721472b1f9c4abf924b525564335a4cd2294c330b57ee690db92"
        },
    ]
    
    reaction_payload = [
        {
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session1",
        "messageId": "f91c56988ab5721472b1f9c4abf924b525564335a4cd2294c330b57ee690db92",
        "rating": "like",
        "feedbackText": ""
        },
        {
        "userId": "abelmgetnet@gmail.com",
        "sessionId": "session2",
        "messageId": "f91c56988ab5721472b1f9c4abf924b525564335a4cd2294c330b57ee690db92",
        "rating": "dislike",
        "feedbackText": "correct your answer please"
        }
    ]
    
    # @task(0)
    # def test_login_endpoint(self):
    #     # Pick a random user credential from the list
    #     user = random.choice(self.credentials)

    #     # Send a POST request to the /login endpoint with the user's credentials
    #     response = self.client.post("/api/v1/auth/login", data=user)

    #     # Log the response for debugging (optional)
    #     if response.status_code == 200:
    #         print(f"Success: {response.json()}")
    #     else:
    #         print(f"Error: {response.status_code}, Response: {response.text}")

    #     # Ensure this user stops after sending the request
    #     self.stop()

    # @task(0)
    # def test_register_endpoint(self):
    #     # Helper function to generate random strings for testing
    #     def random_string(length=10):
    #         return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    #     def random_email():
    #         return f"user{random.randint(1000, 9999)}@example.com"

    #     def random_phone_number():
    #         return f"+1234567890{random.randint(0, 9)}"

    #     def random_address():
    #         return f"{random.randint(1, 9999)} {random_string(5)} St, City, Country"

    #     def random_security_question():
    #         return "What is your favorite color?"

    #     def random_security_answer():
    #         return "Blue"

    #     # Generate random data for the registration
    #     data = {
    #         "username": random_string(8),
    #         "email": random_email(),
    #         "password": random_string(12),
    #         "phone_number": random_phone_number(),
    #         "address": random_address(),
    #         "security_question": random_security_question(),
    #         "security_answer": random_security_answer()
    #     }

    #     # Send a POST request to the /auth/register endpoint
    #     response = self.client.post("/api/v1/auth/register", json=data)

    #     # Log the response for debugging
    #     if response.status_code == 200:
    #         print(f"Registration Success: {response.json()}")
    #     else:
    #         print(f"Registration Error: {response.status_code}, Response: {response.text}")
    #     self.stop()
        
    @task(0)
    def get_user_env(self):
        # Randomly choose a test email (you can replace this with actual emails)
        # Define the credentials list with only emails
        user = random.choice(self.credentials)
        email = user["username"]
        
        # Send a GET request to the endpoint
        response = self.client.get(f"/api/v1/env/get-user?email={email}")
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            print(f"Fetched user environment for {email}: {response.json()}")
        else:
            print(f"Failed to fetch user environment for {email}, Status Code: {response.status_code}")
        self.stop()
        
    @task(0)
    def update_or_create_user_env(self):
        # Create a payload for the user
    
        user = random.choice(self.email)
        email = user["email"]
        payload = {
            "email": email,
            "DB_MS": "SQL",
            "DB_USER": "testuser",
            "DB_PASSWORD": "password123",
            "DB_HOST": "localhost",
            "DB_PORT": 3306,
            "DB": "test_db",
            "DB_TABLES": ["lsdk","alksdjf","testlfs"]
        }

        # Send the PUT request to update or create a user environment
        response = self.client.put(
            "/api/v1/env/user",  # Endpoint for updating or creating user environment
            json=payload,
        )
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            print(f"Successfully wrote user environment for {email}: {response.json()}")
        else:
            print(f"Failed to write user environment for {email}, Status Code: {response.status_code}")
        self.stop()
        
    @task(0)
    def update_or_create_admin_env(self):
        # Create a payload for the user
        payload = {
                "email": "abel@arcturustech.com",
                "email_user": "abelmgetnet@gmail.com",
                "DB_MS": "string",
                "DB_USER": "string",
                "DB_PASSWORD": "string",
                "DB_HOST": "string",
                "DB_PORT": 0,
                "DB": "string",
                "DB_TABLES": [
                    "ola comostas",
                    "it works"
                ],
                "DB_DRIVER": "string",
                "MODEL": "string",
                "OPENAI_API_KEY": "string",
                "WEAVIATE_URL": "string",
                "WEAVIATE_API_KEY": "string",
                "REDIS_HOST": "string",
                "REDIS_PORT": 0,
                "MY_EMAIL": "user@example.com",
                "MY_EMAIL_PASSWORD": "string",
                "EMAIL_APP_PASSWORD": "string",
                "FRONTEND_API_URL": "string",
                "BACKEND_API_URL": "string",
                "REQUESTS_PER_WINDOW": 0,
                "TIME_WINDOW": 0,
                "ALLOWED_HTTP_REQUEST_METHODS": [
                    "string"
                ],
                "RESTRICTED_HTTP_REQUEST_METHODS": [
                    "string"
                ],
                "CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS": [
                    "string"
                ],
                "BACKEND_CORS_ORIGINS": [
                    "string"
                ],
                "ACCESS_TOKEN_EXPIRE_MINUTES": 0,
                "REFRESH_TOKEN_EXPIRE_MINUTES": 0,
                "ALGORITHM": "string",
                "JWT_SECRET_KEY": "string",
                "JWT_REFRESH_SECRET_KEY": "string"
                }

        # Send the PUT request to update or create a user environment
        response = self.client.put(
            "/api/v1/env/admin",  # Endpoint for updating or creating user environment
            json=payload,
        )
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            print(f"Successfully wrote admin environment for user: {response.json()}")
        else:
            print(f"Failed to write admin environment for user, Status Code: {response.status_code}")
        self.stop()

    # TODO: I am thinking of removing weaviate and just use auth mysql to store memory chat
    # if that is fixed i think the only left thing would be async opeai connection and async db connections
    @task(1)
    def send_chat_message(self):
        # Generate sample data
        chat_payload = random.choice(self.chat_payload)
        
        # Make POST request to the chatbot endpoint (adjust URL accordingly)
        response = self.client.post("/api/v1/chatbot/query", json=chat_payload)

        # Log the response for debugging purposes
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Request failed with status code: {response.status_code}")
        self.stop()
        
    @task(0)
    def send_reactions(self):
        reaction_payload = random.choice(self.reaction_payload)
        
        # Make POST request to the chatbot endpoint (adjust URL accordingly)
        response = self.client.post("/api/v1/chatbot/reaction", json=reaction_payload)

        # Log the response for debugging purposes
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Request failed with status code: {response.status_code}")
        self.stop()
        
    @task(0)
    def send_regen(self):
        regen_payload = random.choice(self.regen_payload)
        
        # Make POST request to the chatbot endpoint (adjust URL accordingly)
        response = self.client.post("/api/v1/chatbot/regenerate", json=regen_payload)

        # Log the response for debugging purposes
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Request failed with status code: {response.status_code}")
        self.stop()
        