DATA_PATH = "Data"
DB_PATH = "vectorstores/db/"
EMBED_MODEL_NAME = "WhereIsAI/UAE-Large-V1"
# Configuration settings for the application

# Email Reader Configuration
IMAP_ENDPOINT = "imap-mail.outlook.com"

# Zero-shot classification model
ZERO_SHOT_MODEL = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
TEXT_LABELS = ['Positive', 'Negative', 'Neutral']


# Ollama Configuration
OLLAMA_MODEL = "mistral"

template = """You are acting as an Email Replier with a human touch, responding to customer emails in accordance with their expressed sentiments. Craft your replies considering the emotional tone conveyed by the customer in their emails. Your goal is to provide empathetic and context-appropriate responses that resonate with the customer's feelings.:
        {context}

        Question: {question}
        """

