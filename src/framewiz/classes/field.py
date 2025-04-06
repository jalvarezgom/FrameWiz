import numbers
from typing import Hashable, Iterable, Any

from pandas import DataFrame, Series

from src.framewiz.classes.enums import FrameBuilderDirectionEnum

Column = DataFrame
Row = Iterable[tuple[Hashable, Series]]
TFieldBuilder = list['FieldBuilder']

class FieldBuilder:
    column_name: str = None
    field_type: object = None
    field_dependencies: TFieldBuilder = []

    @classmethod
    def add_dependencies(cls, dependencies: TFieldBuilder) -> TFieldBuilder:
        if not cls in dependencies:
            for field_dependency in cls.field_dependencies:
                field_dependency.add_dependencies(dependencies)
            dependencies.append(cls)
        return dependencies

    @classmethod
    def evaluate(cls, direction: FrameBuilderDirectionEnum, *args, **kwargs) -> Column | Row:
        match direction:
            case FrameBuilderDirectionEnum.ROW:
                return cls._evaluate_row(*args, **kwargs)
            case FrameBuilderDirectionEnum.COLUMN:
                return cls._evaluate_column(*args, **kwargs)
            case _:
                raise ValueError(f'Unsupported direction: {direction}')

    @classmethod
    def _evaluate_column(cls, df: DataFrame, **xtra_args) -> Column:
        formula_value = cls.formula_column(df, **xtra_args)
        if xtra_args['rounding_value'] and isinstance(formula_value, numbers.Number):
            formula_value = round(formula_value, xtra_args['rounding_value'])
        df[cls.column_name] = formula_value
        return formula_value

    @classmethod
    def _evaluate_row(cls, previous_row: Row, row: Row, **xtra_args) -> Row:
        formula_value = cls.formula_row(previous_row, row, **xtra_args)
        if xtra_args['rounding_value'] and isinstance(formula_value, numbers.Number):
            formula_value = round(formula_value, xtra_args['rounding_value'])
        row[cls.column_name] = formula_value
        return formula_value

    @classmethod
    def formula_column(cls, df: DataFrame, **xtra_args) -> Any:
        raise NotImplementedError('formula_column must be implemented in the subfield')

    @classmethod
    def formula_row(cls, previous_row: Row, row: Row, **xtra_args) -> Any:
        raise NotImplementedError('formula_row must be implemented in the subfield')
