from flask import Blueprint, request
from werkzeug.exceptions import BadRequest
import dateutil.parser

from src.models.hacker import Hacker
from src import db

hackers_blueprint = Blueprint("hackers", __name__)

@hackers_blueprint.route("/", methods=["POST"])
def create_hacker():
    """
    Creates a new Hacker.
    ---
    tags:
        - hacker
    summary: Create Hacker
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/Hacker'
        description: Created Hacker Object
        required: true
    responses:
        201:
            description: OK
        400:
            description: Bad request.
        5XX:
            description: Unexpected error.
    """
    data = request.get_json()

    if not data:
        raise BadRequest()

    if d := data["date"]:
        data["date"] = dateutil.parser.parse(d)

    hacker = Hacker.createOne(**data, permissions=("HACKER",))

    res = {
        "status": "success",
        "message": "Hacker was created!"
    }

    return res, 201

