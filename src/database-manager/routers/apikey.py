#FIXME: duplicate defs in the routers and crud.py may be the cause of the Duplicate ID problem?
# however like this in many examples? 

from routers.dependencies import *

@router.post("/apikey/", response_model=schemas.ApiKey)
def create_apikey(apikey: schemas.ApiKeyCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_apikey(db, database.mac=device.mac)
    return crud.create_apikey(db=db,  apikey = apikey)


@router.get("/apikeys/", response_model=List[schemas.ApiKey])
def read_apikey(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    apikeys = crud.get_apikeys(db, skip=skip, limit=limit)
    return apikeys


@router.get("/apikey/{apikey_id}", response_model=schemas.ApiKey)
def read_apikey(apikey_id: int, db: Session = Depends(get_db)):
    db_apikey = crud.get_apikey(db, apikey_id=apikey_id)
    if db_apikey is None:
        raise HTTPException(status_code=404, detail="ApiKey not found")
    return db_apikey
    
