# main.py
# FastAPI 기반 간단한 사용자 인증 API

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

# FastAPI 애플리케이션 인스턴스 생성
# title: API 문서에 표시될 제목
# version: API 버전 관리
app = FastAPI(
    title="User Authentication API",
    version="1.0.0",
    description="간단한 사용자 인증 시스템 API"
)

# Pydantic 모델 정의 - 요청/응답 데이터 검증
class User(BaseModel):
    """사용자 정보를 담는 데이터 모델"""
    id: Optional[int] = None
    username: str
    email: EmailStr  # 이메일 형식 자동 검증
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    """사용자 생성 요청 데이터 모델"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# 메모리 기반 임시 데이터베이스 (실무에서는 PostgreSQL, MongoDB 등 사용)
fake_users_db = []
user_id_counter = 1

# 루트 엔드포인트 - 헬스체크용
@app.get("/")
async def root():
    """
    API 헬스체크 엔드포인트
    
    Returns:
        dict: 서비스 상태 정보
    """
    return {
        "status": "healthy",
        "message": "User Authentication API is running",
        "version": "1.0.0"
    }

# 모든 사용자 조회
@app.get("/users", response_model=list[User])
async def get_users():
    """
    등록된 모든 사용자 목록 조회
    
    Returns:
        list[User]: 사용자 목록 (비밀번호 제외)
    """
    return fake_users_db

# 특정 사용자 조회
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    특정 사용자 정보 조회
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        User: 사용자 정보
        
    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
    """
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

# 새로운 사용자 등록
@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """
    새로운 사용자 등록
    
    Args:
        user: 사용자 생성 정보
        
    Returns:
        User: 생성된 사용자 정보
        
    Raises:
        HTTPException: 이미 존재하는 사용자인 경우 400 에러
    """
    global user_id_counter
    
    # 중복 확인
    for existing_user in fake_users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=400, 
                detail="이미 존재하는 사용자명입니다"
            )
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=400, 
                detail="이미 존재하는 이메일입니다"
            )
    
    # 새 사용자 생성
    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name
    }
    fake_users_db.append(new_user)
    user_id_counter += 1
    
    return new_user

# 사용자 정보 수정
@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate):
    """
    사용자 정보 수정
    
    Args:
        user_id: 수정할 사용자 ID
        user: 수정할 사용자 정보
        
    Returns:
        User: 수정된 사용자 정보
        
    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
    """
    for idx, existing_user in enumerate(fake_users_db):
        if existing_user["id"] == user_id:
            updated_user = {
                "id": user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
            fake_users_db[idx] = updated_user
            return updated_user
    
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

# 사용자 삭제
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """
    사용자 삭제
    
    Args:
        user_id: 삭제할 사용자 ID
        
    Returns:
        dict: 삭제 결과 메시지
        
    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
    """
    for idx, user in enumerate(fake_users_db):
        if user["id"] == user_id:
            fake_users_db.pop(idx)
            return {"message": "사용자가 성공적으로 삭제되었습니다"}
    
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

# 직접 실행 시 (개발 환경)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)