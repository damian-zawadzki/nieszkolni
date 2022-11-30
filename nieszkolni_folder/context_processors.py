from nieszkolni_folder.audit_manager import AuditManager


def sections_processor(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        status = AuditManager().check_if_clocked_in(current_user)

        return {"status": status}
