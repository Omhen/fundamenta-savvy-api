from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.company import Company
from app.schemas import company as company_schema

router = APIRouter()


@router.get("/", response_model=List[company_schema.Company])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of companies.
    """
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=company_schema.Company)
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a single company by ID.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return company


@router.get("/ticker/{ticker}", response_model=company_schema.Company)
def get_company_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a company by ticker symbol.
    """
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker {ticker} not found"
        )
    return company


@router.post("/", response_model=company_schema.Company, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: company_schema.CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new company.
    """
    existing_company = db.query(Company).filter(Company.ticker == company_in.ticker).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with ticker {company_in.ticker} already exists"
        )

    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.put("/{company_id}", response_model=company_schema.Company)
def update_company(
    company_id: int,
    company_in: company_schema.CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a company.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a company.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    db.delete(company)
    db.commit()
    return None
