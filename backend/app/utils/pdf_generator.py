import os

def export_text_document(output_path: str, content: str):
    """
    Writes a pristine, cleanly formatted executive document straight to disk.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[Exporter] Clean document written to: {output_path}")
    except Exception as e:
        print(f"[Exporter Error] Failed writing document: {str(e)}")


def export_pdf_document(output_path: str, title: str, content: str):
    """
    Writes a professionally typeset executive PDF matching modern corporate standards
    with 2-column aligned dates, custom section divider bars, and executive slate typography.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except Exception:
        # Fallback: write plain text file with .pdf extension
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(title + "\n\n")
                f.write(content)
            print(f"[Exporter] Fallback text document written to: {output_path}")
        except Exception as e:
            print(f"[Exporter Error] Failed fallback PDF write: {str(e)}")
        return

    try:
        margin = 40  # 0.55 inches margin for optimal density
        width, height = letter
        printable_width = width - margin * 2

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#1E293B")   # Slate 800
        accent_color = colors.HexColor("#0284C7")    # Sky Blue Accent
        dark_heading = colors.HexColor("#0F172A")     # Slate 900
        secondary_color = colors.HexColor("#475569")  # Slate 600
        divider_color = colors.HexColor("#CBD5E1")    # Slate 300

        title_style = ParagraphStyle(
            'ResumeTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=dark_heading,
            alignment=0,
            spaceAfter=3
        )

        subtitle_style = ParagraphStyle(
            'ResumeSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=accent_color,
            alignment=0,
            spaceAfter=4
        )

        contact_style = ParagraphStyle(
            'ResumeContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=secondary_color,
            alignment=0,
            spaceAfter=10
        )

        section_heading_style = ParagraphStyle(
            'ResumeSectionHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=accent_color,
            spaceBefore=0,
            spaceAfter=2,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'ResumeBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=primary_color,
            spaceAfter=3
        )

        bullet_style = ParagraphStyle(
            'ResumeBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=primary_color,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=2.5
        )

        role_left_style = ParagraphStyle(
            'RoleLeft',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13,
            textColor=dark_heading
        )

        role_right_style = ParagraphStyle(
            'RoleRight',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=secondary_color,
            alignment=2  # Right aligned
        )

        import re

        def printable(value, format_markdown=True):
            if not value:
                return ""
            value = (value.replace("—", "-")
                          .replace("–", "-")
                          .replace("•", "&bull;")
                          .replace("…", "...")
                          .replace("’", "'")
                          .replace("‘", "'")
                          .replace("”", '"')
                          .replace("“", '"'))
            if format_markdown:
                # Convert markdown bold/italics to HTML tags
                value = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', value)
                value = re.sub(r'\*(.*?)\*', r'<i>\1</i>', value)
            else:
                value = value.replace("**", "").replace("*", "")
                value = re.sub(r'</?[bi]>', '', value)

            # Clean up unwanted spaces before and around hyphens in compound words & numbers (e.g., "AI -enabling" -> "AI-enabling")
            value = re.sub(r'(\b[A-Za-z0-9]+)\s+-\s*([a-z0-9]+)', r'\1-\2', value)
            value = re.sub(r'(\b[A-Za-z0-9]+)\s*-\s+([a-z0-9]+)', r'\1-\2', value)
            value = re.sub(r'\b(AI|AWS|Cloud|Multi|Security|Self|Cross|High|Large|First|Next|Long|Short)\s+-\s*([A-Za-z0-9]+)', r'\1-\2', value, flags=re.IGNORECASE)
            value = re.sub(r'(\d+)\s+-\s*(\d+)', r'\1-\2', value)

            return value.encode("latin-1", "replace").decode("latin-1")

        def make_section_header(title_text):
            p = Paragraph(printable(title_text.upper(), format_markdown=False), section_heading_style)
            t = Table([[p]], colWidths=[printable_width])
            t.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 0), (-1, -1), 1.2, accent_color),
            ]))
            return t

        def make_two_column_row(left_text, right_text):
            p_left = Paragraph(printable(left_text), role_left_style)
            p_right = Paragraph(printable(right_text), role_right_style)
            t = Table([[p_left, p_right]], colWidths=[printable_width * 0.68, printable_width * 0.32])
            t.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            return t

        def is_date_str(text):
            text_lower = text.lower()
            months = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "present"}
            has_month = any(m in text_lower for m in months)
            has_year = bool(re.search(r'\b\d{4}\b', text))
            return (has_month or has_year) and ("-" in text or "present" in text_lower)

        story = []
        is_resume = "resume" in title.lower() or "resume" in content.lower()[:300] or "ran eliahu" in content.lower()[:300]

        lines = [l.strip() for l in content.splitlines() if l.strip()]

        if is_resume:
            start_idx = 0
            if lines and ("tailored resume" in lines[0].lower() or "target role" in lines[0].lower()):
                start_idx = 1

            # Header Parsing
            header_lines = []
            section_triggers = {
                "EXECUTIVE PROFILE", "CORE COMPETENCIES", "PROFESSIONAL EXPERIENCE",
                "TECHNOLOGY & PLATFORM EXPERTISE", "EDUCATION", "TARGET ROLE ALIGNMENT",
                "EXECUTIVE STRENGTHS", "EXPERIENCE"
            }

            while start_idx < len(lines):
                line = lines[start_idx]
                clean_line = line.lstrip("#").strip().upper()
                if any(st in clean_line for st in section_triggers) and len(clean_line) < 40:
                    break
                header_lines.append(line)
                start_idx += 1

            if header_lines:
                # Candidate Name
                story.append(Paragraph(printable(header_lines[0], format_markdown=False), title_style))
                # Candidate Subtitle Tagline
                if len(header_lines) > 1:
                    story.append(Paragraph(printable(header_lines[1], format_markdown=False), subtitle_style))
                # Contact info
                if len(header_lines) > 2:
                    contact = " | ".join([hl for hl in header_lines[2:] if not hl.startswith("##")])
                    contact = re.sub(r'\s*\|\s*\|\s*', ' | ', contact)
                    story.append(Paragraph(printable(contact, format_markdown=False), contact_style))
                story.append(Spacer(1, 4))

            # Body Sections Parsing
            i = start_idx
            current_company = ""
            current_location = ""
            current_section = ""
            skip_section = False

            while i < len(lines):
                line = lines[i]
                clean_line = line.lstrip("#").strip()
                clean_upper = clean_line.upper()

                # Skip internal alignment metadata sections in PDF
                if "TARGET ROLE ALIGNMENT" in clean_upper or "STRATEGIC FOCUS FOR TARGET" in clean_upper:
                    skip_section = True
                    i += 1
                    continue

                if skip_section:
                    if (line.startswith("##") or (line.isupper() and len(line) < 45)) and any(st in clean_upper for st in section_triggers if st != "TARGET ROLE ALIGNMENT"):
                        skip_section = False
                    else:
                        i += 1
                        continue

                # Detect Section Header
                if (line.startswith("##") or (line.isupper() and len(line) < 45)) and any(st in clean_upper for st in section_triggers):
                    current_section = clean_upper
                    story.append(Spacer(1, 6))
                    story.append(make_section_header(clean_line))
                    story.append(Spacer(1, 4))
                    i += 1
                    continue

                # Detect Company / Institution Header (e.g. ### Northwestern Mutual | Milwaukee, WI)
                if line.startswith("###") or (("Northwestern Mutual" in line or "Marquette" in line or "Academic College" in line or "Corporation" in line) and "|" in line and not line.startswith("-") and not line.startswith("•") and not line.startswith("*") and not line.startswith("**")):
                    parts = clean_line.split(" | ") if " | " in clean_line else clean_line.split(" - ")
                    current_company = parts[0].strip()
                    current_location = parts[1].strip() if len(parts) > 1 else ""
                    i += 1
                    continue

                # Detect Job Title / Degree & Date line in PROFESSIONAL EXPERIENCE or EDUCATION section
                is_title_line = (
                    ("PROFESSIONAL EXPERIENCE" in current_section or "EDUCATION" in current_section) and
                    (line.startswith("**") or line.startswith("###") or "|" in line or is_date_str(line)) and
                    not line.startswith("- ") and not line.startswith("•") and not line.startswith("* ") and
                    len(line) < 140
                )
                if is_title_line:
                    title_part = line
                    date_part = ""
                    
                    if "|" in line:
                        p_parts = line.split("|")
                        title_part = p_parts[0].strip()
                        date_part = p_parts[1].strip()
                    elif "(" in line and ")" in line:
                        m = re.search(r'\((.*?)\)', line)
                        if m and is_date_str(m.group(1)):
                            date_part = m.group(1)
                            title_part = line.replace(f"({date_part})", "").strip()

                    left_label = f"<b>{title_part.replace('**', '').strip()}</b>"
                    if current_company and current_company.lower() not in left_label.lower():
                        left_label += f" &mdash; <i>{current_company}</i>"
                    right_label = f"{date_part.replace('*', '').strip()}"
                    if current_location and right_label:
                        right_label += f" | {current_location}"
                    elif current_location:
                        right_label = current_location

                    story.append(make_two_column_row(left_label, right_label))
                    i += 1
                    continue

                # Core Competency / Skill Grid Row (Bullet lines containing '|' ONLY in CORE COMPETENCIES section)
                if "CORE COMPETENCIES" in current_section and (line.startswith("-") or line.startswith("•") or line.startswith("*")) and "|" in line:
                    raw_content = line.lstrip("-•* ").strip()
                    parts = raw_content.split("|")
                    left_item = parts[0].strip()
                    right_item = parts[1].strip() if len(parts) > 1 else ""
                    p1 = Paragraph(f"&bull; {printable(left_item)}", bullet_style)
                    p2 = Paragraph(f"&bull; {printable(right_item)}", bullet_style) if right_item else Paragraph("", body_style)
                    t_grid = Table([[p1, p2]], colWidths=[printable_width * 0.5, printable_width * 0.5])
                    t_grid.setStyle(TableStyle([
                        ('TOPPADDING', (0, 0), (-1, -1), 1),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(t_grid)
                    i += 1
                    continue

                # Standard Bullet points
                if (line.startswith("-") and not line.startswith("---")) or line.startswith("•") or line.startswith("* "):
                    bullet_text = line.lstrip("-•* ").strip()
                    story.append(Paragraph(f"&bull; {printable(bullet_text)}", bullet_style))
                    i += 1
                    continue

                # Standard Body Paragraph (Executive Profile, etc.)
                story.append(Paragraph(printable(line), body_style))
                i += 1


        else:
            # Format Cover Letter / Outreach Note
            story.append(Paragraph(printable(title, format_markdown=False), title_style))
            story.append(Spacer(1, 10))
            
            for line in content.splitlines():
                line_strip = line.strip()
                if not line_strip:
                    story.append(Spacer(1, 6))
                else:
                    story.append(Paragraph(printable(line_strip), body_style))

        doc.build(story)
        print(f"[Exporter] Platypus PDF written to: {output_path}")

    except Exception as e:
        print(f"[Exporter Error] PDF generation failed: {str(e)}")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(title + "\n\n")
                f.write(content)
            print(f"[Exporter] Fallback text document written to: {output_path}")
        except Exception as fe:
            print(f"[Exporter Error] Ultimate fallback failed: {str(fe)}")

