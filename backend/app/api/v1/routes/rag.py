from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from llama_index.core.schema import Document
from typing import List, Optional, Union
import shutil
import os
import uuid
import json
from datetime import datetime
from app.modules.loaders import load_file
from app.services.score_candidate_service import openai_service
from app.prompts.resumes import extract_resume
from app.prompts.job_description import extract_jd
from app.llms.azure_openai_client import azure_client
from app.core.config import settings
from app.core.security import get_current_user
from app.db.neo4j import (
    Neo4jDB,
    get_db
)
from app.db.qdrant import vector_search
from pydantic import BaseModel
from app.services.crawl_jd_service import crawl_and_extract

router = APIRouter(prefix="/api/v1", tags=["Upload data to Vector Database"])


@router.post("/upload-resume/")
async def load_documents(
    files: List[UploadFile] = File(...),
    db: Neo4jDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    processing_results = []
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed.")
    for file in files:
        file_result = {"filename": file.filename, "status": "processing"}
        if not file.filename:
            file_result.update({"status": "error", "error": "Filename is required"})
            processing_results.append(file_result)
            continue
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(temp_dir, unique_filename)
        talent_id = str(uuid.uuid4())
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        except Exception as e:
            file_result.update({"status": "error", "error": f"Error saving file: {e}"})
            processing_results.append(file_result)
            continue
        try:
            documents = load_file(file_path)
            if not documents:
                file_result.update({"status": "error", "error": "No documents found in file"})
                processing_results.append(file_result)
                continue
            prompt = extract_resume(documents)
            llm_response = azure_client.invoke_model(prompt)
            parse_json_llm = azure_client.parse_json_string(llm_response)
            print(f"Parsed JSON from LLM: {llm_response}")
            full_name = parse_json_llm.get("full_name")

            db.process_cv(parse_json_llm, talent_id, full_name)

            doc_metadata = {
                "source_file": file.filename,
                "talent_id": talent_id,
                "full_name": full_name,
                "processing_timestamp": datetime.now().isoformat(),
                "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else "unknown",
                "file_size": file.size if hasattr(file, 'size') else None,
            }

            docs = [Document(text=json.dumps(parse_json_llm, ensure_ascii=False), metadata=doc_metadata)]
            vector_search.create_vector_index(docs, settings.QDRANT_COLLECTION_NAME)

            file_result.update({"status": "success", "metadata": doc_metadata})
        except Exception as e:
            file_result.update({"status": "error", "error": f"Error processing file: {e}"})
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not remove {file_path}: {cleanup_error}")
        processing_results.append(file_result)
    successful_files = [r for r in processing_results if r["status"] == "success"]
    failed_files = [r for r in processing_results if r["status"] == "error"]

    return {
        "message": f"Processed {len(files)} files: {len(successful_files)} successful, {len(failed_files)} failed",
        "total_files": len(files),
        "successful_count": len(successful_files),
        "failed_count": len(failed_files),
        "file_results": processing_results
    }

@router.post("/upload-jd-from-linkedin/")
async def upload_jd_from_file(
    job_title: str = "Software Engineer",
    db: Neo4jDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Đọc jobs.json, extract JD và lưu vào Neo4j
    """
    
    try:
        jobs = await crawl_and_extract(job_title, "Vietnam", max_pages=2, sleep_between=(2, 5))
        results = []
        for job in jobs:
            title = job.get("title")
            company = job.get("company")
            description = job.get("description")
            link = job.get("link")

            prompt = extract_jd(description)
            llm_response = azure_client.invoke_model(prompt)

            db.create_job_description(
                file_path="None",
                url=link,
                type_="",
                jd=llm_response
            )

            results.append({
                "title": title,
                "company": company,
                "url": link,
                "processed_jd": llm_response
            })

        return {"status": "success", "count": len(results), "data": results}

    except Exception as e:
        return {"status": "error", "message": str(e)}

class JDRequest(BaseModel):
    url: Optional[str] = None
    type: Optional[str] = None
    jd: Optional[str] = None


@router.post("/upload-jd/")
async def upload_jd(
    file: Union[UploadFile, str, None] = File(None),
    url: Optional[str] = Form(None),
    type_: Optional[str] = Form(None),
    db: Neo4jDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Upload JD file or URL -> read content -> save to Neo4j
    """
    file_path = None
    jd_text = None
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if file and isinstance(file, UploadFile) and file.filename:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        documents = load_file(file_path)
        jd_text = " ".join([doc.text for doc in documents]) if documents else None

    elif url:
        documents = load_file([url])
        jd_text = " ".join([doc.text for doc in documents]) if documents else None

    else:
        return {"error": "You must provide either a file or a URL"}

    if not jd_text:
        return {"error": "Could not read JD content"}

    prompt = extract_jd(jd_text)
    llm_response = azure_client.invoke_model(prompt)

    db.create_job_description(
        file_path=file_path,
        url=url,
        type_=type_,
        jd=llm_response
    )
    db.close()

    return {
        "message": "JD uploaded successfully",
        "file_path": file_path,
        "url": url,
        "type": type_,
        "jd_preview": jd_text[:300]
    }


@router.get("/api/v1/jds/")
async def list_jds(limit: int = Query(20, description="Maximum number of JDs to retrieve"),
                   db: Neo4jDB = Depends(get_db),
                   current_user: str = Depends(get_current_user)
                   ):
    jds = db.get_job_descriptions(limit=limit)

    results = []
    for jd in jds:
        results.append({
            "file_path": jd.get("file_path"),
            "url": jd.get("url"),
            "type": jd.get("type"),
            "jd_preview": jd.get("jd"),
        })

    return {"count": len(results), "items": results}


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
