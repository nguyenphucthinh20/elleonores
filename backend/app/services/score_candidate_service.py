from app.llms.azure_openai_client import azure_client
from typing import Dict, Any
import logging
from app.llms.azure_openai_client import AzureOpenAIClient 

logger = logging.getLogger(__name__)

class EvaluationService:
    """Service class for handling OpenAI API interactions via AzureOpenAIClient."""
    
    def __init__(self):
        self.client = azure_client 
    
    async def score_candidate_qualifications(
        self,
        candidate_resume: str,
        job_description: str = ""
    ) -> Dict[str, Any]:
        """Score a candidate's resume against job qualifications using Azure OpenAI."""
        try:
            logger.info("Starting candidate qualification scoring with Azure OpenAI")
            
            prompt_parts = [
                "You are a professional recruiter tasked with evaluating how well a candidate's resume matches the qualifications for a job.",
                ""
            ]
            

            if job_description:
                prompt_parts.append(f"JOB DESCRIPTION: {job_description}")
            
            prompt_parts.extend([
                "",
                "CANDIDATE'S RESUME:",
                candidate_resume,
                "",
                "Please evaluate the candidate against each qualification using the following scale:",
                "0 - Not Met",
                "1 - Somewhat Met",
                "2 - Strongly Met",
                "",
                "Please evaluate ONLY the following qualifications, and return your response in JSON format with explanations for each score:",
                ""
            ])
            
            
            prompt_parts.extend([
                'Format your response as valid JSON with this structure:',
                '{',
                '  "requiredScores": [ { "qualification": "...", "score": 0/1/2, "explanation": "..." } ],',
                '  "preferredScores": [ { "qualification": "...", "score": 0/1/2, "explanation": "..." } ],',
                '  "overallFeedback": "..."',
                '}'
            ])
            
            prompt = "\n".join(prompt_parts)
            
            response_text = self.client.invoke_model(prompt, system_message="You are a professional recruiter.")
            if not response_text:
                raise ValueError("Azure OpenAI returned no response")
            
            logger.info("Parsing response JSON")
            
            scoring_data = AzureOpenAIClient.parse_json_string(response_text)
            
            required_scores = scoring_data.get("requiredScores", [])
            preferred_scores = scoring_data.get("preferredScores", [])
            
            required_total = sum(item.get("score", 0) for item in required_scores)
            preferred_total = sum(item.get("score", 0) for item in preferred_scores)
            
            total_score = required_total + preferred_total
            
            result = {
                "requiredScores": required_scores,
                "preferredScores": preferred_scores,
                "totalScore": total_score,
                "overallFeedback": scoring_data.get("overallFeedback", ""),
                "scoringBreakdown": {
                    "requiredTotal": required_total,
                    "preferredTotal": preferred_total,
                }
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error scoring candidate qualifications: {e}")
            raise

openai_service = EvaluationService()