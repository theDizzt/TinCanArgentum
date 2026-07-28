import pandas as pd
import numpy as np
from pathlib import Path
from random import Random
from project_paths import DATA_DIR, PROJECT_ROOT
import random
from games.poke2vec import calculate_similarity_vector, calculate_ranks

class PokemantleEngine:
    def __init__(self, data_dir=DATA_DIR, seed=20260419):
        data_path = Path(data_dir)
        if not data_path.is_absolute():
            data_path = PROJECT_ROOT / data_path
        self.alias_map = {
            "은비": "Rayquaza",
            "최은비": "Rayquaza",
            "한비": "Darkrai",
            "최한비": "Darkrai",
            "연비": "Celesteela",
            "첨성대": "Stakataka",
            "호우": "Cinderace",
            "코젤": "Corviknight",
            "오보청": "Masquerain",
            "그림버켄": "Tyranitar",
            "코로나": "	Crobat",
            "로즈마리": "Roserade",
            "루리": "Azumarill",
            "화랑": "Volcarona",
            "백설기": "Frosmoth",
            "도희": "Groudon",
            "수향": "Kyogre",
            "별이": "Jirachi",
            "우드해머": "Torterra",
            "와공이": "Salamence",
            "샬롯": "Chandelure",
            "스텔라": "Magnezone",
            "케인인님": "Probopass",
            "오트밀": "Samurott",
            "쿵야": "Excadrill",
            "극한": "Scolipede",
            "알파": "Diancie",
            "벡터": "Absol",
            "미분": "Charizard",
            "와": "Vanilluxe",
            "연두": "Meowscarada",
            "한조": "Decidueye",
            "쿠키": "Incineroar",
            "김종국": "Incineroar",
            "반지": "Primarina",
            "후르츠링": "Toucannon",
            "무우": "Meganium",
            "라코스테": "Feraligatr",
            "브와": "Heracross",
            "와디나르마": "Armarouge",
            "말차": "Sinistcha",
            "빠가츄": "Pawmot",
            "광안대교": "Archaludon",
            "타바스코": "Scovillain",
            "짱돌": "Glimmora",
            "해돌이": "Palafin",
            "볼케이노": "Blaziken",
            "지코바": "Talonflame",
            "비비빅": "Vivillon",
            "주웡": "Empoleon",
            "쭹": "Piplup",
            "길고양이": "Galvantula",
            "빈": "Ariados",
            "빛나리": "Ampharos",
            "당근": "Sceptile",
            "지진": "Swampert",
            "와섯모": "Breloom",
            "니오우": "Wailord",
            "귄어근릎": "Flygon",
            "원시한카리아스": "Armaldo",
            "LCT": "Metagross",
            "엘시티": "Metagross",
            "레지두둥실": "Drifblim",
            "비버니코인": "Bidoof",
            "비버통코인": "Bibarel",
            "박다정": "Reshiram",
            "박준혁": "Zekrom",
            "박민혁": "Kyurem",
            "다정": "Reshiram",
            "준혁": "Zekrom",
            "민혁": "Kyurem"
        }
        
        self.random = Random(seed)

        self.pokedex = pd.read_csv(data_path / "pokedex.csv").replace({np.nan: None})
        self.name_map = pd.read_csv(data_path / "name_map.csv")
        self.old_secret = pd.read_csv(
            data_path / "old_secret.csv",
            index_col="puzzle_number",
        )

        self.pokemon_size = len(self.pokedex.index)
        self.old_secret_size = len(self.old_secret.index)

        self.en_to_ko = {
            row["en"].strip().lower(): row["ko"]
            for _, row in self.name_map.iterrows()
            if isinstance(row["en"], str) and isinstance(row["ko"], str)
        }

        self.secret_indexes = self.random.sample(range(self.pokemon_size), k=self.pokemon_size)

        print("[POKEMANTLE] similarity 계산 중...")
        self.similarity_vector = calculate_similarity_vector(self.pokedex)
        print("[POKEMANTLE] 완료")

        # KR → US 이름 매핑
        self.ko_to_en = {
            row["ko"].strip().lower(): row["en"]
            for _, row in self.name_map.iterrows()
            if isinstance(row["ko"], str)
        }
    
    def get_random_answer_index(self):
        return random.randint(0, self.pokemon_size - 1)

    def normalize_name(self, name: str) -> str:
        key = name.strip().lower()

        # 이스터에그 별칭 먼저 처리
        if key in self.alias_map:
            return self.alias_map[key]

        # 일반 한국어 이름 매핑
        return self.ko_to_en.get(key, name.strip())
    
    # 별명 사용 여부
    def is_alias_input(self, name: str) -> bool:
        key = name.strip().lower()
        return key in self.alias_map

    def get_secret_index(self, puzzle_number: int) -> int:
        if puzzle_number <= self.old_secret_size:
            name = self.old_secret.loc[puzzle_number]["name"]
            return self.pokedex.index[self.pokedex["name"] == name].tolist()[0]
        return self.secret_indexes[puzzle_number % self.pokemon_size]

    def guess_by_index(self, answer_index: int, name: str):
        name = self.normalize_name(name)

        ranks = calculate_ranks(
            pokemon_index=answer_index,
            pokedex=self.pokedex,
            similarity_vector=self.similarity_vector,
        )

        for result in ranks:
            if result.name.lower() == name.lower():
                return {
                    "name": result.name,
                    "rank": result.rank,
                    "similarity": float(result.similarity),
                    "is_correct": result.rank == 0,
                }

        return None

    def get_all_ranks_by_index(self, answer_index: int):
        ranks = calculate_ranks(
            pokemon_index=answer_index,
            pokedex=self.pokedex,
            similarity_vector=self.similarity_vector,
        )

        return [
            {
                "name": r.name,
                "rank": r.rank,
                "similarity": float(r.similarity),
            }
            for r in ranks
        ]
