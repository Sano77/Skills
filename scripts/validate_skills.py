#!/usr/bin/env python3
import os
import sys
import json

EXPECTED_SKILLS = [
    "higgsfield-brandkit",
    "higgsfield-generate",
    "higgsfield-marketplace-cards",
    "higgsfield-product-photoshoot",
    "higgsfield-soul-id",
    "higgsfield-video-explainer",
    "higgsfield-websites",
    "higgsfield-youtube-thumbnail",
]

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    lock_file = os.path.join(root, "skills-lock.json")
    skills_dir = os.path.join(root, ".agents", "skills")

    print(f"==> Checking skills-lock.json at: {lock_file}")
    if not os.path.isfile(lock_file):
        print("ERROR: skills-lock.json not found!", file=sys.stderr)
        return 1

    try:
        with open(lock_file, "r", encoding="utf-8") as f:
            lock_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse skills-lock.json: {e}", file=sys.stderr)
        return 1

    if lock_data.get("version") != 1:
        print(f"ERROR: Expected lockfile version 1, got {lock_data.get('version')}", file=sys.stderr)
        return 1

    locked_skills = lock_data.get("skills", {})
    if not isinstance(locked_skills, dict):
        print("ERROR: 'skills' field in skills-lock.json must be an object", file=sys.stderr)
        return 1

    print(f"==> Verifying expected skills directory: {skills_dir}")
    if not os.path.isdir(skills_dir):
        print(f"ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    errors = []
    for skill_name in EXPECTED_SKILLS:
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            errors.append(f"Missing directory for skill '{skill_name}'")
            continue

        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.isfile(skill_md):
            errors.append(f"Missing SKILL.md in '{skill_name}'")
            continue

        with open(skill_md, "r", encoding="utf-8") as sm:
            content = sm.read().strip()

        if len(content) < 50:
            errors.append(f"SKILL.md in '{skill_name}' is too short")

        if skill_name not in locked_skills:
            errors.append(f"Skill '{skill_name}' is not in skills-lock.json")
        else:
            entry = locked_skills[skill_name]
            if not entry.get("source") or not entry.get("skillPath") or not entry.get("computedHash"):
                errors.append(f"Invalid lock entry for '{skill_name}'")

        print(f"  [OK] {skill_name} validated successfully")

    for name in locked_skills.keys():
        if not os.path.isdir(os.path.join(skills_dir, name)):
            errors.append(f"Lockfile contains '{name}' which is missing in .agents/skills")

    if errors:
        print("\nValidation failed with errors:", file=sys.stderr)
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        return 1

    print(f"\nAll {len(EXPECTED_SKILLS)} skills and skills-lock.json passed validation successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
