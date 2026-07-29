"""Pokemantle similarity calculations without pandas or scikit-learn.

The original implementation loaded two large data-analysis frameworks for a
roughly 1,000-row CSV.  NumPy is sufficient for the actual matrix operations
and keeps the bot's resident memory substantially smaller.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


UNUSED_COLUMNS = {
    "pokedex_number",
    "name",
    "image_path",
    "catch_rate",
    "base_friendship",
    "base_experience",
    "percentage_male",
    "egg_cycles",
}
CATEGORICAL_COLUMNS = {
    "generation",
    "status",
    "species",
    "type_1",
    "type_2",
    "ability_1",
    "ability_2",
    "ability_hidden",
    "growth_rate",
    "egg_type_1",
    "egg_type_2",
}
NUMERIC_COLUMNS = {
    "type_number",
    "height_m",
    "weight_kg",
    "abilities_number",
    "total_points",
    "hp",
    "attack",
    "defense",
    "sp_attack",
    "sp_defense",
    "speed",
    "egg_type_number",
    "against_normal",
    "against_fire",
    "against_water",
    "against_electric",
    "against_grass",
    "against_ice",
    "against_fight",
    "against_poison",
    "against_ground",
    "against_flying",
    "against_psychic",
    "against_bug",
    "against_rock",
    "against_ghost",
    "against_dragon",
    "against_dark",
    "against_steel",
    "against_fairy",
}


@dataclass(frozen=True, slots=True)
class GuessResult:
    name: str
    rank: int
    similarity: float


def _number(value: object) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def _one_hot(
    rows: Sequence[Mapping[str, object]],
    columns: Sequence[str],
    *,
    shared_only: bool = False,
) -> np.ndarray:
    category_sets = [
        {row.get(column) for row in rows if row.get(column) not in (None, "")}
        for column in columns
    ]
    if shared_only:
        categories = set.intersection(*category_sets)
    else:
        categories = set.union(*category_sets)
    ordered = sorted(categories, key=str)
    result = np.zeros((len(rows), len(ordered)), dtype=np.float64)
    indexes = {category: index for index, category in enumerate(ordered)}
    for row_index, row in enumerate(rows):
        for column in columns:
            category = row.get(column)
            category_index = indexes.get(category)
            if category_index is not None:
                result[row_index, category_index] += 1.0
    return result


def _max_normalize(feature_vector: np.ndarray, axis: int) -> np.ndarray:
    maximum = np.max(np.abs(feature_vector), axis=axis, keepdims=True)
    return np.divide(
        feature_vector,
        maximum,
        out=np.zeros_like(feature_vector),
        where=maximum != 0,
    )


def calculate_similarity_vector(
    pokedex: Sequence[Mapping[str, object]],
) -> np.ndarray:
    if not pokedex:
        return np.empty((0, 0), dtype=np.float64)

    remaining_columns = [
        column
        for column in pokedex[0]
        if column not in UNUSED_COLUMNS and column not in CATEGORICAL_COLUMNS
    ]
    cosine_columns = [
        column for column in remaining_columns if column not in NUMERIC_COLUMNS
    ]

    base_cosine = np.asarray(
        [[_number(row.get(column)) for column in cosine_columns] for row in pokedex],
        dtype=np.float64,
    )
    base_euclidean = np.asarray(
        [[_number(row.get(column)) for column in remaining_columns] for row in pokedex],
        dtype=np.float64,
    )

    # shared_only preserves the column-alignment behaviour of the former
    # DataFrame.add() calls, including categories absent from one source column.
    categorical = [
        _one_hot(pokedex, ("generation",)),
        _one_hot(pokedex, ("status",)),
        _one_hot(pokedex, ("species",)),
        _one_hot(pokedex, ("type_1", "type_2"), shared_only=True),
        _one_hot(
            pokedex,
            ("ability_1", "ability_2", "ability_hidden"),
            shared_only=True,
        ),
        _one_hot(pokedex, ("growth_rate",)),
        _one_hot(pokedex, ("egg_type_1", "egg_type_2"), shared_only=True),
    ]
    cosine_features = np.concatenate([base_cosine, *categorical], axis=1)
    euclidean_features = _max_normalize(base_euclidean, axis=0)

    cosine = calculate_cosine_similarity_vector(cosine_features)
    euclidean = calculate_euclidean_similarity_vector(euclidean_features)
    return ((cosine * 2.0) + euclidean) / 3.0


def calculate_cosine_similarity_vector(feature_vector: np.ndarray) -> np.ndarray:
    normalized = np.linalg.norm(feature_vector, axis=1, keepdims=True)
    unit = np.divide(
        feature_vector,
        normalized,
        out=np.zeros_like(feature_vector),
        where=normalized != 0,
    )
    return unit @ unit.T


def calculate_euclidean_similarity_vector(
    feature_vector: np.ndarray,
) -> np.ndarray:
    squared = np.sum(feature_vector * feature_vector, axis=1)
    distances_squared = (
        squared[:, None] + squared[None, :] - (2.0 * feature_vector @ feature_vector.T)
    )
    np.maximum(distances_squared, 0.0, out=distances_squared)
    distances = np.sqrt(distances_squared, out=distances_squared)
    return np.ones_like(distances) - _max_normalize(distances, axis=1)


def calculate_ranks(
    pokemon_index: int,
    pokedex: Sequence[Mapping[str, object]],
    similarity_vector: np.ndarray,
) -> list[GuessResult]:
    similarities = similarity_vector[pokemon_index]
    rank_indexes = similarities.argsort()[::-1]
    return [
        GuessResult(
            name=str(pokedex[index]["name"]),
            rank=rank,
            similarity=float(similarities[index]),
        )
        for rank, index in enumerate(rank_indexes)
    ]
