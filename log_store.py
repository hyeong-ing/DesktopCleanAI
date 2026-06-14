import json
from datetime import datetime

from scanner import get_desktop_path
from config import APP_FOLDER_NAME


LOG_VERSION = 1


def get_log_path():
    """
    move-log.json 파일 경로를 가져오는 함수
    """
    return get_desktop_path() / APP_FOLDER_NAME / "move-log.json"


def create_empty_log():
    """
    move-log.json 기본 구조를 만드는 함수
    """
    return {
        "version": LOG_VERSION,
        "undoStack": [],
        "redoStack": [],
    }


def load_log():
    """
    기존 move-log.json을 읽는 함수

    파일이 없으면 새 로그 구조를 반환한다.
    """
    log_path = get_log_path()

    if not log_path.exists():
        return create_empty_log()

    with open(log_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_log(log_data):
    """
    move-log.json을 저장하는 함수
    """
    log_path = get_log_path()

    # .deskpilot 폴더가 없으면 만든다.
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "w", encoding="utf-8") as file:
        json.dump(log_data, file, ensure_ascii=False, indent=2)


def create_session_id():
    """
    정리 세션 ID를 만드는 함수

    예:
    20260614-013000
    """
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save_move_session(results):
    """
    실제 이동 성공 결과를 move-log.json에 저장하는 함수

    SUCCESS 상태인 이동만 저장한다.
    """
    successful_moves = []

    for result in results:
        if result.get("status") != "SUCCESS":
            continue

        successful_moves.append(
            {
                "filename": result.get("filename"),
                "originalPath": result.get("originalPath"),
                "movedPath": result.get("targetPath"),
                "source": result.get("source"),
                "status": result.get("status"),
            }
        )

    # 성공한 이동이 없으면 로그를 저장하지 않는다.
    if not successful_moves:
        return None

    log_data = load_log()

    session = {
        "sessionId": create_session_id(),
        "executedAt": datetime.now().isoformat(timespec="seconds"),
        "basePath": str(get_desktop_path()),
        "moves": successful_moves,
    }

    log_data["undoStack"].append(session)

    # 되돌리기 후 새 이동을 하면 redoStack은 초기화하는 게 일반적이다.
    log_data["redoStack"] = []

    save_log(log_data)

    return session
