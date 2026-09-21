import json
import re
from pathlib import Path


ROOT = Path(__file__).parent


SUMMARIES = {
    "DAY 2": [
        "Fixed Voice: مدة تركيب FTTH compound في الإسكندرية 7 أيام.",
        "لو نتيجة Check availability: Not available و Survey started، الطلب بيروح تلقائي لفريق المعاينة.",
        "بيانات أي order بتتراجع من View، وخدمة Add/Remove VAS بتتم On-Spot.",
        "العميل عنده 14 يوم يكمل إجراءات اشتراك FV بعد رسالة SMS.",
        "اختيار Modify reason = Operator Request متاح للـ Supervisor.",
    ],
    "DAY 3": [
        "ركز على Fixed Voice part 2 و SLA، خصوصا الحالات اللي محتاجة SR أو توجيه للفرع.",
        "راجع صور Info graph SLA لأنها غالبا بتلخص أزمنة الحل والتصعيد.",
        "أي سؤال فيه رسالة أو Screenshot لازم تربطه بالصورة المرفقة قبل اختيار الإجابة.",
    ],
    "DAY 4": [
        "New Subscription: لازم مراجعة landline bills و Check availability قبل الاشتراك.",
        "SLA إنترنت MSAN/TDM هو 5 أيام، و Door to Door للـ FV هو 48 ساعة.",
        "Restart port يتم من CST 360، و Check availability من CST 360.",
        "سعر الراوتر المتاح 1710 شامل الضريبة، و CPE installment متاح من خلال البنك.",
        "سرعة Mega تصل إلى 70M، و Upload speed مش لازم تتقال للعميل.",
    ],
    "DAY 5": [
        "Customer Request Part 1: Daily usage من BSS، والباقات الإضافية المتكررة متاحة ADSL/VDSL/FTTH.",
        "Salfny لو ظهرت رسالة عدم الإتاحة، بلغ العميل إنها غير متاحة.",
        "راجع صور الأسئلة لأنها مرتبطة برسائل النظام والإجراءات الصحيحة.",
    ],
    "DAY 6": [
        "Customer Request Part 2: بعد Early renewal العميل يفقد أي quota أو أيام متبقية حسب السؤال.",
        "لو HDM Offline الإجراء الصحيح Restart Port.",
        "أي مشكلة في HDM Portal لازم تتسجل في SR مع Snapshot للخطأ.",
        "قبل BLQ troubleshooting لازم مراجعة port type.",
        "SLA escalation suspension هو 72 ساعة.",
    ],
    "DAY 7": [
        "Tools: راجع Cheat sheets لأنها أهم مرجع سريع لأماكن الأدوات والمسارات.",
        "Active speed Mega up to 70 مع سرعة مختلفة قد تشير إلى Speed variance.",
        "Many accepted logs والنتائج المتكررة تساعدك تميز logical instability.",
        "استخدم الصور كدليل على شكل الشاشة الصحيح قبل اختيار SR أو Tool.",
    ],
    "DAY 8": [
        "Logical cases: ADSL CPE أقصى سرعة له 24M، و VDSL CPE يدعم حتى 100M.",
        "Private IP مثال واضح: 192.168.1.2.",
        "NAT يحول بين Private IP و Public IP، و DNS يحول بين IP و Domain.",
        "SSID هو Wireless network name، و default MTU قيمته 1492.",
        "Unable to connect to wireless أول خطوة فيها Check with another device.",
    ],
    "DAY 9": [
        "Logical Instability & Slowness: لازم تبلغ العميل يسيب CPE شغال أثناء التصعيد، ما عدا wrong pool أو no profile on NST.",
        "Slowness case SLA هو 2H، والتصعيد يكون إلى NOC.",
        "OTS SLA هو 5WD، و escalation suspension هو 72H.",
        "لو بعد reset/configuration التحميل غير مقبول، الخطوة التالية Check with another OS/PC.",
        "في logical instability لمبة ADSL بتبقى ثابتة، ولازم logical verification قبل التعامل مع الحالة.",
    ],
    "DAY 10": [
        "FTTH يعتمد على GPON ثم OLT ثم Splitter ثم Box ثم جهاز العميل ONT/ONU.",
        "ONU لصوت فقط، و ONT لصوت وإنترنت، وكل أجهزة ONT المذكورة Huawei بضمان سنة.",
        "SLA تركيب FTTH: القاهرة/الجيزة/الإسكندرية 7 أيام، وباقي المحافظات 10 أيام.",
        "مشكلة CST Problem غير المحلولة تلغي طلب FTTH تلقائيا بعد 60 يوم.",
        "أخطاء FTTH المهمة: Incomplete Cross Connection لقسم FO-Fiber، و Wrong Address/Exchange لقسم Sales-FTTH.",
    ],
}


def clean(value):
    value = value.replace("\u200b", "")
    value = re.sub(r"\r\n?", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def is_material_file(path):
    return any(re.search(r"matrual|matrial|material", part, re.IGNORECASE) for part in path.parts)


def organize_material_text(value):
    value = clean(value)
    if not value:
        return ""
    value = value.replace("$$", "")
    value = re.sub(r"\\text\{([^}]+)\}", r"\1", value)
    value = value.replace("\\rightarrow", "→")
    value = value.replace("$", "")
    value = re.sub(r"\)\s*(الـ)", r")\n\1", value)

    section_markers = [
        "المحور الأول",
        "المحور الثاني",
        "المحور الثالث",
        "المحور الرابع",
        "المحور الخامس",
        "قواعد وضوابط الأجهزة:",
        "مراحل الزيارات والمدد الزمنية",
        "نقطة عدم الرجوع",
        "الأنشطة التلقائية",
        "أنشطة التدخل البشري",
        "أنواع المشاكل الشائعة وطرق التعامل معها:",
        "أول قاعدة",
        "مهم جدًا:",
        "حالات مهمة:",
        "سؤال امتحان مباشر:",
    ]
    item_markers = [
        "GPON (",
        "OLT (",
        "Splitter (",
        "Box:",
        "ONU (",
        "ONT (",
        "داخل الكمبوند",
        "داخل الأبراج",
        "جهاز العميل:",
        "جهاز إيجار واحد فقط:",
        "الجمع بين الأجهزة:",
        "التملك (Out Cash):",
        "تسليم الأجهزة للجدد",
        "القاهرة والجيزة والإسكندرية",
        "زيارة الـ Survey",
        "زيارة الـ Home Visit",
        "باقي المحافظات",
        "الكمبوندات الخاصة",
        "تعديل السرعة",
        "تعديل رقم الموبايل",
        "Incomplete Cross Connection:",
        "Get FTTH Path API Failed",
        "خطأ في العنوان",
        "مشاكل من طرف العميل",
        "إذا قام العميل",
    ]

    value = re.sub(r"(🟦\s*DAY\s+\d+)", r"\n\n\1", value)
    value = re.sub(r"([0-9]+️⃣)", r"\n\n\1", value)
    value = re.sub(r"(?<!\n)(\d+\.\s+)", r"\n\n\1", value)
    for marker in section_markers:
        value = value.replace(marker, f"\n\n## {marker}")
    for marker in item_markers:
        value = value.replace(marker, f"\n- {marker}")
    value = re.sub(r"(?<!\n)(✅|❌|⚠️|⭐)", r"\n- \1", value)
    value = re.sub(r"(?<!\n)(→)", r"\n- \1", value)
    value = re.sub(
        r"- GPON \(Central\)\s*\n- →\s*\n- OLT \(ODF/ODN\)\s*\n- → Splitter\s*\n- → Box\s*\n- → Customer Unit \(ONT/ONU\)",
        "- GPON (Central) → OLT (ODF/ODN) → Splitter → Box → Customer Unit (ONT/ONU)",
        value,
    )
    value = re.sub(r"(?<=[.؟:])(?=(?:[اأإآ]ل|لو|لما|في|ومن|بعد|قبل|يتم|لازم|مهم|SLA|VDSL|ADSL|FTTH|BSS|OM|CST|CCA|New|Existing|Upload|Start|Speed|Current|Customer|Data|Voice|Survey|Home|Wrong|No Free|Get FTTH|Incomplete))", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def day_name(path):
    for part in path.parts:
        if re.fullmatch(r"DAY \d+", part, re.IGNORECASE):
            return part.upper()
    return "GENERAL"


def title_from_path(day, path):
    parts = list(path.parts)
    day_index = parts.index(day) if day in parts else 0
    title_parts = parts[day_index + 1 : -1]
    return " / ".join(title_parts) if title_parts else day


def correct_answer(block):
    if "The correct answer is" not in block:
        return ""
    after = block.split("The correct answer is", 1)[1].strip()
    if after.startswith("'"):
        match = re.match(r"'([^']+)'", after)
        return clean(match.group(1)) if match else ""
    after = after.lstrip(":").strip()
    lines = [clean(line) for line in after.splitlines() if clean(line)]
    return lines[0] if lines else ""


def parse_options(answer_text):
    answer_text = clean(answer_text)
    if not answer_text:
        return []
    lines = [clean(line) for line in answer_text.splitlines() if clean(line)]
    if set(line.lower() for line in lines[:2]) == {"true", "false"}:
        return ["True", "False"]
    options = []
    current = None
    for line in lines:
        if re.fullmatch(r"[A-Da-d]\.", line):
            if current:
                options.append(clean(" ".join(current)))
            current = []
            continue
        if current is not None:
            current.append(line)
    if current:
        options.append(clean(" ".join(current)))
    return options


def parse_question_file(path):
    if is_material_file(path):
        return []
    text = clean(path.read_text(encoding="utf-8"))
    blocks = re.split(r"(?=Question \d+\b\s*\n)", text)
    questions = []
    for block in blocks:
        match = re.match(r"Question (\d+)\b", block)
        if not match:
            continue
        number = int(match.group(1))
        answer_marker = f"Question {number}Answer"
        if "Question text" not in block or answer_marker not in block:
            continue
        question_text = clean(block.split("Question text", 1)[1].split(answer_marker, 1)[0])
        answer_section = block.split(answer_marker, 1)[1].split("Feedback", 1)[0]
        answer = correct_answer(block)
        questions.append(
            {
                "id": f"{day_name(path)}-{number}",
                "day": day_name(path),
                "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                "topic": title_from_path(day_name(path), path),
                "number": number,
                "question": question_text,
                "options": parse_options(answer_section),
                "answer": answer,
            }
        )
    return questions


def image_record(path):
    day = day_name(path)
    relative = str(path.relative_to(ROOT)).replace("\\", "/")
    folder = path.parent.name
    kind = "question" if "question" in relative.lower() or "qusetion" in relative.lower() else "summary"
    return {
        "day": day,
        "path": relative,
        "folder": folder,
        "kind": kind,
        "label": f"{day} - {folder}",
        "note": OCR_NOTES.get(relative, ""),
    }


def image_question_number(path):
    if not re.search(r"question|qusetion|questoin", str(path), re.IGNORECASE):
        return None
    match = re.match(r"(\d+)", path.stem)
    return int(match.group(1)) if match else None


def attach_question_images(questions, images):
    lookup = {}
    for image in images:
        number = image_question_number(image)
        if number is None:
            continue
        lookup.setdefault((day_name(image), number), []).append(str(image.relative_to(ROOT)).replace("\\", "/"))
    for question in questions:
        question["images"] = lookup.get((question["day"], question["number"]), [])


def parse_material_file(path):
    text = organize_material_text(path.read_text(encoding="utf-8-sig"))
    if not text:
        return None
    return {
        "day": day_name(path),
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "title": title_from_path(day_name(path), path),
        "text": text,
    }


def load_ocr_notes():
    notes_path = ROOT / "ocr-notes.json"
    if not notes_path.exists():
        return {}
    return json.loads(notes_path.read_text(encoding="utf-8-sig"))


def build_data():
    txt_files = sorted(ROOT.glob("DAY */**/*.txt"))
    images = sorted(
        [
            path
            for pattern in ("DAY */**/*.png", "DAY */**/*.jpg", "DAY */**/*.jpeg")
            for path in ROOT.glob(pattern)
        ]
    )
    questions = []
    materials = []
    for path in txt_files:
        questions.extend(parse_question_file(path))
        material = parse_material_file(path) if is_material_file(path) else None
        if material:
            materials.append(material)
    attach_question_images(questions, images)
    days = sorted({day_name(path) for path in txt_files + images}, key=lambda value: int(value.split()[1]))
    return {
        "days": [
            {
                "name": day,
                "summary": SUMMARIES.get(day, []),
                "questionCount": sum(1 for question in questions if question["day"] == day),
                "imageCount": sum(1 for image in images if day_name(image) == day),
                "materialCount": sum(1 for material in materials if material["day"] == day),
            }
            for day in days
        ],
        "questions": questions,
        "images": [image_record(path) for path in images],
        "materials": materials,
    }


OCR_NOTES = load_ocr_notes()


if __name__ == "__main__":
    data = build_data()
    output = "window.WE_STUDY_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "study-data.js").write_text(output, encoding="utf-8")
    print(f"Generated {len(data['questions'])} questions and {len(data['images'])} images.")
