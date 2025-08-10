# Code Documentation: Chatbot for Database Interaction

This documentation template outlines the structure and functionality of a chatbot designed to interact with databases, allowing users to converse with their data. The system comprises a backend (Python-based) and a mobile app (Dart/Flutter). Below is a detailed breakdown of components, their roles, and examples.

---

## Backend Structure (`backend/`)

### 1. **`app/api/`** - API Endpoints  
Handles HTTP routes for chatbot interactions, authentication, and credential management.  
- **Example Endpoints**:  
  - `POST /chat`: Send a user message and return a chatbot response.  
    ```python
    @router.post("/chat")
    async def chat(message: UserMessage, db: Session = Depends(get_db)):
        response = LangchainService.generate_response(message.text, db)
        return {"response": response}
    ```
  - `POST /auth/login`: Authenticate users via OAuth2 or API keys.  
  - `GET /env-config`: Retrieve environment-specific credentials (e.g., database URLs).  

---

### 2. **`app/core/`** - Configuration Management  
Manages SaaS/on-prem configurations and credential collection logic.  
- **SaaS**: Uses cloud-based secret managers (e.g., AWS Secrets Manager).  
- **On-Prem**: Reads credentials from `.env` files or user input.  
- **Example**:  
  ```python
  class ConfigLoader:
      def load(self):
          if os.getenv("DEPLOY_ENV") == "saas":
              return AwsSecretsManager().fetch()
          else:
              return dotenv_values(".env")
  ```

---

### 3. **`app/model/`** - Data Models  
Defines request/response schemas for API parameters.  
- **Example Model**:  
  ```python
  class UserCredentials(BaseModel):
      username: str
      password: SecretStr
      db_type: Literal["postgres", "mysql"]
  ```

---

### 4. **`app/prompts/`** - Natural Language Instructions  
Contains templates for guiding the chatbot's behavior.  
- **Example Prompt** (`sql_query_generator.txt`):  
  ```text
  You are a data analyst assistant. Generate a SQL query to answer the user's question: "{question}". 
  Tables available: {tables}.
  ```

---

### 5. **`app/schemas/`** - Data Validation  
Uses Pydantic to validate data flow (e.g., authentication, database connections).  
- **Example Schema**:  
  ```python
  class ChatMessage(BaseModel):
      text: str
      session_id: UUID
      timestamp: datetime
  ```

---

### 6. **`app/services/`** - Core Business Logic  
- **Key Services**:  
  - **LangchainService**: Manages conversation chains with OpenAI/GPT-4.  
  - **DatabaseService**: Connects to user databases (PostgreSQL, MySQL) using SQLAlchemy.  
  - **WeaviateService**: Vector search for contextual responses.  
  - **AuthService**: Handles JWT token generation and OAuth2 flows.  

- **Example**: Generating a SQL response:  
  ```python
  class DatabaseService:
      def execute_query(self, query: str):
          engine = create_engine(self.connection_url)
          return pd.read_sql(query, engine)
  ```

---

### 7. **`app/sql/`** - Optimized SQL Queries  
Pre-written queries for common tasks.  
- **Example Query** (`user_activity.sql`):  
  ```sql
  SELECT user_id, COUNT(*) AS total_actions 
  FROM activity_log 
  WHERE timestamp > NOW() - INTERVAL '7 days' 
  GROUP BY user_id;
  ```

---

### 8. **`app/scripts/`** - Helper Scripts  
Includes translation, classification, and tracing utilities.  
- **Example**: A script to anonymize sensitive data in logs.  

---

## Mobile App Structure (`mobile/`)

### 1. **`lib/screens/`** - UI Pages  
- **AuthenticationScreen**: Login/Signup with OAuth or email.  
- **ChatScreen**: Displays messages and sends user input to the backend.  
- **MenuDrawer**: Navigation for settings/theme changes.  

---

### 2. **`lib/services/`** - App Logic  
- **SpeechService**: Converts speech to text using device APIs.  
  ```dart
  class SpeechService {
      Future<String> listen() async {
          return await SpeechToText().recognize();
      }
  }
  ```
- **CacheService**: Stores chat history locally with Hive.  

---

### 3. **`lib/providers/`** - State Management  
- **ThemeProvider**: Toggles dark/light mode.  
  ```dart
  class ThemeProvider with ChangeNotifier {
      bool _isDark = false;
      bool get isDark => _isDark;
      
      void toggleTheme() {
          _isDark = !_isDark;
          notifyListeners();
      }
  }
  ```

---

## Deployment & Infrastructure

### 1. **Docker & CI/CD**  
- **`Dockerfile`**: Containerizes the backend with Gunicorn and Nginx.  
- **`.bitbucket/workflows/`**: Runs tests on pull requests.  

---

### 2. **Testing (`tests/`)**  
- **Example Test**: Verify database connection:  
  ```python
  def test_db_connection():
      db = DatabaseService(conn_url="postgresql://test:test@localhost/test")
      assert db.execute_query("SELECT 1") == 1
  ```

---

## Example Use Case  
1. **User Input**: "Show sales trends for Q2 2023."  
2. **Chatbot Action**:  
   - LangchainService generates a SQL query using `app/prompts/sql_query_generator.txt`.  
   - DatabaseService executes the query and returns a DataFrame.  
   - The result is formatted into a natural language response.  
3. **Mobile App**: Displays the response as a chart or text.  

---

This documentation provides a high-level overview. For detailed function-level explanations, refer to the Sphinx docs in `docs/` in `https://bitbucket.org/arcturusinternal/applicare_ai/src/main/backend/`

---
To run the Sphinx documentation, follow the installation guide in the applicare_ai Bitbucket main branch README. Once installed, the Sphinx docs will be hosted and accessible for further reference.

---
You can also find this docs markdown file on 
`https://bitbucket.org/arcturusinternal/applicare_ai/src/main/backend/docs/docs-template.md`