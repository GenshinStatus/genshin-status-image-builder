from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import service.score_calc as score_calc
import model.util_model as util_model
from repository.util_repository import \
    CHARACTER_DATA_DICT, WEAPON_DATA_DICT, ARTIFACT_DATA_DICT, STATUS_NAMEHASH_DICT

ELEMENTAL_NAME_DICT = {
    "Physics": "物理ダメージ",
    "Fire": "炎元素ダメージ",
    "Electric": "雷元素ダメージ",
    "Water": "水元素ダメージ",
    "Grass": "草元素ダメージ",
    "Wind": "風元素ダメージ",
    "Rock": "岩元素ダメージ",
    "Ice": "氷元素ダメージ",
}

class Artifact(BaseModel):
    icon_name: str
    main_name: str
    score: Decimal = Decimal(0.0)
    util: Optional[util_model.Artifact] = None

    def set_util(self):
        self.util = ARTIFACT_DATA_DICT[self.icon_name]

    @property
    def main_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]


class Weapon(BaseModel):
    icon_name: str
    sub_name: Optional[str] = None
    level: int
    rank: int
    util: Optional[util_model.Weapon] = None

    @property
    def sub_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.sub_name]

    def set_util(self):
        self.util = WEAPON_DATA_DICT[self.icon_name]


class Skill(BaseModel):
    level: int
    add_level: int
    util: Optional[util_model.Skill] = None

    def set_util(self, skill: util_model.Skill):
        self.util = skill


class Character(BaseModel):
    id: str
    constellations: int
    level: int
    added_hp: int
    added_attack: int
    added_defense: int
    critical_rate: Decimal
    critical_damage: Decimal
    charge_efficiency: Decimal
    elemental_mastery: int
    elemental_name: Optional[str] = None
    elemental_value: Optional[str] = None
    skills: list[Skill]
    artifacts: dict[str, Artifact]
    weapon: Weapon
    costume_id: str = "defalut"
    build_type: Optional[str] = None
    costume: Optional[util_model.Costume] = None
    util: Optional[util_model.JpCharacterModel] = None

    @property
    def constellation_list(self):
        return self.util.consts[:self.constellations]

    @property
    def build_name(self):
        return score_calc.BUILD_NAMES[self.build_type]

    @property
    def elemental_jp_name(self):
        return ELEMENTAL_NAME_DICT.get(self.elemental_name)

    def init_utils(self):
        self.util = CHARACTER_DATA_DICT[self.id]
        self.costume = self.util.costumes[self.costume_id]
        for v in self.artifacts.values():
            v.set_util()
        self.weapon.set_util()
        for skill, util_skill in zip(self.skills, self.util.skills):
            skill.set_util(util_skill)

class RankingData(BaseModel):
    rank: int
    uid: int
    level: int
    nickname: str
    create_date: str
    character: Character

    def init_utils(self):
        self.character.init_utils()