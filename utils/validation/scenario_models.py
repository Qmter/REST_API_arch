from typing import Dict
from typing_extensions import Literal

from pydantic import (
    BaseModel,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

# ============================================================
# Expected
# ============================================================

class Expected(BaseModel):
    errCode: int
    httpCode: int

    @field_validator("httpCode")
    @classmethod
    def validate_http_code(cls, v: int) -> int:
        valid_codes = {
            200, 201, 204,
            400, 401, 403, 404, 405,
            500
        }
        if v not in valid_codes:
            raise ValueError(f"Некорректный HTTP код: {v}")
        return v


# ============================================================
# RefValue
# ============================================================

class RefValue(BaseModel):
    ref: str

    @field_validator("ref")
    @classmethod
    def validate_ref(cls, v: str) -> str:
        if not v.startswith("#"):
            raise ValueError("ref должен начинаться с '#'")
        return v
    

# ============================================================
# ModifyValue
# ============================================================

class ModifyValue(BaseModel):
    value: str
    modify: str



ParameterValue = str | int | float | bool | RefValue | ModifyValue | dict


# ============================================================
# Step
# ============================================================

class Step(BaseModel):
    endpoint: str
    method: Literal[
        "GET", "POST", "PUT", "PATCH",
        "DELETE", "HEAD", "OPTIONS"
    ]

    parameters: Dict[str, ParameterValue] | None = None
    validation: Dict[str, ParameterValue] | None = None
    expected: Expected | None = None

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("endpoint должен начинаться с '/'")
        return v

    @model_validator(mode="after")
    def validate_post_rules(self):
        if self.method == "POST" and not self.parameters:
            raise ValueError(
                "POST метод должен содержать непустые parameters"
            )
        return self


# ============================================================
# TestCase
# ============================================================

class TestCase(BaseModel):
    description: str
    steps: Dict[str, Step]

    @field_validator("steps")
    @classmethod
    def validate_steps_keys(cls, v: Dict[str, Step]):
        for step_id in v:
            if not step_id.isdigit():
                raise ValueError(
                    f"ID шага должен быть числом в виде строки, получено: {step_id}"
                )
        return v


# ============================================================
# AFTER-TEST
# ============================================================

class AfterTest(BaseModel):
    steps: Dict[str, Step]


# ============================================================
# EndpointScenario
# ============================================================

class EndpointScenario(BaseModel):
    TESTS: Dict[str, TestCase]
    AFTER_TEST: AfterTest | None = Field(
        None,
        alias="AFTER-TEST"
    )

    @field_validator("TESTS")
    @classmethod
    def validate_test_ids(cls, v: Dict[str, TestCase]):
        for test_id in v:
            if not test_id.isdigit():
                raise ValueError(
                    f"ID теста должен быть числом в виде строки, получено: {test_id}"
                )
        return v


# ============================================================
# Scenario (ROOT MODEL)
# ============================================================

class Scenario(RootModel[Dict[str, EndpointScenario]]):

    @field_validator("root")
    @classmethod
    def validate_endpoint_keys(cls, v: Dict[str, EndpointScenario]):
        for endpoint in v:
            if not endpoint.startswith("/"):
                raise ValueError(
                    f"Endpoint '{endpoint}' должен начинаться с '/'"
                )
        return v


