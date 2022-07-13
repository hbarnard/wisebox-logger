from routers.dependencies import *


@router.post("/bucket/", response_model=schemas.Bucket)
def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_bucket(db, database.mac=device.mac)
    return crud.create_bucket(db=db,  bucket = bucket)


@router.get("/buckets/", response_model=List[schemas.Bucket])
def read_bucket(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    buckets = crud.get_buckets(db, skip=skip, limit=limit)
    return buckets


@router.get("/bucket/{bucket_id}", response_model=schemas.Bucket)
def read_bucket(bucket_id: int, db: Session = Depends(get_db)):
    db_bucket = crud.get_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return db_bucket
    
