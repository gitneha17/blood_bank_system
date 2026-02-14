from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import os


def generate_certificate(
    donor_name,
    blood_group,
    units,
    donation_date,
    save_path="certificates"
):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_name = f"{donor_name.replace(' ', '_')}_certificate.pdf"
    file_path = os.path.join(save_path, file_name)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b><font size=22>Certificate of Appreciation</font></b>", styles["Title"]))
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph(
        "This is to proudly certify that", styles["Normal"]
    ))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph(
        f"<b><font size=16>{donor_name}</font></b>", styles["Title"]
    ))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(
        f"has voluntarily donated <b>{units}</b> units of <b>{blood_group}</b> blood "
        f"on <b>{donation_date}</b> and contributed towards saving lives.",
        styles["Normal"]
    ))

    story.append(Spacer(1, 0.5 * inch))

    story.append(Paragraph(
        f"Certificate ID: BBMS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        styles["Normal"]
    ))

    story.append(Spacer(1, 1 * inch))

    story.append(Paragraph(
        "Authorized Signatory<br/>Blood Bank Management System",
        styles["Normal"]
    ))

    doc.build(story)

    return file_path
