from pathlib import Path
from typing import Union


def resolve_model_name(model_path: Union[str, Path]):
    if not model_path:
        return None
    model_path = Path(model_path)
    return model_path.name


def resolve_excel_path(model_path: Union[str, Path]):
    if not model_path:
        return None
    model_path = Path(model_path)
    return model_path.joinpath(resolve_model_name(model_path) + ".xlsx")


def resolve_json_path(model_path: Union[str, Path]):
    if not model_path:
        return None
    model_path = Path(model_path)
    return model_path.joinpath("simulation_data.json")


def resolve_result_path(model_path: Union[str, Path]):
    if not model_path:
        return None
    model_path = Path(model_path)
    return model_path.joinpath("result.json")


def sim_data_dir(sim_id: str, data_dir: Path):
    if not sim_id:
        return data_dir
    return data_dir.joinpath(sim_id)
