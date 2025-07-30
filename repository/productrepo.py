# repository/productrepo.py
from fastapi import status, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database_file import models, schemas_products

def create_category(request: schemas_products.AddCategory, db : Session):
    try :
        category = db.query(models.Categories).filter(models.Categories.category_name == request.category_name).first()
        if category:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Category is already listed.")
            
        new_category = models.Categories(
                            category_name = request.category_name, 
                            description = request.description
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    
def add_product(request: schemas_products.AddProduct, db : Session):
    try :
        product = db.query(models.Products).filter(models.Products.product_name == request.product_name).first()
        category = db.query(models.Categories).filter(models.Categories.category_id == request.category_id).first()
        if product:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Product is already listed.")
        elif not category:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Category is not listed.")
            
        new_product = models.Products(
                            product_name = request.product_name, 
                            category_id = request.category_id,
                            unit = request.unit,
                            price = request.price
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))



def list_products(db : Session):
    try :
        products = db.query(models.Products).all()
        
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no Product listed.")

        return products
    except Exception as e:
        print(f"Exception Occure while Product Fatching : {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exception Occure while Product Fatching : {e}")
    
def list_product(db: Session, id: int = 0, name: str = ""):
    try:
        product = None

        if id != 0 and name:
            product = db.query(models.Products).filter(
                and_(
                    models.Products.product_id == id,
                    models.Products.product_name == name
                )
            ).first()
        elif id != 0:
            product = db.query(models.Products).filter(models.Products.product_id == id).first()
        elif name:
            product = db.query(models.Products).filter(models.Products.product_name == name).first()

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        return product

    except Exception as e:
        print(f"Exception occurred while fetching product: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exception: {e}")

    
def list_categories(db : Session):
    try :
        categories = db.query(models.Categories).all()
        
        if not categories:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no Product listed.")

        return categories
    except Exception as e:
        print(f"Exception Occure while Categories Fatching : {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exception Occure while Categories Fatching : {e}")
    
def list_category(db : Session, id : int = 0, name: str = ""):
    try :
        category : models.Categories
        if id == 0:
            category = db.query(models.Categories).filter(models.Categories.category_name == name).first()
        elif name == "":
            category = db.query(models.Categories).filter(models.Categories.category_id == id).first()
        else:
            category = db.query(models.Categories).filter(
                models.Categories.category_id == id,
                models.Categories.category_name == name
            ).first()
            
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no Category listed.")

        return category
    except Exception as e:
        print(f"Exception Occure while Product Fatching : {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exception : {e}")
    
    
def update_product_stock(db : Session, id : int, Stock_Increase_By: int):
    product = db.query(models.Products).filter(models.Products.product_id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not Found.")

    product.unit += Stock_Increase_By
    db.commit()
    db.refresh(product)
    
    return product