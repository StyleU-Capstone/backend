import os
import shutil
import uuid

import httpx
from fastapi import HTTPException, UploadFile

from config import (
    PREDICT_COLOR_TYPE_LLM_URL,
    PREDICT_BODY_TYPE_ML_URL,
    PREDICT_BODY_TYPE_LLM_URL,
    PREDICT_COLOR_TYPE_URL,
)
from databases.database_connector import DatabaseConnector
from services.llm_connector import send_llm_request


async def analyze_body_type(sex, height, bust, waist, hips, username=None):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            ml_response = await client.post(PREDICT_BODY_TYPE_ML_URL, json={
                "bust": bust, "waist": waist, "hips": hips, "height": height, "sex": sex,
            })
            ml_response.raise_for_status()
            body_type = ml_response.json()["body_type"]
            if not body_type:
                raise HTTPException(status_code=500, detail="ML-service returned empty body_type")

            llm_response = await send_llm_request(PREDICT_BODY_TYPE_LLM_URL, {"body_type": body_type, "sex": sex})
            recommendation = llm_response

        if username:
            async with DatabaseConnector() as connector:
                user_id = await connector.get_user_id(username)
                await connector.add_user_parameters(
                    user_id,
                    sex = sex,
                    height=height,
                    bust=bust,
                    waist=waist,
                    hips=hips,
                    body_type=body_type,
                    body_type_recommendation=recommendation,
                )

        return {"body_type": body_type, "recommendation": recommendation}

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def analyze_color_type(file: UploadFile, username=None):
    suffix = os.path.splitext(file.filename)[-1]
    temp_path = f"/tmp/{uuid.uuid4()}{suffix}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            file.file.seek(0)
            files = {'file': (file.filename, file.file, file.content_type)}

            response = await client.post(PREDICT_COLOR_TYPE_URL, files=files)
            response.raise_for_status()
            color_type = response.json().get("color_type")
            if not color_type:
                raise HTTPException(status_code=500, detail="ML-service returned empty color_type")

            llm_response = await send_llm_request(PREDICT_COLOR_TYPE_LLM_URL, {"color_type": color_type})
            recommendation = llm_response

        if username:
            file.file.seek(0)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            async with DatabaseConnector() as connector:
                user_id = await connector.get_user_id(username)
                await connector.add_user_parameters(
                    user_id,
                    color_type=color_type,
                    color_type_recommendation=recommendation,
                )
                await connector.save_user_photo(username, temp_path)
                await connector.delete_avatar(username)

        return {"color_type": color_type, "recommendation": recommendation}

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


async def get_user_features(username: str) -> dict:
    async with DatabaseConnector() as connector:
        return await connector.get_user_features(username)
