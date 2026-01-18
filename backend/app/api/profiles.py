"""
Profile API Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.profile import Profile, Skill, Education, Experience
from app.schemas.profile import (
    ProfileCreate, ProfileUpdate, ProfileResponse,
    SkillCreate, SkillResponse,
    EducationCreate, EducationResponse,
    ExperienceCreate, ExperienceResponse
)


router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile"""
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == current_user.id)
        .options(
            selectinload(Profile.skills),
            selectinload(Profile.education),
            selectinload(Profile.experience)
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse.model_validate(profile)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == current_user.id)
        .options(
            selectinload(Profile.skills),
            selectinload(Profile.education),
            selectinload(Profile.experience)
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return ProfileResponse.model_validate(profile)


# Skills endpoints
@router.post("/me/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a skill to profile"""
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    skill = Skill(profile_id=profile.id, **skill_data.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    
    return SkillResponse.model_validate(skill)


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a skill"""
    result = await db.execute(
        select(Skill)
        .join(Profile)
        .where(Skill.id == skill_id, Profile.user_id == current_user.id)
    )
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    await db.delete(skill)
    await db.commit()


# Education endpoints
@router.post("/me/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def add_education(
    edu_data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add education to profile"""
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    education = Education(profile_id=profile.id, **edu_data.model_dump())
    db.add(education)
    await db.commit()
    await db.refresh(education)
    
    return EducationResponse.model_validate(education)


@router.delete("/me/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete education entry"""
    result = await db.execute(
        select(Education)
        .join(Profile)
        .where(Education.id == education_id, Profile.user_id == current_user.id)
    )
    education = result.scalar_one_or_none()
    
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    
    await db.delete(education)
    await db.commit()


# Experience endpoints
@router.post("/me/experience", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def add_experience(
    exp_data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add work experience to profile"""
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    experience = Experience(profile_id=profile.id, **exp_data.model_dump())
    db.add(experience)
    await db.commit()
    await db.refresh(experience)
    
    return ExperienceResponse.model_validate(experience)


@router.delete("/me/experience/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete experience entry"""
    result = await db.execute(
        select(Experience)
        .join(Profile)
        .where(Experience.id == experience_id, Profile.user_id == current_user.id)
    )
    experience = result.scalar_one_or_none()
    
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    await db.delete(experience)
    await db.commit()
