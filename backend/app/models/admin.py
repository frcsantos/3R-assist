from typing import Any

from pydantic import BaseModel, Field


class AdminTablesResponse(BaseModel):
    tables: list[str]


class AdminSettingsResponse(BaseModel):
    app_env: str
    llm_model: str


class AdminForeignKeyRef(BaseModel):
    table: str
    column: str


class AdminColumnOption(BaseModel):
    value: Any
    label: str


class AdminTableDataResponse(BaseModel):
    table: str
    columns: list[str]
    column_comments: dict[str, str | None] = Field(default_factory=dict)
    column_types: dict[str, str] = Field(default_factory=dict)
    required_columns: list[str] = Field(default_factory=list)
    auto_columns: list[str] = Field(default_factory=list)
    foreign_keys: dict[str, AdminForeignKeyRef] = Field(default_factory=dict)
    column_options: dict[str, list[AdminColumnOption]] = Field(default_factory=dict)
    primary_key: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]]
    total: int
    limit: int
    offset: int = 0
    sort_by: str | None = None
    sort_dir: str | None = None


class AdminTableQuery(BaseModel):
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    sort_by: str | None = Field(default=None, min_length=1, max_length=63)
    sort_dir: str = Field(default="asc")


class AdminCellUpdateRequest(BaseModel):
    primary_key: dict[str, Any]
    column: str
    value: Any = None


class AdminCellUpdateResponse(BaseModel):
    table: str
    column: str
    value: Any
    row: dict[str, Any]


class AdminRowsDeleteRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=100)


class AdminRowsDeleteResponse(BaseModel):
    table: str
    deleted: int


class AdminColumnCommentUpdateRequest(BaseModel):
    comment: str | None = None


class AdminColumnCommentUpdateResponse(BaseModel):
    table: str
    column: str
    comment: str | None = None


class AdminRowInsertRequest(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)


class AdminRowInsertResponse(BaseModel):
    table: str
    row: dict[str, Any]
