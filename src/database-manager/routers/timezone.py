from routers.dependencies import *

@router.post("/timezone/", response_model=schemas.Timezone)
def create_timezone(timezone: schemas.TimezoneCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_timezone(db, database.mac=device.mac)
    return crud.create_timezone(db=db,  timezone = timezone)


@router.get("/timezones/", response_model=List[schemas.Timezone])
def read_timezone(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    timezones = crud.get_timezones(db, skip=skip, limit=limit)
    return timezones


@router.get("/timezone/{timezone_id}", response_model=schemas.Timezone)
def read_timezone(timezone_id: int, db: Session = Depends(get_db)):
    db_timezone = crud.get_timezone(db, timezone_id=timezone_id)
    if db_timezone is None:
        raise HTTPException(status_code=404, detail="Timezone not found")
    return db_timezone
    
