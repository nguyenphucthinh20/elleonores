from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from typing import Optional, Union
import shutil
import os
from app.modules.loaders import load_file
from app.prompts.job_description import extract_jd
from app.llms.azure_openai_client import azure_client
from app.core.security import get_current_user
from app.db.neo4j import (
    Neo4jDB,
    get_db
)
import uuid
from app.services.crawl_jd_service import crawl_and_extract

router = APIRouter(prefix="/api/v1", tags=["Job descripton"])


@router.post("/get-jd-from-linkedin/")
async def get_jd_from_file(
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
                jd_id=str(uuid.uuid4()),
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
        jd_id=str(uuid.uuid4()),
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

@router.get("/jds/")
async def list_jds(limit: int = Query(20, description="Maximum number of JDs to retrieve"),
                   db: Neo4jDB = Depends(get_db),
                   current_user: str = Depends(get_current_user)
                   ):
    jds = db.get_job_descriptions(limit=limit)

    results = []
    for jd in jds:
        results.append({
            "id": jd.get("id"),
            "file_path": jd.get("file_path"),
            "url": jd.get("url"),
            "type": jd.get("type"),
            "jd_preview": jd.get("jd"),
        })

    return {"count": len(results), "items": results}

@router.delete("/job_descriptions/{jd_id}")
async def delete_job_description(jd_id: str,
                            db: Neo4jDB = Depends(get_db),
                            current_user: str = Depends(get_current_user)
                            ):
    """
    Delete JobDescription by jd_id
    """
    result = db.delete_jd(jd_id)
    return {"message": result}