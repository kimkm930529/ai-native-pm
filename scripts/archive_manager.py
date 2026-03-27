#!/usr/bin/env python3
"""
Archive Manager — 오래된 결과물 아카이브 에이전트
오늘 기준 30일 이상 지난 파일을 archive/ 폴더로 이동한다.

사용법:
  python3 scripts/archive_manager.py --dry-run       # 미리보기 (실제 이동 없음)
  python3 scripts/archive_manager.py --run            # 실제 이동 실행
  python3 scripts/archive_manager.py --days 60        # 기준일 변경 (기본: 30일)
  python3 scripts/archive_manager.py --run --target output  # 특정 폴더만 처리
"""

import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# 아카이브 대상 폴더 목록 (루트 기준 상대 경로)
SCAN_DIRS = [
    "output",
    "prd-agent-system/output",
    "figma-agent-system/output",
    "gtm-agent-system/output",
    "pgm-agent-system/output",
    "report-agent-system/output",
    "epic-ticket-system/output",
    "ux-copywriter-system/output",
]

# 아카이브하지 않을 파일/폴더 패턴
EXCLUDE_PATTERNS = {
    ".DS_Store",
    ".gitkeep",
    "logs",        # 로그 폴더는 별도 관리
    "flash",       # weekly flash 폴더
    "weekly",      # weekly 폴더
    "reports",     # reports 하위 폴더
    "artifacts",   # artifacts 폴더
}

# 아카이브하지 않을 확장자
EXCLUDE_EXTENSIONS = {
    ".log",
    ".json",   # 설정/메타 파일
}


def get_archive_path(file_path: Path, archive_root: Path) -> Path:
    """원본 경로 구조를 보존하여 archive 경로 생성"""
    rel = file_path.relative_to(PROJECT_ROOT)
    return archive_root / rel


def scan_files(days: int, target: str = None) -> list[tuple[Path, datetime]]:
    """아카이브 대상 파일 스캔"""
    cutoff = datetime.now() - timedelta(days=days)
    results = []

    scan_dirs = SCAN_DIRS
    if target:
        scan_dirs = [d for d in SCAN_DIRS if target in d]

    for scan_dir in scan_dirs:
        base = PROJECT_ROOT / scan_dir
        if not base.exists():
            continue

        for item in base.iterdir():
            # 폴더는 제외 (하위 폴더 구조는 보존)
            if item.is_dir():
                continue
            # 제외 패턴 확인
            if item.name in EXCLUDE_PATTERNS:
                continue
            # 제외 확장자 확인
            if item.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                results.append((item, mtime))

    return sorted(results, key=lambda x: x[1])


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/1024/1024:.1f}MB"


def run_archive(days: int, dry_run: bool, target: str = None):
    cutoff_date = datetime.now() - timedelta(days=days)
    archive_root = PROJECT_ROOT / "output" / "_archive"

    today_label = datetime.now().strftime("%Y-%m")
    archive_dir = archive_root / today_label

    files = scan_files(days, target)

    if not files:
        print(f"✅ 아카이브 대상 없음 (기준: {days}일 이전 = {cutoff_date.strftime('%Y-%m-%d')} 이전)")
        return

    print(f"📦 아카이브 대상 파일 ({len(files)}개) — 기준: {cutoff_date.strftime('%Y-%m-%d')} 이전")
    print(f"   이동 위치: output/_archive/{today_label}/\n")

    total_size = 0
    for fpath, mtime in files:
        rel = fpath.relative_to(PROJECT_ROOT)
        size = fpath.stat().st_size
        total_size += size
        print(f"  [{mtime.strftime('%Y-%m-%d')}] {rel}  ({format_size(size)})")

    print(f"\n  합계: {len(files)}개 파일, {format_size(total_size)}")

    if dry_run:
        print("\n⚠️  DRY RUN — 실제 이동 없음. --run 옵션으로 실행하세요.")
        return

    # 실제 이동
    print("\n🚀 아카이브 시작...")
    moved = 0
    errors = 0

    for fpath, mtime in files:
        dest = get_archive_path(fpath, archive_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(fpath), str(dest))
            moved += 1
            print(f"  ✓ {fpath.name} → {dest.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            errors += 1
            print(f"  ✗ {fpath.name} — 오류: {e}")

    print(f"\n✅ 완료: {moved}개 이동, {errors}개 오류")
    if errors == 0:
        print(f"📁 아카이브 위치: output/_archive/{today_label}/")


def main():
    parser = argparse.ArgumentParser(description="Archive Manager — 오래된 결과물 정리")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 (이동 없음)")
    parser.add_argument("--run", action="store_true", help="실제 이동 실행")
    parser.add_argument("--days", type=int, default=30, help="기준일 (기본: 30일)")
    parser.add_argument("--target", type=str, help="특정 폴더만 처리 (예: output, prd-agent-system)")
    args = parser.parse_args()

    if not args.dry_run and not args.run:
        # 기본: dry-run
        args.dry_run = True

    run_archive(days=args.days, dry_run=args.dry_run, target=args.target)


if __name__ == "__main__":
    main()
