#!/usr/bin/env python3
"""
Figma REST API Client — figma-agent-system
파일 구조 탐색, 노드 조회, 이미지 내보내기, 텍스트 추출

연동 필요:
  .env에 다음 환경변수 추가:
    FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
  토큰 발급: figma.com/settings → Security → Personal access tokens

사용법:
  python3 client.py --check
  python3 client.py --file {file_key}
  python3 client.py --node {file_key} {node_id}
  python3 client.py --export {file_key} --nodes "{node_id1},{node_id2}" [--format png] [--scale 2]
  python3 client.py --extract-text {file_key} [--node {node_id}]
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def load_env():
    env_path = Path(__file__).parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

load_env()

FIGMA_ACCESS_TOKEN = os.environ.get("FIGMA_ACCESS_TOKEN", "")
FIGMA_BASE_URL = "https://api.figma.com/v1"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "images"


def figma_get(path: str, params: dict = {}) -> dict:
    query = urllib.parse.urlencode(params)
    url = f"{FIGMA_BASE_URL}{path}"
    if query:
        url += f"?{query}"
    req = urllib.request.Request(
        url,
        headers={"X-Figma-Token": FIGMA_ACCESS_TOKEN},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"error": str(e)}


# ─── 연결 확인 ──────────────────────────────────────────────

def check_connection():
    if not FIGMA_ACCESS_TOKEN:
        print(json.dumps({
            "status": "error",
            "message": "FIGMA_ACCESS_TOKEN 미설정",
            "guide": "figma.com/settings → Security → Personal access tokens에서 발급"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = figma_get("/me")
    if "error" in result:
        print(json.dumps({
            "status": "error",
            "message": result["error"],
            "guide": "토큰이 올바른지 확인하세요. figd_ 로 시작해야 합니다."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "user": result.get("handle"),
        "email": result.get("email"),
    }, ensure_ascii=False, indent=2))


# ─── 파일 구조 ──────────────────────────────────────────────

def get_file(file_key: str):
    result = figma_get(f"/files/{file_key}", {"depth": 2})
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2)); sys.exit(1)

    document = result.get("document", {})
    pages = []
    for page in document.get("children", []):
        frames = []
        for child in page.get("children", []):
            if child.get("type") in ("FRAME", "COMPONENT", "COMPONENT_SET"):
                bbox = child.get("absoluteBoundingBox", {})
                frames.append({
                    "id": child.get("id"),
                    "name": child.get("name"),
                    "type": child.get("type"),
                    "width": bbox.get("width"),
                    "height": bbox.get("height"),
                    "children_count": len(child.get("children", [])),
                })
        pages.append({
            "id": page.get("id"),
            "name": page.get("name"),
            "frames": frames,
            "frame_count": len(frames),
        })

    # 컴포넌트 목록
    components = result.get("components", {})
    component_names = [v.get("name", "") for v in components.values()]

    print(json.dumps({
        "file_key": file_key,
        "file_name": result.get("name"),
        "last_modified": result.get("lastModified"),
        "version": result.get("version"),
        "pages": pages,
        "page_count": len(pages),
        "components": {
            "count": len(components),
            "names": sorted(set(component_names))[:50],
        },
    }, ensure_ascii=False, indent=2))


# ─── 특정 노드 ──────────────────────────────────────────────

def get_node(file_key: str, node_id: str):
    encoded_id = urllib.parse.quote(node_id, safe="")
    result = figma_get(f"/files/{file_key}/nodes", {"ids": node_id, "depth": 3})
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2)); sys.exit(1)

    nodes = result.get("nodes", {})
    node_key = node_id.replace(":", "%3A") if ":" in node_id else node_id
    # Figma는 node_id를 키로 반환
    node_data = nodes.get(node_id) or nodes.get(list(nodes.keys())[0]) if nodes else None
    if not node_data:
        print(json.dumps({"error": f"노드 {node_id}를 찾을 수 없습니다."})); sys.exit(1)

    node = node_data.get("document", {})

    def summarize_children(children: list, depth: int = 0) -> list:
        if depth > 2:
            return []
        result = []
        for c in children:
            item = {
                "id": c.get("id"),
                "name": c.get("name"),
                "type": c.get("type"),
            }
            if c.get("children"):
                item["children"] = summarize_children(c["children"], depth + 1)
                item["children_count"] = len(c["children"])
            if c.get("type") == "TEXT":
                item["text"] = c.get("characters", "")
            result.append(item)
        return result

    print(json.dumps({
        "node_id": node_id,
        "name": node.get("name"),
        "type": node.get("type"),
        "children": summarize_children(node.get("children", [])),
        "children_count": len(node.get("children", [])),
    }, ensure_ascii=False, indent=2))


# ─── 이미지 내보내기 ─────────────────────────────────────────

def export_images(file_key: str, node_ids: list[str], fmt: str = "png", scale: int = 2):
    ids_param = ",".join(node_ids)
    result = figma_get(f"/images/{file_key}", {
        "ids": ids_param,
        "format": fmt,
        "scale": str(scale),
    })
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2)); sys.exit(1)

    images = result.get("images", {})
    saved = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for node_id, url in images.items():
        if not url:
            saved.append({"node_id": node_id, "status": "failed"})
            continue
        safe_id = node_id.replace(":", "_").replace("/", "_")
        out_path = OUTPUT_DIR / file_key / f"{safe_id}.{fmt}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, out_path)
            saved.append({"node_id": node_id, "path": str(out_path), "status": "ok"})
        except Exception as e:
            saved.append({"node_id": node_id, "status": "failed", "error": str(e)})

    print(json.dumps({"exported": saved, "count": len(saved)}, ensure_ascii=False, indent=2))


# ─── 텍스트 추출 ────────────────────────────────────────────

def extract_texts(file_key: str, node_id: str = ""):
    params = {"depth": 5}
    if node_id:
        result = figma_get(f"/files/{file_key}/nodes", {"ids": node_id, "depth": 5})
        nodes = result.get("nodes", {})
        root = list(nodes.values())[0].get("document", {}) if nodes else {}
    else:
        result = figma_get(f"/files/{file_key}", params)
        root = result.get("document", {})

    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2)); sys.exit(1)

    texts = []

    def walk(node: dict, page_name: str = "", frame_name: str = ""):
        if node.get("type") == "TEXT" and node.get("characters"):
            texts.append({
                "node_id": node.get("id"),
                "node_name": node.get("name"),
                "content": node.get("characters"),
                "page": page_name,
                "frame": frame_name,
            })
        for child in node.get("children", []):
            child_frame = frame_name
            if child.get("type") == "FRAME":
                child_frame = child.get("name", frame_name)
            walk(child, page_name, child_frame)

    if root.get("type") == "DOCUMENT":
        for page in root.get("children", []):
            for child in page.get("children", []):
                walk(child, page_name=page.get("name", ""), frame_name=child.get("name", ""))
    else:
        walk(root)

    print(json.dumps({
        "texts": texts,
        "count": len(texts),
    }, ensure_ascii=False, indent=2))


# ─── CLI ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Figma REST API Client")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--file", type=str, metavar="FILE_KEY")
    parser.add_argument("--node", type=str, metavar="FILE_KEY")
    parser.add_argument("--export", type=str, metavar="FILE_KEY")
    parser.add_argument("--extract-text", type=str, metavar="FILE_KEY")
    parser.add_argument("--nodes", type=str, help="쉼표 구분 node_id 목록")
    parser.add_argument("--node-id", type=str, help="단일 node_id")
    parser.add_argument("--format", type=str, default="png", choices=["png", "jpg", "svg", "pdf"])
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()

    if args.check:
        check_connection()
    elif args.file:
        get_file(args.file)
    elif args.node:
        if not args.node_id:
            print(json.dumps({"error": "--node-id 필요"})); sys.exit(1)
        get_node(args.node, args.node_id)
    elif args.export:
        if not args.nodes:
            print(json.dumps({"error": "--nodes 필요 (쉼표 구분)"})); sys.exit(1)
        node_ids = [n.strip() for n in args.nodes.split(",")]
        export_images(args.export, node_ids, args.format, args.scale)
    elif args.extract_text:
        extract_texts(args.extract_text, args.node_id or "")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
