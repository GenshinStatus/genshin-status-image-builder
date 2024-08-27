from pydantic import BaseModel
from typing import Optional


class Icon(BaseModel):
    name: str
    path: str


class NameCard(BaseModel):
    icon: Icon


class Weapon(BaseModel):
    icon: Icon
    name: str


class Artifact(BaseModel):
    icon: Icon
    set_name: Optional[str] = None
    equip_type: str


class Skill(BaseModel):
    name: str
    icon: Icon
    id: str
    proud_id: str


class Position(BaseModel):
    x: Optional[int] = -221
    y: Optional[int] = 34
    scale: Optional[int] = 97


class Costume(BaseModel):
    side_icon: Icon
    avatar_icon: Icon
    gacha_icon: Icon
    position: Position


class JpCharacterModel(BaseModel):
    element: str
    consts: list[Icon]
    skills: list[Skill]
    name: str
    english_name: str
    proud_map: dict[str, str]
    quality: int
    costumes: dict[str, Costume]

class Pfps(BaseModel):
    name: str
    icon: Icon
