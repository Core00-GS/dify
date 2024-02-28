from typing import Tuple


class OpeningStatementValidator:
    @classmethod
    def validate_and_set_defaults(cls, config: dict) -> Tuple[dict, list[str]]:
        """
        Validate and set defaults for opening statement feature

        :param config: app model config args
        """
        if not config.get("opening_statement"):
            config["opening_statement"] = ""

        if not isinstance(config["opening_statement"], str):
            raise ValueError("opening_statement must be of string type")

        # suggested_questions
        if not config.get("suggested_questions"):
            config["suggested_questions"] = []

        if not isinstance(config["suggested_questions"], list):
            raise ValueError("suggested_questions must be of list type")

        for question in config["suggested_questions"]:
            if not isinstance(question, str):
                raise ValueError("Elements in suggested_questions list must be of string type")

        return config, ["opening_statement", "suggested_questions"]
