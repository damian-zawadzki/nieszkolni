from nieszkolni_folder.audit_manager import AuditManager
from nieszkolni_folder.challenge_manager import ChallengeManager
from nieszkolni_folder.roadmap_manager import RoadmapManager
from nieszkolni_folder.stream_manager import StreamManager


def sections_processor(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        current_user = first_name + " " + last_name

        if request.user.is_superuser:
            superuser_status = True
        else:
            superuser_status = False

        status = AuditManager().check_if_clocked_in(current_user)

        challenges = ChallengeManager().display_planned_challenges(current_user)
        challenge_status = ChallengeManager().refresh_process(challenges)

        try:
            avatar = RoadmapManager().display_profile(current_user)[2]
        except Exception as e:
            avatar = ""

        quaterly_points = StreamManager().display_activity(current_user)
        target = StreamManager().display_activity_target(current_user)

        return {
            "current_user": current_user,
            "status": status,
            "superuser_status": superuser_status,
            "challenge_status": challenge_status,
            "avatar": avatar,
            "quaterly_points": quaterly_points,
            "target": target
            }

    else:
        return {}
