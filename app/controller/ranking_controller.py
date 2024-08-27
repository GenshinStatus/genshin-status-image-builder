from fastapi import APIRouter
from fastapi.responses import FileResponse
import service.gen_ranking_user_image as gen_ranking_user_image
import model.status_model as status_model
import model.ranking_model as ranking_model


router = APIRouter(prefix="/rankingimage", tags=["ranking image generator"])


@router.post("/get_user/{gen_type}/")
def get_ranking_user_image(ranking_data: ranking_model.RankingData, highlight:int=0):
    # 0->hp, 1->atack, 2->defense, 3->critical, 4->mastery, 5->elemental
    filename = f"{ranking_data.create_date}_{ranking_data.uid}_{ranking_data.character.id}_{ranking_data.character.build_type}_{highlight}.png"
    file_path = f"ranking_images/{filename}"
    gen_ranking_user_image.save_image(
        file_path=file_path,
        ranking_data=ranking_data,
    )
    return FileResponse(file_path, filename=filename)