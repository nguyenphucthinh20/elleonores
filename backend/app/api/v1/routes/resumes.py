from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from llama_index.core.schema import Document
from typing import List, Optional, Union
import shutil
import os
import uuid
import json
from datetime import datetime
from app.modules.loaders import load_file
from app.prompts.resumes import extract_resume
from app.llms.azure_openai_client import azure_client
from app.core.config import settings
from app.core.security import get_current_user
from app.db.neo4j import (
    Neo4jDB,
    get_db
)
from app.db.qdrant import vector_search

router = APIRouter(prefix="/api/v1", tags=["Resumes"])


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

@router.get("/resume/{talent_id}")
def get_resume(talent_id: str):
    resume = vector_search.get_resume_by_talent_id(settings.QDRANT_COLLECTION_NAME, 
                                                   talent_id)
    if not resume:
        raise HTTPException(status_code=404, detail=f"talent_id {talent_id} not found.")
    return {"resume": resume}

@router.get("/resumes/all")
def get_all_resumes():
    resumes = vector_search.get_all_resumes(settings.QDRANT_COLLECTION_NAME)
    if not resumes:
        raise HTTPException(status_code=404, detail="There is no resume in the system.")
    return {"resumes": resumes}

@router.delete("/candidates/{talent_id}")
async def delete_candidate(talent_id: str):

    message = vector_search.delete_candidate_by_talent_id(settings.QDRANT_COLLECTION_NAME, 
                                                          talent_id)

    return {"message": message}