from scanner import scan_desktop_files, scan_destination_folders
from rules import read_rules
from classifier import get_folder_names, classify_by_tag, classify_by_rules
from config import ARCHIVE_FOLDER_NAME



def create_plan_for_file(file_path, destination_folder_names, rules):
    """
    파일 하나에 대한 정리 계획을 만드는 함수

    우선순위:
    1. 파일명 앞 [태그] 기준 분류
    2. rules.txt 키워드 기준 분류
    3. archive 폴더가 있으면 archive 추천
    4. archive 폴더도 없으면 Desktop에 남기기
    """

    # 1순위: 파일명 태그 기반 분류
    result = classify_by_tag(file_path, destination_folder_names)

    if result is not None:
        result["action"] = "MOVE"
        result["confidence"] = 1.0
        return result

    # 2순위: rules.txt 기반 분류
    result = classify_by_rules(file_path, rules, destination_folder_names)

    if result is not None:
        result["action"] = "MOVE"
        result["confidence"] = 0.8
        return result

    # 3순위: 분류 실패 시 archive 폴더로 추천
    if ARCHIVE_FOLDER_NAME in destination_folder_names:
        return {
            "filename": file_path.name,
            "targetFolder": ARCHIVE_FOLDER_NAME,
            "reason": "태그와 rules.txt로 분류되지 않아 archive 폴더로 추천합니다.",
            "source": "FALLBACK_ARCHIVE",
            "action": "MOVE",
            "confidence": 0.3,
        }

    # 4순위: archive 폴더도 없으면 Desktop에 남기기
    return {
        "filename": file_path.name,
        "targetFolder": None,
        "reason": "분류되지 않았고 archive 폴더가 없어 Desktop에 남깁니다.",
        "source": "UNCLASSIFIED",
        "action": "KEEP",
        "confidence": 0.0,
    }


def build_move_plan():
    """
    test_desktop 안의 모든 파일에 대한 정리 계획을 만드는 함수
    """
    desktop_files = scan_desktop_files()
    destination_folders = scan_destination_folders()

    destination_folder_names = get_folder_names(destination_folders)
    rules = read_rules()

    plan = []

    for file_path in desktop_files:
        file_plan = create_plan_for_file(
            file_path,
            destination_folder_names,
            rules,
        )

        plan.append(file_plan)

    return plan


def print_move_plan(plan):
    """
    정리 계획을 터미널에 보기 좋게 출력하는 함수
    """
    print("정리 미리보기")
    print("------------")

    if not plan:
        print("정리할 파일이 없습니다.")
        return

    for item in plan:
        filename = item["filename"]
        action = item["action"]
        target_folder = item["targetFolder"]
        source = item["source"]
        reason = item["reason"]
        confidence = item["confidence"]

        if action == "MOVE":
            print(
                f"[이동 예정] {filename} -> {target_folder} "
                f"/ 출처: {source} "
                f"/ 확신도: {confidence} "
                f"/ 이유: {reason}"
            )
        else:
            print(
                f"[남기기] {filename} "
                f"/ 출처: {source} "
                f"/ 확신도: {confidence} "
                f"/ 이유: {reason}"
            )


if __name__ == "__main__":
    move_plan = build_move_plan()
    print_move_plan(move_plan)
