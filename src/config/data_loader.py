import os
import copy
from dotenv import load_dotenv
from models.resume_data_template import RESUME_DATA_TEMPLATE
from services.logging_config import logger

# Load environment variables from .env file
load_dotenv()

def _load_and_populate_data(template):
    """
    Recursively traverses the template, replacing 'ENV::VAR_NAME' placeholders
    with actual environment variable values.
    """
    if isinstance(template, dict):
        populated_dict = {}
        for key, value in template.items():
            populated_dict[key] = _load_and_populate_data(value)
        return populated_dict
    elif isinstance(template, list):
        return [_load_and_populate_data(item) for item in template]
    elif isinstance(template, str) and template.startswith("ENV::"):
        var_name = template.split("::")[1]
        value = os.getenv(var_name)
        if value is None:
            logger.warning(f"Environment variable '{var_name}' not set. Using placeholder.")
            return f"<{var_name} not set>"
        return value
    else:
        return template

def get_resume_data():
    """
    Loads the resume data template and populates it with environment variables.
    Returns a deep copy of the populated data to prevent in-memory modification of the template.
    """
    # Use a deep copy to ensure the original template is not modified
    template_copy = copy.deepcopy(RESUME_DATA_TEMPLATE)
    return _load_and_populate_data(template_copy)

# Load the data once when the module is imported.
# This acts as a cached, singleton instance of the populated resume data.
RESUME_DATA = get_resume_data()

if __name__ == '__main__':
    # For debugging purposes, print the populated data structure
    import json
    print("--- Populated Resume Data ---")
    print(json.dumps(RESUME_DATA, indent=2))
    print("\n--- End of Data ---") 