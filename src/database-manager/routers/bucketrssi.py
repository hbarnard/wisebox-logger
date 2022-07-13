from routers.dependencies import *

@router.post("/bucketrssi/", response_model=schemas.BucketRssi)
def create_bucketrssi(bucketrssi: schemas.BucketRssiCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_bucketrssi(db, database.mac=device.mac)
    return crud.create_bucketrssi(db=db,  bucketrssi = bucketrssi)


@router.get("/bucketrssis/", response_model=List[schemas.BucketRssi])
def read_bucketrssi(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bucketrssis = crud.get_bucketrssis(db, skip=skip, limit=limit)
    return bucketrssis


@router.get("/bucketrssi/{bucketrssi_id}", response_model=schemas.BucketRssi)
def read_bucketrssi(bucketrssi_id: int, db: Session = Depends(get_db)):
    db_bucketrssi = crud.get_bucketrssi(db, bucketrssi_id=bucketrssi_id)
    if db_bucketrssi is None:
        raise HTTPException(status_code=404, detail="BucketRssi not found")
    return db_bucketrssi
    
