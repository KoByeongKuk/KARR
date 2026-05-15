#!/usr/bin/env python3
# version: pack_apply_v7
"""?�뇌???�플�??�을 ?�용???�로?�트????번에 ?�용.

?�름:
  1. KIT_NAME ???�뇌??40_?�플�?developer/<KIT_NAME>/ ?�더
  2. PROJECT_PATH ???�용???�용???�로?�트 (비우�?web_init 결과 ?�동)
  3. manifest.json ??apply.{copy_to, post_install, app_imports, app_body} ?�용:
     - files/* ??PROJECT_PATH/copy_to/ (?? src/components/)
     - post_install: npm install / npx expo install ?�동 ?�행
     - app_imports: App.tsx ?�는 App.tsx ??import 추�? + JSX 본문 ?�동
  4. 결과 출력 ???�음 ?�계 ?�내 (npm run dev ??

???�구가 코다리에�?주는 ?�퍼?�워:
  - 매뉴??cp + npm install ?�출 ???�도 ??
  - ??명령?�로 "?�트 ?�용 ?�료"
  - ?�존???�락 ?�음 (manifest 가 진실 ?�스)
"""
import os, sys, json, subprocess, shutil


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "pack_apply.json")
WEB_INIT_CFG = os.path.join(HERE, "web_init.json")


def _log(msg, kind="info"):
    prefix = {"info": "?��", "ok": "??, "warn": "?�️ ", "err": "??, "step": "??}.get(kind, "??)
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def _load(p):
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _run(cmd, cwd):
    _log(f"$ {cmd}", "step")
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        for line in (r.stderr or "").splitlines()[-8:]:
            _log(line, "warn")
        return False
    return True


def _load_operator_credentials(brain_root):
    """v7: ?�영??1??기업)???�격증명???�뇌?�서 로드. pack_apply 가 ?�트 HTML/JS
       ??placeholder �??�영???�로 ?�동 교체.
       지??placeholder:
         __GEMINI_API_KEY__         ??Gemini API ??
         __GEMINI_TEXT_MODEL__      ???�스??모델�?
         __GEMINI_IMAGE_MODEL__     ???��?지 모델�?
         __PAYPAL_CLIENT_ID__       ??PayPal Live/Sandbox Client ID
       ?�격증명?� ?��? ?�결 ?�널 (KoByeongKuk AI Lab) ?�서 ?�력. ?�트 ?�용??고객) ??
       ???��? �??�이 ?�음 ???�영?��? 빌드 ?�점??박힘. """
    creds = {
        "__GEMINI_API_KEY__": "",
        "__GEMINI_TEXT_MODEL__": "gemini-3.1-flash-lite-preview",
        "__GEMINI_IMAGE_MODEL__": "gemini-3.1-flash-image-preview",
        "__PAYPAL_CLIENT_ID__": "",
    }
    business_tools = os.path.join(brain_root, "_company", "_agents", "business", "tools")
    # Gemini
    try:
        gp = os.path.join(business_tools, "gemini_account.json")
        if os.path.exists(gp):
            with open(gp, "r", encoding="utf-8") as f:
                g = json.load(f)
            if g.get("API_KEY"): creds["__GEMINI_API_KEY__"] = g["API_KEY"]
            if g.get("TEXT_MODEL"): creds["__GEMINI_TEXT_MODEL__"] = g["TEXT_MODEL"]
            if g.get("IMAGE_MODEL"): creds["__GEMINI_IMAGE_MODEL__"] = g["IMAGE_MODEL"]
    except Exception:
        pass
    # PayPal
    try:
        pp = os.path.join(business_tools, "paypal_revenue.json")
        if os.path.exists(pp):
            with open(pp, "r", encoding="utf-8") as f:
                p = json.load(f)
            if p.get("CLIENT_ID"): creds["__PAYPAL_CLIENT_ID__"] = p["CLIENT_ID"]
    except Exception:
        pass
    return creds


def _inject_credentials(file_path, creds):
    """v7: ?�스???�일 ?�의 placeholder �??�영???�격증명?�로 교체.
       바이?�리·?��?지 ?�일?� skip. UTF-8 �??�으�?skip. """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, IsADirectoryError):
        return False
    except Exception:
        return False
    replaced = False
    for placeholder, value in creds.items():
        if placeholder in content and value:
            content = content.replace(placeholder, value)
            replaced = True
    if replaced:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False
    return False


def _copy_tree(src_dir, dst_dir, creds=None):
    """v2: 기존 ?�일???�으�?.backup ?�동 ?�성 (?�용??코드 보호).
    백업???��? ?�으�???��?��? ?�음 (멱등??.
    v7: creds 가 주어지�?복사 ??�??�일?�서 placeholder 교체.
    v7.1: ?�격증명 ?�락 placeholder 가 ?�으�?경고 (?�영???�력 ?�도)."""
    os.makedirs(dst_dir, exist_ok=True)
    copied = 0
    backed_up = []
    injected = 0
    missing_placeholders = {}  # placeholder -> count
    for root, _dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target = os.path.join(dst_dir, rel) if rel != "." else dst_dir
        os.makedirs(target, exist_ok=True)
        for f in files:
            dst_path = os.path.join(target, f)
            if os.path.exists(dst_path):
                bk = dst_path + ".backup"
                if not os.path.exists(bk):
                    try:
                        shutil.copy2(dst_path, bk)
                        backed_up.append(os.path.relpath(dst_path, dst_dir))
                    except Exception:
                        pass
            shutil.copy2(os.path.join(root, f), dst_path)
            copied += 1
            # v7: ?�격증명 placeholder ?�동 inline
            if creds and any(creds.values()):
                if _inject_credentials(dst_path, creds):
                    injected += 1
            # v7.1: ?��? placeholder ?�캔 (�??�격증명 감�?)
            if creds:
                try:
                    with open(dst_path, "r", encoding="utf-8") as fh:
                        body = fh.read()
                    for ph, val in creds.items():
                        if not val and ph in body:
                            missing_placeholders[ph] = missing_placeholders.get(ph, 0) + 1
                except Exception:
                    pass
    if backed_up:
        _log(f"기존 ?�일 {len(backed_up)}�?.backup 보존: {', '.join(backed_up[:3])}{' ?? if len(backed_up) > 3 else ''}", "info")
    if injected:
        _log(f"?�� ?�영???�격증명 {injected}�??�일???�동 inline (Gemini/PayPal placeholder 교체)", "ok")
    if missing_placeholders:
        guide = {
            "__GEMINI_API_KEY__": "KoByeongKuk AI Lab ???��? ?�결 ????Google Gemini ??API Key ?�력",
            "__PAYPAL_CLIENT_ID__": "KoByeongKuk AI Lab ???��? ?�결 ???�� PayPal ??Client ID ?�력",
        }
        _log("?�️  ?�영???�격증명 ?�락 ???�트??복사?��?�??�제 ?�출?� ????", "warn")
        for ph in sorted(missing_placeholders):
            _log(f"   ??{ph} ??{guide.get(ph, '?��? ?�결 ?�널?�서 ?�력 ?�요')}", "warn")
        _log("   ?????�력 ???�트 ?�시 ?�용?�면 ?�동 inline ?�니??", "warn")
    return copied


def _find_app_file(project_path):
    """vite/next 모두 커버. src/App.tsx ?�선, ?�으�?App.tsx (expo)."""
    for cand in ["src/App.tsx", "App.tsx", "src/app/page.tsx", "app/page.tsx"]:
        p = os.path.join(project_path, cand)
        if os.path.exists(p):
            return p
    return None


def _update_app_tsx(app_path, imports, body):
    """App.tsx �?깨끗?�게 ?�로 ?�성. ?�본?� .backup ?�로 보존.
    v2: regex 부�?매칭?�로 ??JSX 가 ?�던 ?�고 ???�체 ??��?�기 + 백업 방식?�로 변�?"""
    try:
        with open(app_path, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception:
        return False

    # ?��? ?�트 ?�용?�으�?skip
    if all(f"from './components/{n}'" in original for n in imports):
        return False

    # 백업 ???�용?��? ?�댄 �??��? ?�게
    try:
        backup_path = app_path + ".backup"
        if not os.path.exists(backup_path):
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original)
    except Exception:
        pass

    # ??App.tsx ??깨끗??최소 버전
    import_lines = "\n".join([f"import {n} from './components/{n}'" for n in imports])
    new_content = f"""{import_lines}

export default function App() {{
  return (
    <main className="min-h-screen bg-white text-gray-900">
      {body}
    </main>
  );
}}
"""
    try:
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception:
        return False


def _find_brain_root():
    """?�뇌 ?�더 ?�동 ?�색 (?�국???�더�??�함).

    v4: BRAIN_ROOT ?�경변?��? 가??강함 (KoByeongKuk AI Lab ?�스?�션??직접 지??.
    ?�전??~/.connect-ai-brain 가 �??�더�?존재�??�도 ?�선 매칭?�서
    ?�제 ?�용???�뇌(~/Downloads/지?�메모리) ???�트�?�?찾던 ?�고 차단.
    """
    env = os.environ.get("BRAIN_ROOT", "").strip()
    if env:
        ep = os.path.expanduser(env)
        if os.path.exists(ep):
            return ep
    cands = [
        os.path.expanduser("~/Downloads/지?�메모리"),
        os.path.expanduser("~/.connect-ai-brain"),
        os.path.expanduser("~/.connect-ai-brain-imported"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]  # �?번째 fallback


def _list_kits(brain_root):
    """developer 카테고리??모든 ?�트?� manifest 반환."""
    tdir = os.path.join(brain_root, "40_?�플�?, "developer")
    if not os.path.exists(tdir):
        return []
    kits = []
    for name in os.listdir(tdir):
        d = os.path.join(tdir, name)
        if not os.path.isdir(d):
            continue
        mp = os.path.join(d, "manifest.json")
        if not os.path.exists(mp):
            continue
        try:
            with open(mp, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            kits.append({"name": name, "manifest": manifest})
        except Exception:
            pass
    return kits


def _score_kit(manifest, intent_text):
    """매니?�스??vs ?�용???�도(intent_text) 매칭 ?�수.
    keywords + name + description ?�어 매칭. ?�국?�·영??모두."""
    if not intent_text:
        return 0
    haystack = " ".join([
        manifest.get("name", ""),
        manifest.get("description", ""),
        " ".join(manifest.get("keywords") or []),
        manifest.get("category", ""),
    ]).lower()
    intent_lc = intent_text.lower()
    score = 0
    # keywords 직접 매칭 (?��? 가중치)
    for kw in (manifest.get("keywords") or []):
        if kw.lower() in intent_lc:
            score += 10
    # name ?�체가 ?�도???�으�?(?? "landing-kit" ??"landing")
    for token in manifest.get("name", "").split():
        if len(token) >= 3 and token.lower() in intent_lc:
            score += 5
    # 카테고리
    if (manifest.get("category", "").lower() or "") in intent_lc:
        score += 3
    return score


def _autodetect_kit(brain_root, intent_text):
    """?�용???�도?�서 가???�합???�트 ?�동 추론. (kit_name, score, alternatives) 반환."""
    kits = _list_kits(brain_root)
    if not kits:
        return None, 0, []
    scored = [(k["name"], _score_kit(k["manifest"], intent_text), k["manifest"].get("description", "")) for k in kits]
    scored.sort(key=lambda x: -x[1])
    if scored[0][1] == 0:
        # 매치 0 ??fallback: 가???�반?�인 landing-kit
        for k in kits:
            if k["name"] == "landing-kit":
                return "landing-kit", 0, scored[:3]
        return kits[0]["name"], 0, scored[:3]
    return scored[0][0], scored[0][1], scored[:3]


def _parse_cli_args():
    """v4: 로컬 LLM ??CLI ?�자�??�출?�는 ?�턴??지??
       `--kit landing-kit --user-intent "..." --project /path` ?�는
       ?�경변??KIT_NAME / USER_INTENT / PROJECT_PATH."""
    out = {}
    args = sys.argv[1:]
    i = 0
    aliases = {
        "--kit": "KIT_NAME", "--kit-name": "KIT_NAME",
        "--user-intent": "USER_INTENT", "--intent": "USER_INTENT",
        "--project": "PROJECT_PATH", "--project-path": "PROJECT_PATH",
        "--brain-root": "BRAIN_ROOT", "--brain": "BRAIN_ROOT",
    }
    while i < len(args):
        a = args[i]
        if a in aliases and i + 1 < len(args):
            out[aliases[a]] = args[i + 1]
            i += 2
        elif "=" in a and a.startswith("--"):
            k, v = a[2:].split("=", 1)
            key = aliases.get("--" + k)
            if key:
                out[key] = v
            i += 1
        else:
            i += 1
    for k in ("KIT_NAME", "USER_INTENT", "PROJECT_PATH", "BRAIN_ROOT"):
        if k in os.environ and os.environ[k].strip():
            out.setdefault(k, os.environ[k])
    return out


def main():
    cfg = _load(CONFIG)
    init_cfg = _load(WEB_INIT_CFG)

    cli = _parse_cli_args()
    for k, v in cli.items():
        if v and str(v).strip():
            cfg[k] = v

    kit_name = (cfg.get("KIT_NAME") or "").strip()
    user_intent = (cfg.get("USER_INTENT") or "").strip()

    # v5: CLI --brain-root 가 ?�으�?env 처럼 ?�동?�켜 _find_brain_root ?�선?�위 ?�용
    cli_brain = cli.get("BRAIN_ROOT", "").strip() if cli else ""
    if cli_brain:
        os.environ["BRAIN_ROOT"] = cli_brain
    # ?�뇌 ?�더 찾기 (?�동 추론?�도 ?�요)
    brain_root = _find_brain_root()

    # v3: KIT_NAME 비어?�고 USER_INTENT ?�으�??�동 매칭
    selection_card = ""
    if not kit_name and user_intent:
        detected, score, alts = _autodetect_kit(brain_root, user_intent)
        if detected:
            kit_name = detected
            _log(f"?�동 추론 ??'{kit_name}' (매칭 ?�수 {score})", "info")
            if score == 0:
                _log("  ?�️ ?�용???�도?� 명확??매칭 ?�음. 가???�반?�인 ?�트�?fallback.", "warn")
            # ?�각 카드 (stdout??마크?�운 ??채팅창에 ?�더링됨)
            card_lines = [
                "",
                "## ?�� ?�트 ?�동 ?�택",
                "",
                f"> ?�용???�도: _\"{user_intent}\"_",
                "",
                "| ?�위 | ?�트 | 매칭 ?�수 | 비고 |",
                "|---|---|---|---|",
            ]
            for i, (n, s, desc) in enumerate(alts):
                marker = "**�??�택**" if n == kit_name else ""
                d_short = (desc[:50] + "??) if len(desc) > 50 else desc
                card_lines.append(f"| {i+1} | `{n}` | **{s}** | {marker} {d_short} |")
            if score == 0:
                card_lines.append("")
                card_lines.append("?�️ _명확??매칭 ?�음 ??fallback?�로 가???�반?�인 ?�트 ?�택._")
            card_lines.append("")
            card_lines.append("> ?�� ?�른 ?�트�?바꾸?�면 `pack_apply` �?`KIT_NAME=<?�하???�트>` �??�시 ?�행.")
            card_lines.append("")
            selection_card = "\n".join(card_lines)

    if not kit_name:
        kits = _list_kits(brain_root)
        avail = ", ".join([f"'{k['name']}'" for k in kits]) or "(?�뇌???�트 ?�음 ??EZER ?�서 먼�? 주입)"
        _log(f"KIT_NAME 비어?�고 USER_INTENT ???�음.", "err")
        _log(f"  방법 1: KIT_NAME 명시 ??{avail}", "info")
        _log(f"  방법 2: USER_INTENT ??'?�이?�트 SaaS ?�딩' 같�? ?�연???�력 ???�동 추론", "info")
        sys.exit(1)

    project = (cfg.get("PROJECT_PATH") or "").strip()
    if not project:
        project = (init_cfg.get("LAST_PROJECT") or "").strip()
    if not project:
        _log("PROJECT_PATH 비어?�고 web_init 기록???�음", "err")
        sys.exit(1)
    project = os.path.expanduser(project)
    if not os.path.isdir(project):
        _log(f"?�로?�트 ?�더 ?�음: {project}", "err")
        sys.exit(1)

    kit_dir = os.path.join(brain_root, "40_?�플�?, "developer", kit_name)
    if not os.path.exists(kit_dir):
        _log(f"?�트 ?�음: {kit_dir}", "err")
        _log(f"먼�? EZER Pack Vault ?�서 '{kit_name}' 주입?�세??", "info")
        sys.exit(1)

    manifest_path = os.path.join(kit_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        _log(f"manifest ?�음: {manifest_path}", "err")
        sys.exit(1)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    apply = manifest.get("apply", {})
    copy_to = apply.get("copy_to", "src/components/")
    post_install = apply.get("post_install", [])
    app_imports = apply.get("app_imports", [])
    app_body = apply.get("app_body", "")

    _log(f"?�트: {manifest.get('name', kit_name)} ??{project}", "info")
    _log(f"기반: {manifest.get('base', '?')}", "info")

    # v7: ?�영???�격증명 로드 (Gemini/PayPal placeholder ?�동 inline)
    creds = _load_operator_credentials(brain_root)

    # 1) ?�일 복사 (+ placeholder 교체)
    src_files = os.path.join(kit_dir, "files")
    dst_files = os.path.join(project, copy_to.lstrip("./"))
    if not os.path.exists(src_files):
        _log("?�트??files/ ?�더 ?�음 ???�일 복사 ?�킵", "warn")
    else:
        n = _copy_tree(src_files, dst_files, creds=creds)
        _log(f"{n}�??�일 복사 ??{dst_files}", "ok")

    # 2) ?�존???�동 ?�치
    if post_install:
        _log(f"?�존??{len(post_install)}�??�치 �?..", "info")
        for cmd in post_install:
            ok = _run(cmd, cwd=project)
            if not ok:
                _log(f"부가 명령 ?�패: {cmd} ??계속 진행", "warn")

    # 3) App.tsx ?�동 ?�데?�트 (best-effort)
    if app_imports:
        app_file = _find_app_file(project)
        if app_file:
            changed = _update_app_tsx(app_file, app_imports,
                                      app_body or "\n".join([f"<{n} />" for n in app_imports]))
            if changed:
                _log(f"App.tsx ?�동 ?�데?�트: {app_file}", "ok")
            else:
                _log(f"App.tsx ?��? ?�정???�는 ?�턴 매칭 ?�패 ???�동 ?�인: {app_file}", "warn")
        else:
            _log("App.tsx �?찾음 ???�동?�로 import + JSX 추�? ?�요", "warn")

    # 결과 ??stdout ?�로 마크?�운 (채팅�??�더�?
    if selection_card:
        print(selection_card)
    print()
    print(f"## ???�용 ?�료: `{manifest.get('name', kit_name)}`")
    print()
    print(f"- **?�치**: `{project}`")
    print(f"- **기반**: {manifest.get('base', '?')}")
    if "expo" in (manifest.get("base", "").lower()):
        print(f"- **?�행**: `cd {project} && npm start` ???�에 Expo Go 깔고 QR ?�캔")
    else:
        print(f"- **?�행**: `cd {project} && npm run dev` ??http://localhost:5173")
    print()
    _log(f"?�용 ?�료: {kit_name}", "ok")


if __name__ == "__main__":
    main()
