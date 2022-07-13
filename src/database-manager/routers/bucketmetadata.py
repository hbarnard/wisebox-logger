from routers.dependencies import *


@router.post("/bucketmetadata/", response_model=schemas.BucketMetadata)
def create_bucketmetadata(bucketmetadata: schemas.BucketMetadataCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_bucketmetadata(db, database.mac=device.mac)
    return crud.create_bucketmetadata(db=db,  bucketmetadata = bucketmetadata)


@router.get("/bucketmetadatas/", response_model=List[schemas.BucketMetadata])
def read_bucketmetadata(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bucketmetadatas = crud.get_bucketmetadatas(db, skip=skip, limit=limit)
    return bucketmetadatas


@router.get("/bucketmetadata/{bucketmetadata_id}", response_model=schemas.BucketMetadata)
def read_bucketmetadata(bucketmetadata_id: int, db: Session = Depends(get_db)):
    db_bucketmetadata = crud.get_bucketmetadata(db, bucketmetadata_id=bucketmetadata_id)
    if db_bucketmetadata is None:
        raise HTTPException(status_code=404, detail="BucketMetadata not found")
    return db_bucketmetadata
    
