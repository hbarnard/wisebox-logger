from routers.dependencies import *


@router.post("/organisation/", response_model=schemas.Organisation)
def create_organisation(organisation: schemas.OrganisationCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_organisation(db, database.mac=device.mac)
    return crud.create_organisation(db=db,  organisation = organisation)


@router.get("/organisations/", response_model=List[schemas.Organisation])
def read_organisation(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organisations = crud.get_organisations(db, skip=skip, limit=limit)
    return organisations


@router.get("/organisation/{organisation_id}", response_model=schemas.Organisation)
def read_organisation(organisation_id: int, db: Session = Depends(get_db)):
    db_organisation = crud.get_organisation(db, organisation_id=organisation_id)
    if db_organisation is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return db_organisation
    
