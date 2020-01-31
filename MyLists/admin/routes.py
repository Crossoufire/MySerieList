from flask import Blueprint
from flask_login import login_required


bp = Blueprint('admin', __name__)


@bp.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    pass
