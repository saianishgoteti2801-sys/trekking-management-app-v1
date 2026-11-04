from functools import wraps
from flask import (flash,redirect,url_for,)
from flask_login import (current_user,login_required,)
from database.enums import UserRole
def admin_required(view_function):
    @wraps(view_function)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != UserRole.ADMIN.value:
            flash("Administrator access is required.","danger",)
            return redirect(url_for("auth.login"))
        return view_function(*args,**kwargs,)
    return wrapped
def staff_required(view_function):
    @wraps(view_function)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != UserRole.STAFF.value:
            flash("Staff account required.","danger",)
            return redirect(url_for("auth.login"))
        if not current_user.is_active:
            flash("Staff account is awaiting approval.","warning",)
            return redirect(url_for("auth.login"))
        return view_function(*args,**kwargs,)
    return wrapped
def trekker_required(view_function):
    @wraps(view_function)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != UserRole.TREKKER.value:
            flash("Trekker account required.","danger",)
            return redirect(url_for("auth.login"))
        return view_function(*args,**kwargs,)
    return wrapped