from typing import Optional
from openai import OpenAI
import openai
from openai import OpenAI
from pydub import AudioSegment
import subprocess
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
import os, sys
from math import exp
import numpy as np
from app.prompts.main import Prompt
import json
from app.sql.main import SqlQuery
from difflib import get_close_matches

class OpenAIService:
    # @staticmethod
    # async def speech_to_text(audio_data, settings: Optional[Settings] = None):
    #     client = OpenAI(api_key=logger_settings.OPENAI_API_KEY)
    #     with open(audio_data, "rb") as audio_file:
    #         transcript = client.audio.transcriptions.create(
    #             model="whisper-1",
    #             response_format="text",
    #             file=audio_file
    #         )
    #     return transcript

    # @staticmethod
    # async def text_to_speech(input_text: str, webm_file_path: str, wav_file_path: str, settings: Optional[Settings] = None):
    #     client = OpenAI(api_key=logger_settings.OPENAI_API_KEY)
    #     response = client.audio.speech.create(
    #         model="tts-1",
    #         voice="nova",
    #         input=input_text
    #     )
    #     with open(webm_file_path, "wb") as f:
    #         response.stream_to_file(webm_file_path)
    #     # convert webm to wav
    #     try:
    #         # Load the WebM file
    #         audio = AudioSegment.from_file(webm_file_path, format="webm")
    #         # Export as WAV file
    #         audio.export(wav_file_path, format="wav")
    #     except Exception as e:
    #         logger.error(f"Failed to convert {webm_file_path} to WAV: {e}")
    #         # Optionally, run ffmpeg manually to debug
    #         command = [
    #             'ffmpeg',
    #             '-i', webm_file_path,
    #             wav_file_path
    #         ]
    #         try:
    #             subprocess.run(command, check=True, capture_output=True, text=True)
    #             logger.info(f"ffmpeg command executed successfully")
    #         except subprocess.CalledProcessError as e:
    #             logger.error(f"ffmpeg command failed: {e.stderr}")
    #     return wav_file_path
    
    @staticmethod
    async def get_completion(
        messages: list[dict[str, str]],
        model: str = logger_settings.MODEL,
        max_tokens=500,
        temperature=0,
        stop=None,
        seed=123,
        tools=None,
        logprobs=None,
        top_logprobs=None,
        settings: Optional[Settings] = None
    ) -> str:
        '''
        params: 

        messages: list of dictionaries with keys 'role' and 'content'.
        model: the model to use for completion. Defaults to 'davinci'.
        max_tokens: max tokens to use for each prompt completion.
        temperature: the higher the temperature, the crazier the text
        stop: token at which text generation is stopped
        seed: random seed for text generation
        tools: list of tools to use for post-processing the output.
        logprobs: whether to return log probabilities of the output tokens or not. 
        '''
        # Ensure async client is used
        client = openai.AsyncOpenAI(api_key=logger_settings.OPENAI_API_KEY)  # Replace with your API key
        model = logger_settings.MODEL
        params = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": stop,
            "seed": seed,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
        }
        if tools:
            params["tools"] = tools

        completion = await client.chat.completions.create(**params)
        logger.info(f"Completion Generated!")
        return completion
    
    # @staticmethod
    # async def respond(query: str, payload: str, flag: str, settings: Optional[Settings] = None) -> str:
    #     try:
    #         if flag == 'problem':
    #             PROMPT_PATH=os.path.join(logger_settings.PROMPT_DIR, "admin_response/problem_template.txt")
    #         elif flag == 'cause':
    #             PROMPT_PATH=os.path.join(logger_settings.PROMPT_DIR, "admin_response/cause_template.txt")
    #         elif flag == 'fix':
    #             PROMPT_PATH=os.path.join(logger_settings.PROMPT_DIR, "admin_response/fix_template.txt")
    #         else:
    #             PROMPT_PATH=os.path.join(logger_settings.PROMPT_DIR, "admin_response.txt")
    #         with open(PROMPT_PATH, "r") as file:
    #             PROMPT = file.read()
    #     except FileNotFoundError as e:
    #         logger.error(f"File not found: {e}")
    #         raise FileNotFoundError(f"File not found: {e}")
    #     API_RESPONSE = await OpenAIService.get_completion(
    #         [{"role": "system", "content": PROMPT.format(question=query, payload=payload)}],
    #         model=logger_settings.MODEL,
    #         settings=settings
    #     )
    #     system_msg = str(API_RESPONSE.choices[0].message.content)
    #     return system_msg
    
    
    # @staticmethod
    # async def classify(user_message: str, settings: Optional[Settings] = None) -> str:
    #     try:
    #         PROMPT_PATH=os.path.join(logger_settings.PROMPT_DIR, "classification_template.txt")
    #         with open(PROMPT_PATH, "r") as file:
    #             PROMPT = file.read()
    #     except FileNotFoundError as e:
    #         logger.error(f"File not found: {e}")
    #         raise FileNotFoundError(f"File not found: {e}")
    #     API_RESPONSE = await OpenAIService.get_completion(
    #         [{"role": "user", "content": PROMPT.format(user_message=user_message)}],
    #         model=logger_settings.MODEL,
    #         logprobs=True,
    #         top_logprobs=1,
    #         settings=settings
    #     )
    #     top_three_logprobs = API_RESPONSE.choices[0].logprobs.content[0].top_logprobs
    #     content = ""
    #     system_msg = str(API_RESPONSE.choices[0].message.content)

    #     for i, logprob in enumerate(top_three_logprobs, start=1):
    #         linear_probability = np.round(np.exp(logprob.logprob) * 100, 2)
    #         if logprob.token in ["problem", "cause", "fix"] and linear_probability >= 95.00:
    #             content += (
    #                 f"\n"
    #                 f"output token {i}: {system_msg},\n"
    #                 f"logprobs: {logprob.logprob}, \n"
    #                 f"linear probability: {linear_probability} \n"
    #             )
    #             logger.debug(f"{content} \nclassification: {logprob.token}")
    #             classification = str(system_msg)
    #         else:
    #             classification = ""
    #             logger.warning(f"classification: {classification}, logprobs confidence is less than 95%.")
    #     return classification
    
    @staticmethod
    async def classify_akhil(user_message: str, settings: Optional[Settings] = None) -> str:
        formated_prompt = await Prompt.read_prompt_full("akhil_systems/classfications1", user_message=user_message)
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "user", "content": formated_prompt}],
            model=logger_settings.MODEL,
            logprobs=True,
            top_logprobs=1,
            settings=settings
        )
        top_three_logprobs = API_RESPONSE.choices[0].logprobs.content[0].top_logprobs
        content = ""
        system_msg = str(API_RESPONSE.choices[0].message.content)

        for i, logprob in enumerate(top_three_logprobs, start=1):
            linear_probability = np.round(np.exp(logprob.logprob) * 100, 2)
            if logprob.token in ["true", "false"] and linear_probability >= 95.00:
                content += (
                    f"\n"
                    f"output token {i}: {system_msg},\n"
                    f"logprobs: {logprob.logprob}, \n"
                    f"linear probability: {linear_probability} \n"
                )
                logger.debug(f"{content} \nclassification: {logprob.token}")
                classification = str(system_msg)
                if classification == 'true' or logprob.token == 'true':
                    logger.debug(f"Classification: \n{classification}")
                    return 'true'
                
                elif classification == 'false' or logprob.token == 'false':
                    return 'false'
                else:
                    return ''
            else:
                classification = ''
                logger.warning(f"classification: {classification}, logprobs confidence is less than 95%.")
                return ''
        return classification
    
    @staticmethod
    def formated_name(param):
        return f"'{param}'"

    @staticmethod 
    async def classify_parameter(user_message: str, settings: Optional[Settings] = None) -> str:
        formated_prompt = await Prompt.read_prompt_full(
                                    "com/arcturustech/parameter_extraction", 
                                    user_message=user_message
                                    )
        # Send the prompt to the OpenAI API
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "system", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response_content = API_RESPONSE.choices[0].message.content.strip()
        try:
            extracted_params = json.loads(response_content)
            logger.debug(f"Extracted parameters: {extracted_params}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding response: {response_content}. Exception: {e}")
            extracted_params = {"interval": None, "start_time": None, "end_time": None}
        if not extracted_params.get("interval") or (extracted_params.get("interval") in [None, "None"]):
            interval = "5 MINUTE"
        else:
            interval = extracted_params.get("interval")
        sql_query = await SqlQuery.read_sql_full("com/arcturustech/demo_beta/txn_slow_cause", 
                                           interval=interval)

        logger.debug(f"SQL Query: \n\n{sql_query}\n\n")
        return sql_query

    @staticmethod 
    async def classify_akhil_lab(user_message: str, settings: Optional[Settings] = None) -> str:
        formated_prompt = await Prompt.read_prompt_full("akhil_systems/classifications", user_message=user_message)
        # Send the prompt to the OpenAI API
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "user", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response_content = API_RESPONSE.choices[0].message.content.strip()
        try:
            extracted_params = json.loads(response_content)
            logger.debug(f"Extracted parameters: {extracted_params}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding response: {response_content}. Exception: {e}")
            extracted_params = {"PD": None, "FIELDNAME": None, "REGISTRATIONNO": None}
        if not extracted_params.get("PD"):  # Check if PD is missing or empty
            P = 'op'  # Default to 'op'
        elif extracted_params["PD"].lower() == 'opd':
            P = 'op'
        elif extracted_params["PD"].lower() == 'ipd':
            P = 'ip'
        else:
            P = 'op'
        FIELD_NAME = OpenAIService.extract_field_parameters(extracted_params["FIELDNAME"])
        sql_query = await SqlQuery.read_sql_full("lab_results", 
                                           PD=OpenAIService.formated_name(extracted_params["PD"].upper()),
                                           P=P, 
                                           REGISTRATIONNO=extracted_params["REGISTRATIONNO"], 
                                           FIELDNAME=OpenAIService.formated_name(FIELD_NAME))
        logger.debug(f"SQL Query: \n\n{sql_query}\n\n")
        return sql_query
    
    @staticmethod
    def validate_fieldname(fieldname: str) -> str:
        """Matches the given fieldname to the closest match in FIELDNAME_LIST."""
        
        # Full FIELDNAME list
        FIELDNAME_LIST = [
            "Bleeding Time (BT)1", "24 Hour Urine Total Volume", "LDH (Fluid)", "Urine Chloride (Spot)", 
            "Urine Potassium (Spot)", "25 HYDROXY VITAMIN D-TOTAL", "Absolute Basophil Count", 
            "Absolute Eosinophil Count (AEC)", "Absolute Lymphocyte Count", "Absolute Monocyte Count", 
            "Absolute Neutrophil Count (ANC)", "Acetone Qualitative", 
            "Activtd.Partial Thromboplastin Time (APTT) Control", 
            "Actvtd.Partial Thromboplastin Time (APTT) Patient", "age", "Albumin", 
            "Alkaline Phosphatase", "ALPHA-FETOPROTEIN(AFP) TUMOR MARKER", "Ammonia (Plasma)*", 
            "Amylase", "Amylase (Fluid)", "ANTI CYCLIC CITRULLINATED PEPTIDE (ANTI CCP)", 
            "Anti Mullerian Hormone (AMH)", "ANTI THYROGLOBULIN (ANTI-TG)", 
            "ANTI THYROID PROXIDASE", "Anti Thyroid Proxidase*", "Antibody to Hepatitis C Virus", 
            "Antibody to HIV 1 & 2, p24 Antigen", "Ascitic/Peritoneal Albumin", 
            "Ascitic/Peritoneal Fluid for Glucose", "Atypical Cells", 
            "BETA HCG (CANCER MARKER)", "Bilirubin Conjugated (Bc)", "Bilirubin Total (TBil) Numeric", 
            "Bilirubin Unconjugated (Bu)", "Bleeding Time (BT)", "Blood Sugar (1 Hr.)", 
            "Blood Sugar (2 Hrs.)", "Blood Sugar (Fasting)", "BUN - Blood Urea Nitrogen", "CA 125", 
            "Calcium", "CEA", "Chloride", "Chloride (Serum/Plasma)", "Cholesterol-Total", 
            "CK / CPK (Creatine Kinase)", "CKMB", "CORTISOL (AM)", "CORTISOL (PM)", 
            "CORTISOL (RANDOM)", "Creatinine", "CREATININE KINASE MB MASS", 
            "CRP - C Reactive Protein", "CSF Differential Count- Lymphocytes", 
            "CSF Differential Count- Neutrophils", "CSF for Glucose", "CSF for Protein", 
            "D- Dimer", "DLC - Band Cells", "DLC - Basophils", "DLC - Blasts", "DLC - Eosinophils", 
            "DLC - Lymphocytes", "DLC - Metamyelocytes", "DLC - Monocytes", "DLC - Myelocytes", 
            "DLC - Neutrophils", "DLC - Promyelocytes", "dTIBC", "ESR (Erythrocyte Sed.Rate)", 
            "Estradiol (E2)", "FDP  (Fibrin Degradation Product)", "Ferritin", 
            "Ferritin - Covid", "Fluid for Glucose", "Fluid for Protein", "Fluid Volume", 
            "FSH- Follicle Stimulating Hormone*", "FT3 - Free T3", "FT4 - Free T4", 
            "G - 6 PD DEFICIENCY TEST *", "GGTP (GAMMA GT)", "Glucose (2 Hour Post Prandial)", 
            "Glucose (Fasting Blood Sugar / FBS)", "Glucose (RBS/Random Blood Sugar)", 
            "GLUCOSE CHALLENGE TEST (GCT)", "Haemoglobin Estimation (Hb)", 
            "HBA1C - Glycosylated Hemoglobin", "HCG - BETA SPECIFIC", "HDL CHOLESTEROL", 
            "HEM", "Hepatitis A Virus (Anti-HAV IgM)", "Hepatitis B surface Antigen", 
            "HEPATITIS B VIRUS SURFACE ANTIBODY{QUANT}", "Hepatitis E Virus {Anti-HEV IgM}", 
            "Iron", "LDH", "LH- Leutenizing Hormone", "Lipase", "Magnesium", "Mantoux Test", 
            "MCH", "MCHC", "MCV", "New123", "NT-proBNP*", "PCV (Haematocrit)", 
            "Peritoneal Fluid - Diff. Count, Lymphocytes", 
            "Peritoneal Fluid - Diff. Count, Neutrophills", "Phosphorus", 
            "Platelet Count", "Pleural Fluid - Diff. Count, Lymphocytes", 
            "Pleural Fluid - Diff. Count, Neutorphils", "Pleural Fluid for Glucose", 
            "Pleural Fluid for LDH", "Pleural Fluid for Protein", "Potassium", 
            "Procalcitonin(PCT),Quantitavie", "Prolactin", "Protein Total", 
            "Prothrombin Time (PT) Control", "Prothrombin Time (PT) INR Value", 
            "Prothrombin Time (PT) Ratio", "Prothrombin Time Patient Value", 
            "PSA Total (Prostate Specific Antigen)", "PTH - INTACT", "RBC Count (Red Blood Cell)", 
            "RDW", "Reticulocyte Count", "Semen Analysis - Morphology, Abnormal", 
            "Semen Analysis - Morphology, Normal", "Semen Analysis - Motility, Active", 
            "Semen Analysis - Motility, Active.", "Semen Analysis - Motility, Non-motile", 
            "Semen Analysis - Motility, Sluggish", "Semen Analysis - Motility, Sluggish.", 
            "Semen Analysis - Total Sperm Count", "Semen Analysis - Volume", 
            "Semen Analysis -Percentage Motility ( Grade A + B", 
            "Semen Analysis Post wash-Non-Motile", 
            "Semen Analysis post wash-Total Sperm Count", "serum creatnine", 
            "SERUM PROGESTERONE", "SGOT (AST)", "SGPT (ALT)", "Sodium", 
            "test Himanshu", "Test123", "Testosterone, Total", "TLC", 
            "Total IgE", "Total Leukocyte Count (TLC)", "Triglycerides", 
            "Troponin-I (Quantitative)", "TSH-Thyroid Stimulating Hormone", "UREA", 
            "Uric Acid", "Urine Analysis - pH", "Urine Analysis - Quantity", 
            "Urine Analysis - Specific Gravity", "Urine Creatinine", "Urine Creatinine.", 
            "Urine Microalbumin(n)", "Urine Protein", "Urine Sodium (Spot)", "Vitamin B12"
        ]

        if fieldname in FIELDNAME_LIST:
            return fieldname
        closest_match = get_close_matches(fieldname, FIELDNAME_LIST, n=1, cutoff=0.6)
        logger.debug(f"Closest match: \n\n{closest_match}")
        return closest_match[0] if closest_match else ""

    @staticmethod
    def extract_field_parameters(field_name: str) -> dict:
        """Extracts PD, FIELDNAME, and REGISTRATIONNO from the user message."""
        return OpenAIService.validate_fieldname(field_name)

    @staticmethod
    async def classify_applicare(user_message: str, settings: Optional[Settings] = None) -> str:
        logger.info(f'Classifying user message (slow/cause/false)')
        formated_prompt = await Prompt.read_prompt_full(
            "com/arcturustech/slow_cause_classification",
            user_message=user_message
        )
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "system", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response = API_RESPONSE.choices[0].message.content.strip().strip('"')
        system_msg = str(response)
        logger.info(f"\nApplicare Classification API Response: \n{system_msg}")

        if system_msg in ["true", "false"]:
            classification = str(system_msg)
            if classification == 'true':
                logger.debug(f"Classification: \n{classification}")
                return classification
            
            elif classification == 'false':
                logger.debug(f"Classification: \n{classification}")
                return classification
            else:
                logger.debug(f"Classification: \n{classification}")
                return 'false'
        else:
            classification = 'false'
            logger.warning(f"The classification is neither 'true' nor 'false'.")
            return 'false'

    @staticmethod
    async def classify_applicare_recommendation(user_message: str, settings: Optional[Settings] = None) -> str:
        logger.info(f'Classifying user message recommendation T/F')
        formated_prompt = await Prompt.read_prompt_full(
            "com/arcturustech/question_recommendation",
            user_message=user_message
        )
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "system", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response = API_RESPONSE.choices[0].message.content.strip().strip('"')
        system_msg = str(response)
        logger.info(f"\nApplicare Classification API Response: \n{system_msg}")

        if system_msg in ["true", "false"]:
            classification = str(system_msg)
            if classification == 'true':
                logger.debug(f"Classification: \n{classification}")
                return classification
            
            elif classification == 'false':
                logger.debug(f"Classification: \n{classification}")
                return classification
            else:
                logger.debug(f"Classification: \n{classification}")
                return 'false'
        else:
            classification = 'false'
            logger.warning(f"The classification is neither 'true' nor 'false'.")
            return 'false'
    
    @staticmethod
    async def language_detector(user_message: str, settings: Optional[Settings] = None) -> str:
        '''
            @params user_message: users question
                    settings: user specific config settings
            @return classification  true: if the user_message is not english
                                    false: if the user_message is english
        '''
        logger.info(f"Classifying user message (if it's english or not)")
        formated_prompt = await Prompt.read_prompt_full( 
            "translation/language_classification",
            user_message=user_message
        )
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "user", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response = API_RESPONSE.choices[0].message.content.strip().strip('"')
        system_msg = str(response)
        logger.info(f"\nLanguage Classification API Response: \n{system_msg}")

        if system_msg in ["true", "false"]:
            classification = str(system_msg)
            if classification == 'true':
                logger.debug(f"Classification: \n{classification}")
                return classification
            else:
                logger.debug(f"Classification: \n{classification}")
                return "false"
        else:
            classification = "false"
            logger.warning(f"classification: {classification}")
            return classification
    
    @staticmethod
    async def in_translation(user_message: str, settings: Optional[Settings] = None) -> str:
        logger.info(f'Translating user message to english...')
        formated_prompt = await Prompt.read_prompt_full(
            "translation/in_translation_engine",
            user_message=user_message
        )
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "system", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response = API_RESPONSE.choices[0].message.content.strip().strip('"')
        system_msg = str(response)
        logger.info(f"\nTranslation API Response: \n{system_msg}")
        return system_msg
    
    @staticmethod
    async def out_translation(user_message: str, english_text: str, settings: Optional[Settings] = None) -> str:
        logger.info(f'Translating openai output to original language...')
        formated_prompt = await Prompt.read_prompt_full(
            "translation/out_translation_engine",
            original_text=user_message,
            english_text=english_text
        )
        API_RESPONSE = await OpenAIService.get_completion(
            [{"role": "system", "content": formated_prompt}],
            model=logger_settings.MODEL,
            settings=settings
        )
        response = API_RESPONSE.choices[0].message.content.strip().strip('"')
        system_msg = str(response)
        logger.info(f"\nTranslation API Response: \n{system_msg}")
        return system_msg
