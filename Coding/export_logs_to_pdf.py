from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import datetime
import logs_analysis

def export_logs_to_pdf():
    filename = f"logs_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Title page
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 200, "🔒 System Logs Report")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 240, datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S"))
    c.showPage()

    # Setup text object
    margin_left = 50
    margin_top = height - 50
    text = c.beginText(margin_left, margin_top)
    text.setFont("Courier", 10)

    # Gather logs
    log_sections = {
        "🔌 USB Logs": logs_analysis.get_usb_logs(),
        "🔐 Security Logs": logs_analysis.get_security_logs(),
        "⚙️ System Logs": logs_analysis.get_system_logs(),
        "🧠 Application Logs": logs_analysis.get_application_logs(),
        "🌐 DNS Logs": logs_analysis.get_dns_logs()
    }

    page_num = 1

    for title, content in log_sections.items():
        # Write section title
        text.setFont("Helvetica-Bold", 12)
        text.textLine(title)
        text.setFont("Courier", 10)
        text.textLine("")

        for line in content.splitlines():
            if text.getY() < 80:
                c.drawText(text)
                draw_footer(c, page_num)
                page_num += 1
                c.showPage()
                text = c.beginText(margin_left, margin_top)
                text.setFont("Courier", 10)
                text.textLine(title + " (Continued)")
                text.textLine("")
            text.textLine(line)

        # Add section separator
        if text.getY() < 100:
            c.drawText(text)
            draw_footer(c, page_num)
            page_num += 1
            c.showPage()
            text = c.beginText(margin_left, margin_top)
            text.setFont("Courier", 10)
        text.textLine("-" * 80)
        text.textLine("")

    # Final write
    c.drawText(text)
    draw_footer(c, page_num)
    c.save()
    return filename

def draw_footer(c, page_num):
    """Draw footer with page number."""
    width, height = A4
    c.setFont("Helvetica", 9)
    footer_text = f"Page {page_num}"
    c.drawCentredString(width / 2, 30, footer_text)
