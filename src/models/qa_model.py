from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
from .config.data_loader import RESUME_DATA
from .services.logging_config import logger

class QAModel:
    """
    A simple Question Answering model pipeline using a pre-trained transformer.
    """
    def __init__(self, model_name: str = "deepset/minilm-uncased-squad2"):
        """
        Initializes the QA model and tokenizer.
        """
        logger.info(f"Loading QA model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            self.qa_pipeline = pipeline(
                "question-answering", 
                model=self.model, 
                tokenizer=self.tokenizer
            )
            self.resume_context = self._build_resume_context()
            logger.info("QA model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load QA model: {e}")
            self.qa_pipeline = None
            self.resume_context = ""

    def _build_resume_context(self) -> str:
        """
        Builds a single string context from the structured resume data.
        """
        # This can be expanded to create a more narrative context
        return " ".join([
            f"{v}" for k, v in RESUME_DATA.items() 
            if isinstance(v, str)
        ])

    def answer_question(self, question: str) -> tuple[str, float]:
        """
        Answers a question based on the resume context.
        
        Returns:
            A tuple containing the answer string and the confidence score.
        """
        if not self.qa_pipeline or not self.resume_context:
            return "The QA model is not available.", 0.0

        try:
            result = self.qa_pipeline(question=question, context=self.resume_context)
            answer = result.get("answer", "I could not find a specific answer.")
            score = result.get("score", 0.0)
            logger.info(f"Question answered with score: {score:.4f}")
            return answer, score
        except Exception as e:
            logger.error(f"Error during question answering: {e}")
            return "I encountered an error while processing your question.", 0.0

# Example usage:
if __name__ == '__main__':
    qa_model = QAModel()
    if qa_model.qa_pipeline:
        test_question = "What is Frank's experience with Agile?"
        print(f"Testing with question: '{test_question}'")
        answer, score = qa_model.answer_question(test_question)
        print(f"Answer: '{answer}' (Confidence: {score:.4f})")
    else:
        print("Could not run QA model test.") 