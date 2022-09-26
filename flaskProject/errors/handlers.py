from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template("errors/errorbase.html", error_name = 404, error_problem = """هذه الصفحة غير موجودة"""), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template("errors/errorbase.html", error_name = 403, error_problem = """غير مسموح لك بالدخول لهذه الصفحة"""), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template("errors/errorbase.html", error_name = 500, error_problem = """يوجد خطأ برجاء التوجه لمؤسس الموقع"""), 500

