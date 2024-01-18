from pathlib import Path
from secrets import token_urlsafe
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from app.utils.security import is_valid_image
from app import schema, oauth2

router = APIRouter(prefix="/payment_proof")

@router.post("/")
async def upload_payment_screenshot(image_file: UploadFile = File()):
    file_content = await image_file.read()
    file_name = image_file.filename
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="o.o You don't have the screenshot image?"
        )
    if not is_valid_image(file_name, file_content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, JPEG and PNG image files are allowed"
        )
    ID = token_urlsafe(32)
    new_filename = f"{ID}.{file_name.split('.')[-1]}"
    file_path = Path("payment_proof") / new_filename
    with file_path.open("wb") as buffer:
        buffer.write(file_content)
    return {"screenshot_id": new_filename}

@router.get("/view")
def get_payment_screenshot(_id: str = Query(..., alias="id"), _: schema.MemberOut = Depends(oauth2.get_current_member)):
    screenshot_path = Path("payment_proof") / _id
    if not screenshot_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There isn't any Screenshot which belongs to that ID"
        )
    return FileResponse(screenshot_path)

