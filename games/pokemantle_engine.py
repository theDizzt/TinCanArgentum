import csv
import random
from functools import lru_cache
from pathlib import Path
from random import Random

import numpy as np

from games.poke2vec import calculate_similarity_vector
from project_paths import DATA_DIR, PROJECT_ROOT


def _read_csv(path: Path) -> list[dict[str, str | None]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {key: (value if value != "" else None) for key, value in row.items()}
            for row in csv.DictReader(file)
        ]


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
            "민혁": "Kyurem",
        }

        self.random = Random(seed)
        self.pokedex = _read_csv(data_path / "pokedex.csv")
        name_map = _read_csv(data_path / "name_map.csv")
        old_secret = _read_csv(data_path / "old_secret.csv")

        self.pokemon_size = len(self.pokedex)
        self.old_secret_size = len(old_secret)
        self.names = tuple(str(row["name"]) for row in self.pokedex)
        self._name_indexes = {
            name.strip().lower(): index for index, name in enumerate(self.names)
        }
        self._old_secret_names = {
            int(str(row["puzzle_number"])): str(row["name"])
            for row in old_secret
        }
        self.en_to_ko = {
            str(row["en"]).strip().lower(): str(row["ko"])
            for row in name_map
            if row.get("en") and row.get("ko")
        }
        self.ko_to_en = {
            str(row["ko"]).strip().lower(): str(row["en"])
            for row in name_map
            if row.get("en") and row.get("ko")
        }
        self.secret_indexes = self.random.sample(
            range(self.pokemon_size),
            k=self.pokemon_size,
        )

        print("[POKEMANTLE] similarity 계산 중...")
        self.similarity_vector = calculate_similarity_vector(self.pokedex)
        print("[POKEMANTLE] 완료")

    def get_random_answer_index(self):
        return random.randint(0, self.pokemon_size - 1)

    def name_at(self, index: int) -> str:
        return self.names[index]

    def normalize_name(self, name: str) -> str:
        key = name.strip().lower()
        return self.alias_map.get(key, self.ko_to_en.get(key, name.strip()))

    def is_alias_input(self, name: str) -> bool:
        return name.strip().lower() in self.alias_map

    def get_secret_index(self, puzzle_number: int) -> int:
        if puzzle_number <= self.old_secret_size:
            name = self._old_secret_names[puzzle_number]
            return self._name_indexes[name.strip().lower()]
        return self.secret_indexes[puzzle_number % self.pokemon_size]

    @lru_cache(maxsize=4)
    def _rank_data(self, answer_index: int) -> tuple[np.ndarray, np.ndarray]:
        similarities = self.similarity_vector[answer_index]
        order = similarities.argsort()[::-1]
        ranks = np.empty(self.pokemon_size, dtype=np.int32)
        ranks[order] = np.arange(self.pokemon_size, dtype=np.int32)
        return order, ranks

    def guess_by_index(self, answer_index: int, name: str):
        normalized = self.normalize_name(name).lower()
        guessed_index = self._name_indexes.get(normalized)
        if guessed_index is None:
            return None

        _, ranks = self._rank_data(answer_index)
        rank = int(ranks[guessed_index])
        return {
            "name": self.names[guessed_index],
            "rank": rank,
            "similarity": float(self.similarity_vector[answer_index, guessed_index]),
            "is_correct": rank == 0,
        }

    def get_all_ranks_by_index(self, answer_index: int):
        order, _ = self._rank_data(answer_index)
        similarities = self.similarity_vector[answer_index]
        return [
            {
                "name": self.names[index],
                "rank": rank,
                "similarity": float(similarities[index]),
            }
            for rank, index in enumerate(order)
        ]
