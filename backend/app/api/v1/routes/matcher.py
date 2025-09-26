from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from llama_index.core.schema import Document
from typing import List, Optional, Union
import shutil
import os
import uuid
import json
from datetime import datetime
from app.services.evaluation_candidate_service import openai_service
from app.llms.azure_openai_client import azure_client
from app.core.config import settings
from app.core.security import get_current_user
from app.db.neo4j import (
    Neo4jDB,
    get_db
)
from app.db.qdrant import vector_search
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Matcher"])

class MatchRequest(BaseModel):
    question: Union[str, dict]
    number_candidate: int = 5
    job_description: Optional[str] = ""


@router.post("/find_matching_candidates_score/")
async def retrieve_score(
    req: MatchRequest,
    db: Neo4jDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    if isinstance(req.question, dict):
        query_text = json.dumps(req.question, ensure_ascii=False)
    else:
        query_text = req.question
    results = vector_search.retrieve_from_qdrant_neo4j(query_text=query_text,
                                                       number_candidate=req.number_candidate)
    print(f"Retrieved results: {results}")
    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    enriched_results = []
    for candidate_info, similarity_score in results:
        talent_id = candidate_info["talent_id"]

        resume_text = vector_search.get_resume_text_by_talent_id(talent_id)
        if not resume_text:
            enriched_results.append({
                **candidate_info,
                "similarityScore": similarity_score,
                "qualificationScore": None,
                "scoringDetails": {}
            })
            continue

        try:
            scoring_result = await openai_service.score_candidate_qualifications(
                candidate_resume=resume_text,
                job_description=req.job_description
            )
        except Exception as e:
            scoring_result = {"error": str(e)}

        enriched_results.append({
            **candidate_info,
            "similarityScore": similarity_score,
            "qualificationScore": scoring_result.get("totalScore") if isinstance(scoring_result, dict) else None,
            "scoringDetails": scoring_result
        })
    db.upload_matching_results({"results": enriched_results})
    print(f"Enriched results: {enriched_results}")
    return {"results": enriched_results}

@router.get("/matching-results/")
async def get_matching_results(
    jd_id: Optional[str] = None,
    db: Neo4jDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    results = db.get_matching_results(jd_id=jd_id)
    return {"results": results}
