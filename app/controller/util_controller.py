from fastapi import APIRouter
from fastapi.responses import Response
import service.repo_to_json as repo_to_json
import service.score_calc as score_calc
import service.character_position_service as chara_position
import service.enka_image_downloader as enka_image_downloader
from model.response_json_model import CharacterPosition
from repository.util_repository import \
    CHARACTER_DATA_DICT, update_character_model_dict

router = APIRouter(prefix="/util", tags=["util"])


@router.put("/update-image")
async def get_status():
    result = await repo_to_json.updates()
    if result:
        return Response(status_code=201)
    else:
        return Response(status_code=204)


@router.get("/buildtypelist")
async def get_build_type_list():
    return score_calc.BUILD_NAMES


@router.get("/position-list")
async def get_position_data():
    return await chara_position.get_character_positions()


@router.put("/updat-eposition")
async def update_position(position: CharacterPosition):
    await chara_position.update_position_data(
        english_name=position.english_name,
        costume_id=position.id,
        position=position.position
    )
    return Response(content="position update!", status_code=201)

@router.put("/update-image-only")
async def update_image_only():
    await enka_image_downloader.util_image_update()
    return Response(status_code=200)

@router.get("/name-to-id/{name}")
async def get_name_to_id(name: str):
    update_character_model_dict()
    print(CHARACTER_DATA_DICT)
    for k, v in CHARACTER_DATA_DICT.items():
        if v.name == name:
            return {"id":k, "name":name}
    return Response(content="Character not found.", status_code=404)