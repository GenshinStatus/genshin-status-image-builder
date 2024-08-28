from io import BytesIO
from lib.gen_image import GImage, Colors, Algin, Anchors, ImageAnchors
from concurrent.futures import ThreadPoolExecutor, Future
import model.ranking_model as ranking_model
import model.util_model as util_model
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
from repository.assets_repository import ASSETS
from decimal import Decimal
import lib.cache_image as cache_image


def __create_background(chara_costume: util_model.Costume) -> GImage:
    """キャラ画像を合成したバックグラウンドを生成します。

    Args:
        element (str): 属性の名前
        chara_icon (ranking_model.RankingData.character.costume): キャラのcostume

    Returns:
        GImage: 合成した画像
    """
    # 背景画像
    img = GImage(
        box_size=(720, 140),
        default_font_size=26,
    )

    # 背景画像
    img_character = GImage(
        box_size=(720, 140),
        default_font_size=26,
    )

    # 背景キャラ画像
    img_character.add_image(
        box=(60, -148),
        size=(900, 450),
        image_path=chara_costume.gacha_icon.path,
    )

    enhancer = ImageEnhance.Brightness(img_character.get_image())
    img_character = enhancer.enhance(0.3)

    img.paste(im=img_character, box=(0, 0))

    # キャラ画像
    img.add_image(
        box=(70, 0),
        size=(140, 140),
        image_path=chara_costume.avatar_icon.path,
    )

    # 背景オーバーレイ
    img.add_image(
        box=(0, 0),
        image_path=ASSETS.ranking.background_shadow,
    )
    
    return img


def __create_lv_and_const(lv: int, constellations: int,  chara_costume: util_model.Costume) -> Image.Image:
    """レベル、凸のイメージを作成します

    Args:
        lv (int): レベル
        constellations (int): 凸
        chara_costume (ranking_model.RankingData.character.costume): キャラのcostume

    Returns:
        Image: 合成した画像
    """
    totu = [
        "無", "1", "2", "3", "4", "5", "完"
    ]

    img = GImage(
        box_size=(86, 42),
        default_font_size=12,
    )
    # レベルと凸
    img.draw_text(
        text=f'Lv {lv}\n{totu[constellations]}凸',
        position=(48, 12),
        align=Algin.LEFT,
    )

    img.add_image(
        box=(0, 0),
        size=(42, 42),
        image_path=chara_costume.side_icon.path,
    )

    return img.get_image()


def __create_status_highlight(add: int, path: str, suffix="", plus="") -> Image.Image:
    """キャラクターのハイライトするべき個別のステータスの画像を取得します。

    Args:
        add (int): 装備による追加の数値
        path (str): ステータスのアイコンのパス
        suffix (str): 後ろにつける文字. Defaults to "%".
        plus (str): 前につける文字. Defaults to "+".

    Returns:
        Image: キャラクターの個別のステータスの画像
    """

    img = GImage(
        box_size=(80, 16),
        default_font_size=10,
    )

    img.add_image(
        image_path=path,
        box=(0, 0),
        size=(16, 16),
        image_anchor=ImageAnchors.LEFT_TOP
    )

    textimg = GImage(
        box_size=(80, 80),
        default_font_size=10,
    )

    # 値の合成
    textimg.draw_text(
        text=f"{plus}{add}{suffix}",
        position=(24, 2),
        anchor=Anchors.LEFT_TOP,
        font_size=10,
        font_color=Colors.WHITE,
    )

    img.paste_with_shadow(
        im=textimg.get_image(),
        box=(0, 0),
        shadow_color=Colors.WHITE,
        shadow_offset=(0, 0),
        blur_radius=2,
        shadow_size=0,
        shadow_opacity=1,
    )

    return img.get_image()


def __create_status(status: Decimal, path: str, suffix="", plus="") -> Image.Image:
    """キャラクターの個別のステータスの画像を取得します。suffixは％などの文字列、plusは＋などの文字列です。

    Args:
        status (int): ステータスの数値
        path (str): ステータスのアイコンのパス
        suffix (str): 後ろにつける文字. Defaults to "%".
        plus (str): 前につける文字. Defaults to "+".
        
    Returns:
        Image.Image: キャラクターの個別のステータス画像
    """
    img = GImage(
        box_size=(80, 16),
        default_font_size=10,
    )

    img.add_image(
        image_path=path,
        box=(0, 0),
        size=(16, 16),
        image_anchor=ImageAnchors.LEFT_TOP
    )

    # ステータスの合成
    img.draw_text(
        text=f"{plus}{status}{suffix}",
        position=(24, 2),
        anchor=Anchors.LEFT_TOP,
        font_size=10,
        font_color=Colors.GRAY,
    )

    return img.get_image()


def __create_full_status(
    hp_add: int,
    atk_add: int,
    df_add: int,
    mas: int,
    cri: Decimal,
    cri_dmg: Decimal,
    mas_chg: Decimal,
    elmt: str = None,
    elmt_dmg: int = None,
    element_icon: str = None,
) -> Image.Image:
    """すべてのステータスのデータを取得します。

    Args:
        hp_add (int): 装備HP
        atk_add (int): 装備攻撃
        df_add (int): 装備防御
        mas (int): 元素熟知
        cri (float): 会心率
        cri_dmg (float): 会心ダメージ率
        mas_chg (float): 元素チャージ
        elmt (str, optional): 元素タイプ. Defaults to None.
        elmt_dmg (int, optional): 元素倍率. Defaults to None.
        element_icon (str, optional): 元素アイコン. Defaults to None.

    Returns:
        Image.Image: ステータスの画像
    """

    img = GImage(
        box_size=(183, 85),
        default_font_size=10,
    )
    futures: list[Future] = []
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_status") as pool:
        # HP
        futures.append(
            pool.submit(
                __create_status_highlight,
                hp_add,
                ASSETS.icon.status.hp,
                "",
                "+"
            )
        )
        # 攻撃
        futures.append(
            pool.submit(
                __create_status,
                atk_add,
                ASSETS.icon.status.attack,
                "",
                "+"
            )
        )
        # 防御
        futures.append(
            pool.submit(
                __create_status,
                df_add,
                ASSETS.icon.status.diffence,
                "",
                "+"
            )
        )
        # 元素熟知
        futures.append(
            pool.submit(
                __create_status,
                mas,
                ASSETS.icon.status.element,
                "",
                "+"
            )
        )
        # クリ率
        futures.append(
            pool.submit(
                __create_status,
                cri,
                ASSETS.icon.status.critical,
                "%",
                ""
            )
        )
        # クリダメ
        futures.append(
            pool.submit(
                __create_status,
                cri_dmg,
                ASSETS.icon.status.critical_per,
                "%",
                ""
            )
        )
        # 元チャ
        futures.append(
            pool.submit(
                __create_status,
                mas_chg,
                ASSETS.icon.status.element_charge,
                "%",
                ""
            )
        )
        # 元素攻撃力
        if elmt is not None:
            futures.append(
                pool.submit(
                    __create_status,
                    elmt_dmg,
                    element_icon,
                    "",
                    ""
                )
            )

    for i, f in enumerate(futures):
        im: Image = f.result()
        # 各画像を合成します
        if i > 3:
            width = 95
            height = 23*(i-4)
        else:
            width = 0
            height = 23*i
        img.paste(im=im, box=(width, height))

    return img.get_image()


def __create_skill(skills: list[ranking_model.Skill]) -> Image.Image:
    """スキルの画像を生成します

    Args:
        skills (list[Skill]): スキルのリスト

    Returns:
        Image.Image: スキル画像
    """

    img = GImage(
        box_size=(68, 30),
        default_font_size=10,
    )
    # スキルレベルの合成
    img.draw_text(
        text="天賦レベル",
        position=(0, 0),
        anchor=Anchors.LEFT_TOP,
        font_color=Colors.GRAY,
        font_size=10
    )
    skill_text = ""
    for i, skill in enumerate(skills):
        skill_text += f"{skill.level + skill.add_level}"
        if i != len(skills)-1:
            skill_text += " / "

    img.draw_text(
        text=str(skill_text),
        position=(0, 15),
        anchor=Anchors.LEFT_TOP,
        font_size=13
    )

    return img.get_image()


def __create_artifact(artifact: ranking_model.Artifact) -> Image.Image:
    """個別の聖遺物の画像を生成します。

    Args:
        artifact (artifact): アーティファクトオブジェクト

    Returns:
        Image.Image: アーティファクトの画像
    """
    base_img = GImage(
        box_size=(32, 32),
        default_font_size=10
    )
    if artifact is None:
        return base_img.get_image()

    # 聖遺物を合成
    base_img.add_image(
        image_path=artifact.util.icon.path,
        box=(0, 0),
        size=(32, 32),
    )
    # メインステータスの画像を合成
    base_img.add_image(
        image_path=ASSETS.icon_namehash[artifact.main_name],
        size=(16, 16),
        box=(16, 16)
    )

    return base_img.get_image()


def __create_artifact_list(artifact_map: dict[ranking_model.Artifact]) -> Image.Image:
    """聖遺物の一覧の画像を生成します。

    Args:
        artifact_list (list[artifact]): アーティファクトオブジェクトの配列

    Returns:
        Image.Image: 聖遺物一覧画像
    """
    img = GImage(
        box_size=(160, 32),
    )

    futures: list[Future] = []
    # 各聖遺物のステータス画像の生成
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_artifact") as pool:
        for i, v in enumerate(['EQUIP_BRACER', 'EQUIP_NECKLACE', 'EQUIP_SHOES', 'EQUIP_RING', 'EQUIP_DRESS']):
            futures.append(
                pool.submit(
                    __create_artifact,
                    artifact_map.get(v)
                )
            )
    # 各ステータス画像の合成
    for i, v in enumerate(futures):
        im: Image = v.result()
        img.paste(im=im, box=(i*32, 0))

    return img.get_image()


def __create_total_socre(artifact_list: dict[str, ranking_model.Artifact], build_type: str) -> Image.Image:
    """聖遺物のトータルスコアの画像を生成します

    Args:
        artifact_list (list[artifact]): 聖遺物の配列
        build_type (str): ビルドのタイプ

    Returns:
        Image.Image: 聖遺物のトータルスコア画像
    """

    img = GImage(
        box_size=(100, 32),
        default_font_size=10,
    )
    # スキルレベルの合成
    img.draw_text(
        text=f"{build_type} スコア合計",
        position=(0, 0),
        anchor=Anchors.LEFT_TOP,
        font_color=Colors.GRAY,
        font_size=10
    )
    
    img.draw_text(
        text=str(round(sum([v.score for v in artifact_list.values()]), 1)),
        position=(16, 16),
        anchor=Anchors.LEFT_TOP,
        font_size=13
    )

    return img.get_image()


def __create_weapon(weapon: ranking_model.Weapon) -> Image.Image:
    """武器画像を生成します

    Args:
        weapon (weapon): weaponオブジェクト

    Returns:
        Image.Image: 武器画像
    """
    totu = [
        "無", "1", "2", "3", "4", "完"
    ]

    img = GImage(
        box_size=(600, 300),
        default_font_size=45,
    )
    # 武器画像を合成
    img.add_image(
        image_path=weapon.util.icon.path,
        size=(30, 30),
        box=(0, 0),
        image_anchor=ImageAnchors.LEFT_TOP
    )
    # 武器ステータスアイコンの合成
    img.add_image(
        image_path=ASSETS.icon_namehash[weapon.sub_name],
        size=(16, 16),
        box=(22, 14),
        image_anchor=ImageAnchors.LEFT_TOP
    )
    # 武器のレベルの合成
    img.draw_text(
        text=f"Lv {weapon.level}\n{totu[weapon.rank]}凸",
        position=(46, 0),
        font_size=12,
        align=Algin.LEFT,
    )
    
    return img.get_image()

def __create_ranking_data(ranking: ranking_model.RankingData) -> Image.Image:
    """ランキングのデータを生成します
    
    Args:
        ranking (ranking_model.RankingData): ランキングデータ
    
    Returns:
        Image.Image: ランキングデータの画像
    """
    ELEMENT_COLOR: dict[str, tuple[int, int, int]] = {
        "Electric": (144, 89, 181),
        "Fire": (209, 89, 73),
        "Grass": (75, 150, 52),
        "Ice": (60, 145, 187),
        "Rock": (167, 120, 26),
        "Water": (53, 89, 166),
        "Wind": (84, 157, 118)
    }
    element_color = ELEMENT_COLOR[ranking.character.util.element]

    # 背景画像の生成
    img = GImage(
        box_size=(720, 140),
        default_font_size=24,
    )

    color_bg = Image.new(
        mode="RGBA",
        color=element_color,
        size=(270, 14)
    )

    img.paste(
        im=color_bg,
        box=(230, 28)
    )

    # 順位の合成
    img.draw_text(
        text=f"{ranking.rank}位",
        position=(36, 70),
        anchor=Anchors.MIDDLE_MIDDLE,
        font_color=Colors.WHITE,
        font_size=24,
    )

    # ユーザー名の合成
    img.draw_text(
        text=ranking.nickname,
        position=(236, 13),
        anchor=Anchors.LEFT_TOP,
        font_color=Colors.WHITE,
        font_size=24,
    )

    # 世界ランク(文字)の合成
    img.draw_text(
        text="世界ランク",
        position=(417, 25),
        anchor=Anchors.LEFT_TOP,
        font_color=Colors.WHITE,
        font_size=10,
    )

    # 世界ランク(数値)の合成
    img.draw_text(
        text=str(ranking.level),
        position=(473, 20),
        anchor=Anchors.LEFT_TOP,
        font_color=Colors.WHITE,
        font_size=15,
    )

    return img.get_image()

def __create_image(ranking: ranking_model.RankingData) -> Image.Image:
    """ランキングデータからユーザーの画像を生成します。

    Args:
        ranking (RankingData): ランキングデータ

    Returns:
        Image.Image: ランキングユーザー画像
    """

    character = ranking.character
    artifacts = character.artifacts
    weapon = character.weapon

    with ThreadPoolExecutor(thread_name_prefix="__create") as pool:
        # 背景画像の取得
        bgf: Future = pool.submit(
            __create_background,
            character.costume,
        )

        # スターとレベル、凸の画像を取得
        lvf: Future = pool.submit(
            __create_lv_and_const, character.level, character.constellations, character.costume)

        # ステータスを取得
        statusf: Future = pool.submit(
            __create_full_status,
            character.added_hp,
            character.added_attack,
            character.added_defense,
            character.elemental_mastery,
            character.critical_rate,
            character.critical_damage,
            character.charge_efficiency,
            character.elemental_jp_name,
            character.elemental_value,
            ASSETS.icon.element[character.elemental_name]
        )

        # 天賦を取得
        skillf: Future = pool.submit(
            __create_skill,
            character.skills
        )

        # 聖遺物画像の取得
        artifactf: Future = pool.submit(
            __create_artifact_list,
            artifacts
        )

        # 聖遺物のトータルスコアを取得
        total_scoref: Future = pool.submit(
            __create_total_socre,
            artifacts,
            character.build_name
        )
        # 武器画像を取得
        weapon_dataf: Future = pool.submit(
            __create_weapon,
            weapon
        )
        # ランキング画像を取得
        ranking_dataf: Future = pool.submit(
            __create_ranking_data,
            ranking
        )

    # 各リザルトを取得
    bg = bgf.result()
    lv = lvf.result()
    status = statusf.result()
    skill = skillf.result()
    artifact = artifactf.result()
    total_score = total_scoref.result()
    weapon_data = weapon_dataf.result()
    ranking_dataf = ranking_dataf.result()

    # ステータスを合成
    bg.paste(im=status, box=(527, 38))
    # レベルなど合成
    bg.paste(im=lv, box=(220, 42))
    # 天賦を合成
    bg.paste(im=skill, box=(421, 54))
    # 聖遺物を合成
    bg.paste(im=artifact, box=(230, 95))
    # 聖遺物のトータルスコアを合成
    bg.paste(im=total_score, box=(421, 95))
    # 武器画像を合成
    bg.paste(im=weapon_data, box=(306, 54))
    # キャラ名を合成
    bg.paste(im=ranking_dataf, box=(0, 0))

    return bg.get_image()


def get_character_image_bytes(ranking_data: ranking_model.RankingData) -> bytes:
    """キャラクターステータスのオブジェクトからDiscord FileとPathを生成します。

    Args:
        ranking_data (ranking_model.RankingData): ランキングデータ

    Returns:
        bytes: Discord FileとPathの入ったTuple型
    """

    image = __create_image(ranking_data)
    image.show()
    fileio = BytesIO()
    image = image.convert("RGB")
    image.save(fileio, format="JPEG", optimize=True, quality=100)
    return fileio.getvalue()


def save_image(file_path: str, ranking_data: ranking_model.RankingData):
    if cache_image.check_cache_exists(file_path=file_path):
        return

    ranking_data.init_utils()

    print(ranking_data)
    image = __create_image(ranking_data)
    image = image.convert("RGBA")
    image.save(file_path, optimize=True, quality=100)
    cache_image.cache_append(file_path=file_path)

import json
def debug_save_image(file_path: str, ranking_data: ranking_model.RankingData):
    with open('ranking_test.json', 'r') as f:
        data = json.load(f)
    
    ranking_data = ranking_model.RankingData(**data)
    ranking_data.init_utils()
    image = __create_image(ranking=ranking_data)
    image = image.convert("RGBA")
    image.save("ranking_images/test.png", optimize=True, quality=100)