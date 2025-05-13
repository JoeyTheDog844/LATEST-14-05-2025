from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, ListItem, ListFlowable, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from system_information import (
    get_system_info,
    get_network_details,
    get_last_windows_update,
    get_desktop_files,
    get_system_identity,
    get_all_user_accounts,
    get_plug_and_play_status,
    get_geolocation_status
)
from log_manager import (
    get_security_logs,
    get_system_logs,
    get_application_logs,
    get_dns_logs,
    get_usb_logs,
)
from security_logs import (
    get_antivirus_status,
    get_firewall_status,
    get_last_scan_time,
    get_usb_device_control_status,
    get_autoplay_status,
    get_rdp_status,
    get_telnet_status,
    get_default_share_status,
    get_shared_folder_status,
    check_saved_passwords,
    get_bios_password_status,
    get_login_password_status,
    get_password_policy_status,
    get_lockout_policy_status,
    get_open_ports,
)
from login_ip_history import get_last_logged_in_ips
from usb_devices_list import get_usb_history
from smartphone_dongle_history import get_smartphone_dongle_history
from extra_installed_programs import get_installed_programs
from startup_apps import get_startup_programs
from shared_folders import get_shared_folders
from unwanted_softwares import detect_unwanted_software
from remote_services import check_remote_services
from service_checker import check_critical_services
from datetime import datetime
import re

# Shared styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    name="CustomTitle",
    parent=styles["Title"],
    fontSize=32,
    leading=38,
    alignment=TA_CENTER,
    spaceAfter=10
)

body_style = ParagraphStyle(
    name="CustomBody",
    parent=styles["BodyText"],
    fontSize=16,
    leading=22,
    alignment=TA_CENTER,
    spaceAfter=8
)

toc_title_style = ParagraphStyle(
    name="TOCTitle",
    parent=styles["Heading2"],
    fontSize=19,
    alignment=0,  # Left-aligned
    spaceAfter=12
)

toc_item_style = ParagraphStyle(
    name="TOCItem",
    parent=styles["Normal"],
    fontSize=14,
    leftIndent=20,
    spaceAfter=6
)

disclaimer_style = ParagraphStyle(
    name="DisclaimerStyle",
    parent=styles["Normal"],
    fontSize=10,
    textColor=colors.grey,
    alignment=TA_CENTER,
    spaceBefore=30,
    spaceAfter=0
)

def create_first_page(name, lab):
    elements = []

    elements.append(Paragraph("<b><u>Cyber Security Audit Report</u></b>", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"<b>Name:</b> {name}", body_style))
    elements.append(Paragraph(f"<b>Lab:</b> {lab}", body_style))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Audit Timestamp:</b> {timestamp}", body_style))

    return elements

def create_table_of_contents():
    toc = []
    toc.append(Spacer(1, 20))
    toc.append(Paragraph("<b><u>Table of Contents</u></b>", toc_title_style))

    toc_items = [
        "1. Cyber Security Health Score",
        "2. System Information",
        "3. Network Details",
        "4. Security Information",
        "5. Users Accounts",
        "6. Last Windows Update",
        "7. RDP & Remote Services",
        "8. Critical Windows Services",
        "9. Desktop Files",
        "10. USB Device Connection History",
        "11. Smartphone / Dongle Connection History",
        "12. Installed Programs",
        "13. Startup Applications",
        "14. Shared Folders",
        "15. Unwanted Softwares",
        "16. Logs"
    ]


    for item in toc_items:
        toc.append(Paragraph(item, toc_item_style))

    # Add disclaimer
    disclaimer_text = "This report contains confidential information intended solely for the recipient. Unauthorized use or distribution is prohibited."
    toc.append(Spacer(1, 30))
    toc.append(Paragraph(disclaimer_text, disclaimer_style))

    toc.append(PageBreak())
    return toc

def add_header_footer(canvas, doc):
    """ Adds Audit Date (top-left), Audit Time (top-right), and Page Numbers (bottom-center). """
    audit_date = datetime.now().strftime("%Y-%m-%d")  # YYYY-MM-DD format
    audit_time = datetime.now().strftime("%H:%M:%S")  # HH:MM:SS format
    page_number = canvas.getPageNumber()  # Get current page number
    
    canvas.setFont("Helvetica", 10)

    # Top-left: Audit Date
    canvas.drawString(40, 750, f"AUDIT DATE: {audit_date}")
    
    # Top-right: Audit Time
    canvas.drawRightString(550, 750, f"AUDIT TIME: {audit_time}")

    # Bottom-center: Page Number
    canvas.drawCentredString(300, 30, f"{page_number}")  # X = 300 (Center), Y = 30 (Bottom)

def clean_text(text):
    """Removes non-printable characters and ensures proper line breaks for PDFs."""
    text = text.encode("ascii", "ignore").decode()  # ✅ Remove Unicode issues
    text = re.sub(r"[^\x20-\x7E\n]", "", text)  # ✅ Remove non-ASCII characters
    text = text.replace("\n", " ")  # ✅ Replace newlines with spaces for descriptions
    text = text.replace("?", "").strip()  # ✅ Remove unexpected `?`
    return text

def format_timestamp(timestamp):
    """Convert Windows Event timestamp to a readable format."""
    try:
        timestamp = timestamp.rstrip("Z")  # ✅ Remove trailing "Z"

        if "." in timestamp:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

        return dt.strftime("%Y-%m-%d %H:%M:%S")  # ✅ Readable format
    except ValueError:
        return timestamp  # Return as is if parsing fails
    
def generate_pdf_report(user_name="", user_lab=""):
    filename = "System_Audit_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)

    elements = []
    elements += create_first_page(user_name, user_lab)
    elements += create_table_of_contents()

    add_security_score_section(elements)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    error_style = ParagraphStyle("ErrorStyle", parent=body_style, textColor=colors.red)
    warning_style = ParagraphStyle("WarningStyle", parent=body_style, textColor=colors.orange)
    info_style = ParagraphStyle("InfoStyle", parent=body_style, textColor=colors.green)
    
    # ✅ Generate Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ✅ Title
    elements.append(Paragraph("<b><u>CYBER SECURITY AUDIT REPORT</u></b>", title_style))
    elements.append(Spacer(1, 20))  # Space after title

    # ✅ Collect System Information in Table
    system_info = get_system_info()
    elements.append(Paragraph("<b><u>System Information</u></b>", heading_style))
    elements.append(Spacer(1, 5))  # Small space before table

    # Define header text color variable
    header_text_color = colors.black  # Change this to colors.white, colors.black, etc.
    
    # Define table data with bold headers
    data = [[
    Paragraph(f'<b><font color="{header_text_color}">S.No</font></b>', styles["Normal"]),
    Paragraph(f'<b><font color="{header_text_color}">Parameter</font></b>', styles["Normal"]),
    Paragraph(f'<b><font color="{header_text_color}">Value</font></b>', styles["Normal"])
    ]]

    # Add actual system information data
    for i, (key, value) in enumerate(system_info.items(), start=1):
        data.append([str(i), key, str(value)])

    # Create table
    system_table = Table(data, colWidths=[50, 200, 250])

    # Apply styles (header row formatting)
    system_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), header_text_color),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Makes header bold
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Ensures normal font for data
    ]))
    # Apply alternating row colors
    for row_idx in range(1, len(data)):
        bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
        ]))

    elements.append(system_table)
    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Collect Network Details in Table
    network_details = get_network_details()
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("<b><u>Network Details</u></b>", heading_style))
    elements.append(Spacer(1, 10))  # Small space before table

    # Define header text color variable
    header_text_color = colors.black  # Change this to colors.white, colors.black, etc.

    data = [[
    Paragraph(f'<b><font color="{header_text_color}">S.No</font></b>', styles["Normal"]),
    Paragraph(f'<b><font color="{header_text_color}">Parameter</font></b>', styles["Normal"]),
    Paragraph(f'<b><font color="{header_text_color}">Value</font></b>', styles["Normal"])
    ]]

    for i, (key, value) in enumerate(network_details.items(), start=1):
        data.append([str(i), key, str(value)])

    network_table = Table(data, colWidths=[50, 200, 250])
    network_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), header_text_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Ensures normal font for data
    ]))
    # Apply alternating row colors
    for row_idx in range(1, len(data)):
        bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
        network_table.setStyle(TableStyle([
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
        ]))

    elements.append(network_table)
    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Security Information Table with Serial Number
    elements.append(Paragraph("<b><u>Security Information</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    # ✅ Add Serial Number Column
    security_data = [
        ["S.No", "Parameter", "Value"]  # Updated header with "S.No"
    ]

    # ✅ Get Open Ports Data
    open_ports = get_open_ports()
    open_ports_status = open_ports["tcp"]  # ✅ TCP Ports
    udp_services_status = open_ports["udp"]  # ✅ UDP Services

    # ✅ Populate table with serial numbers
    security_entries = [
        ["Timestamp", timestamp],
        ["Antivirus Installed", get_antivirus_status()],
        ["Windows Firewall Status", get_firewall_status()],
        ["Last Windows Defender Scan Time", get_last_scan_time()],
        ["USB Storage Device Access", get_usb_device_control_status()],
        ["AutoPlay Status", get_autoplay_status()],
        ["Remote Desktop Protocol (RDP)", get_rdp_status()],
        ["Telnet", get_telnet_status()],
        ["Default Share Status", get_default_share_status()],
        ["Shared Folder Status", get_shared_folder_status()],
        ["Passwords not saved in web/system", check_saved_passwords()],
        ["BIOS Password", get_bios_password_status()],
        ["Windows Login Password", get_login_password_status()],
        ["Password Policy", get_password_policy_status()],
        ["System Lockout Policy", get_lockout_policy_status()],
        ["Open TCP Ports", "\n".join(open_ports_status) if open_ports_status else "No open TCP ports detected."],
        ["UDP Services", "\n".join(udp_services_status) if udp_services_status else "No active UDP services detected."],
    ]

    # ✅ Add serial numbers dynamically
    for i, (parameter, value) in enumerate(security_entries, start=1):
        security_data.append([str(i), parameter, str(value)])

    # ✅ Define column widths (adjusted for Serial Number)
    security_table = Table(security_data, colWidths=[50, 200, 250])

    # ✅ Apply table styles
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font bold
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data font
    ]))

    # ✅ Apply alternating row colors for readability
    for row_idx in range(1, len(security_data)):
        bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
        ]))

    elements.append(security_table)
    elements.append(Spacer(1, 20))  # Space after table

    # IP History
    elements.append(Paragraph("<b><u>Recent IP Login History</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    ip_logs = get_last_logged_in_ips()
    if ip_logs:
        ip_data = [["S.No", "IP Address", "Timestamp"]]
        for i, entry in enumerate(ip_logs, start=1):
            ip_data.append([str(i), entry["ip"], entry["timestamp"]])

        ip_table = Table(ip_data, colWidths=[50, 200, 200])
        ip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        # Apply row color alternation
        for idx in range(1, len(ip_data)):
            bg_color = colors.lightgrey if idx % 2 == 0 else colors.white
            ip_table.setStyle([('BACKGROUND', (0, idx), (-1, idx), bg_color)])

        elements.append(ip_table)
    else:
        elements.append(Paragraph("<i>No recent external logins detected.</i>", body_style))

    # ✅ Users Accounts
    elements.append(Paragraph("<b><u>Users Accounts</u></b>", heading_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(get_all_user_accounts(), body_style))
    elements.append(Spacer(1, 20))

    # ✅ Last Windows Update
    elements.append(Paragraph("<b><u>Last Windows Update</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    updates = get_last_windows_update()

    if updates:
        # Regex split: lookahead for " - KB"
        update_list = re.split(r"(?=\s+-\s+KB)", updates.strip())

        for update in update_list:
            clean_update = update.strip()
            if clean_update:
                elements.append(Paragraph(clean_update, body_style))
    else:
        elements.append(Paragraph("<i>No updates found.</i>", body_style))

    elements.append(Spacer(1, 20))

    # ✅ RDP & Remote Services Section
    elements.append(Paragraph("<b><u>RDP & Remote Services Status</u></b>", heading_style))
    elements.append(Spacer(1, 10))

    # ✅ Fetch service statuses
    remote_services_status = check_remote_services()

    # ✅ Display total count
    num_services = len(remote_services_status)
    elements.append(Paragraph(f"<b>Total Services Checked: {num_services}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_services > 0:
        # ✅ Table Headers
        data = [["S.No", "Service Name", "Status"]]

        # ✅ Add service data
        for i, (service, status) in enumerate(remote_services_status.items(), start=1):
            data.append([str(i), service, status])

        # ✅ Define column widths (Prevent Overflow)
        service_table = Table(data, colWidths=[50, 250, 100])  

        # ✅ Apply Styles
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # ✅ Apply alternating row colors
        for row_idx in range(1, len(data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(service_table)  # Append the table

    else:
        elements.append(Paragraph("<i>No service data available.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Critical Windows Services Section
    elements.append(Paragraph("<b><u>Critical Windows Services Status</u></b>", heading_style))
    elements.append(Spacer(1, 10))

    # ✅ Fetch service statuses
    critical_services_status = check_critical_services()

    # ✅ Display total count
    num_services = len(critical_services_status)
    elements.append(Paragraph(f"<b>Total Services Checked: {num_services}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_services > 0:
        # ✅ Table Headers
        data = [["S.No", "Service Name", "Status"]]

        # ✅ Add service data
        for i, (service, status) in enumerate(critical_services_status.items(), start=1):
            data.append([str(i), service, status])

        # ✅ Define column widths (Prevent Overflow)
        service_table = Table(data, colWidths=[50, 250, 100])  

        # ✅ Apply Styles
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # ✅ Apply alternating row colors
        for row_idx in range(1, len(data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(service_table)  # Append the table

    else:
        elements.append(Paragraph("<i>No service data available.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Desktop Files
    elements.append(Paragraph("<b><u>Desktop Files</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    # Retrieve the desktop file list and count correctly
    desktop_files, file_count = get_desktop_files()

    # Display total number of desktop files first
    elements.append(Paragraph(f"<b>Number of Desktop Files: {file_count}</b>", body_style))
    elements.append(Spacer(1, 5))

    # Ensure desktop_files is properly structured as a list
    if file_count > 0 and isinstance(desktop_files, str):
        desktop_files = desktop_files.split("\n")  # Convert newline-separated text into a list

    # If there are files, format them into a table
    if file_count > 0:
        file_data = [["S.No", "File Name"]]  # Table header

        for i, file in enumerate(desktop_files, start=1):
            file_data.append([str(i), file])  # Ensure proper row structure

        # Define table column widths
        file_table = Table(file_data, colWidths=[50, 400])  

        # Apply styles
        file_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # Apply alternating row colors
        for row_idx in range(1, len(file_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            file_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(file_table)  # Append the fixed table

    else:
        elements.append(Paragraph("<i>No files found on the desktop.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table

    # ✅ USB Device History
    usb_devices = get_usb_history()
    elements.append(Paragraph("<b><u>USB Device Connection History</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    if usb_devices:
        usb_data = [["S.No", "Device Type", "Serial Number", "Friendly Name"]]
    
        for i, device in enumerate(usb_devices, start=1):
            usb_data.append([str(i), device["Device"], device["Serial"], device["FriendlyName"]])

        usb_table = Table(usb_data, colWidths=[50, 150, 150, 150])
    
        usb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header row
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header bold
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Normal font for data
        ]))

        # Apply alternating row colors for readability
        for row_idx in range(1, len(usb_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            usb_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(usb_table)
    else:
        elements.append(Paragraph("<i>No USB storage devices found.</i>", body_style))

    elements.append(Spacer(1, 20))
    
    def format_timestamp(timestamp):
        """Convert Windows Event timestamp to a readable format."""
        try:
            timestamp = timestamp.rstrip("Z")  # ✅ Remove trailing "Z"
        
            if "." in timestamp:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        
            return dt.strftime("%Y-%m-%d %H:%M:%S")  # ✅ Readable format
        except ValueError:
            return timestamp  # Return as is if parsing fails

    # ✅ Smartphone / Dongle Connection History
    smartphones = get_smartphone_dongle_history()
    elements.append(Paragraph("<b><u>Smartphone and Dongle Connection History</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    truncate = lambda text, length=30: text if len(text) <= length else text[:length] + "..."

    if smartphones:
        smartphone_data = [["S.No", "Device", "Vendor", "Type", "Serial Number"]]
        for i, item in enumerate(smartphones, start=1):
            serial_truncated = truncate(item["Serial"])
            smartphone_data.append([
                str(i),
                item["Device"],
                item["Vendor"],
                item["Type"],
                serial_truncated
            ])

        smartphone_table = Table(smartphone_data, colWidths=[40, 130, 80, 100, 180])
        smartphone_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # Alternating row colors
        for row_idx in range(1, len(smartphone_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            smartphone_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(smartphone_table)
    else:
        elements.append(Paragraph("<i>No smartphone or dongle connection traces found.</i>", body_style))

    elements.append(Spacer(1, 20))

    # ✅ Installed Programs
    elements.append(Paragraph("<b><u>Installed Programs</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    installed_programs = get_installed_programs()
    num_programs = len(installed_programs)

    # Display total number of installed programs
    elements.append(Paragraph(f"<b>Total Installed Programs: {num_programs}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_programs > 0:
        # Define wrap style once (outside loop)
        wrap_style = ParagraphStyle(
            name="WrapStyle",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            wordWrap='CJK'  # Ensures long strings wrap even without spaces
        )

        # Prepare the data table with wrapped headers too
        program_data = [
            [Paragraph("<b>S.No</b>", wrap_style),
            Paragraph("<b>Program Name</b>", wrap_style),
            Paragraph("<b>Version</b>", wrap_style)]
        ]

        for i, (name, version) in enumerate(installed_programs, start=1):
            program_data.append([
                Paragraph(str(i), wrap_style),
                Paragraph(name, wrap_style),
                Paragraph(version, wrap_style)
            ])

        # Define table column widths
        program_table = Table(program_data, colWidths=[50, 300, 100])

        # Apply styles
        program_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        # Apply alternating row colors
        for row_idx in range(1, len(program_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            program_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(program_table)

    else:
        elements.append(Paragraph("<i>No installed programs found.</i>", body_style))

    elements.append(Spacer(1, 20))
 
    # ✅ Startup Applications
    elements.append(Paragraph("<b><u>Startup Applications</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    startup_apps = get_startup_programs()
    num_startup_apps = len(startup_apps)

    # Display total number of startup applications
    elements.append(Paragraph(f"<b>Total Startup Applications: {num_startup_apps}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_startup_apps > 0:
        styles = getSampleStyleSheet()
    
        # Prepare the table headers with wrapped text
        startup_data = [
            [
                Paragraph("<b>S.No</b>", styles["Normal"]),
                Paragraph("<b>Application Name</b>", styles["Normal"]),
                Paragraph("<b>Path</b>", styles["Normal"]),
                Paragraph("<b>Source</b>", styles["Normal"]),
            ]
        ]

        # Populate the table with data, ensuring text wrapping
        for i, (name, path, source) in enumerate(startup_apps, start=1):
            startup_data.append([
                Paragraph(str(i), styles["Normal"]),
                Paragraph(name, styles["Normal"]),
                Paragraph(path, styles["Normal"]),  # Wrapped path
                Paragraph(source, styles["Normal"]),
            ])

        # Define table column widths dynamically
        startup_table = Table(startup_data, colWidths=[40, 150, 250, 80])

        # Apply styles to the table
        startup_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align all text left
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Enable grid
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header text
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Normal text font
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top
        ]))

        # Apply alternating row colors for readability
        for row_idx in range(1, len(startup_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            startup_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(startup_table)  # Append the fixed table

    else:
        elements.append(Paragraph("<i>No startup applications found.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table
    
    # ✅ Shared Folders
    elements.append(Paragraph("<b><u>Shared Folders</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    shared_folders = get_shared_folders()
    num_shared_folders = len(shared_folders)

    # Display total number of shared folders
    elements.append(Paragraph(f"<b>Total Shared Folders: {num_shared_folders}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_shared_folders > 0:
        styles = getSampleStyleSheet()

        # Prepare the table headers with wrapped text
        shared_data = [
            [
                Paragraph("<b>S.No</b>", styles["Normal"]),
                Paragraph("<b>Shared Name</b>", styles["Normal"]),
                Paragraph("<b>Local Path</b>", styles["Normal"]),
                Paragraph("<b>Description</b>", styles["Normal"]),
            ]
        ]

        # Populate the table, ensuring text wrapping
        for i, folder in enumerate(shared_folders, start=1):
            shared_data.append([
                Paragraph(str(i), styles["Normal"]),
                Paragraph(folder["Name"], styles["Normal"]),
                Paragraph(folder["Path"], styles["Normal"]),  # Wrapped Path
                Paragraph(folder["Description"], styles["Normal"]),
            ])

        # ✅ FIX: Explicitly set table width and **add left & right margins**
        total_table_width = 400  # ✅ Keep the table **smaller** to ensure margins
        left_margin = 50  # ✅ Left margin space to prevent touching the left side
        right_margin = 50  # ✅ Right margin space to prevent touching the right side

        shared_table = Table(shared_data, colWidths=[40, 100, 150, 110])  # **Reduce column widths**
    
        # ✅ Apply manual left & right margin by adding padding
        shared_table.hAlign = 'LEFT'  # **Left align instead of full width**
        shared_table.spaceAfter = 20  # Space after the table to separate from other content
        
        # Apply styles to the table
        shared_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Enable grid
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold header text
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Normal text font
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top
        ]))

        # Apply alternating row colors for readability
        for row_idx in range(1, len(shared_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            shared_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(shared_table)  # Append the fixed table

    else:
        elements.append(Paragraph("<i>No shared folders found.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Unwanted Software Section
    elements.append(Paragraph("<b><u>Unwanted Software Detection</u></b>", heading_style))
    elements.append(Spacer(1, 10))

    # ✅ Detect unwanted software
    unwanted_software_list = detect_unwanted_software() or []  # ✅ Prevent NoneType error

    # ✅ Display total count
    num_unwanted = len(unwanted_software_list)
    elements.append(Paragraph(f"<b>Total Unwanted Software Found: {num_unwanted}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_unwanted > 0:
        # ✅ Table Headers
        data = [["S.No", "Software Name"]]
        
        # ✅ Add detected software
        for i, software in enumerate(unwanted_software_list, start=1):
            data.append([str(i), software])

        # ✅ Define table column widths (Prevent Overflow)
        unwanted_table = Table(data, colWidths=[50, 400])  

        # ✅ Apply Styles
        unwanted_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # ✅ Apply alternating row colors
        for row_idx in range(1, len(data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            unwanted_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(unwanted_table)  # Append the table

    else:
        elements.append(Paragraph("<i>No unwanted software detected.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table

    # ✅ Log Analysis with Color Coding
    def format_logs_for_pdf(logs):
        if not logs.strip():
            return [("<b>No logs found.</b>", info_style)]

        events = logs.strip().split("Event[")
        formatted_logs = []

        for event in events:
            event = event.strip()
            if event:
                event_lines = event.split("\n")
                event_id = next((line.split(":")[1].strip() for line in event_lines if "Event ID" in line), "Unknown")
                timestamp_raw = next((line.split(":", 1)[1].strip() if ":" in line else "Unknown" for line in event_lines if "Date" in line), "Unknown")
                timestamp = format_timestamp(timestamp_raw)  # ✅ Convert timestamp
                source = next((line.split(":")[1].strip() for line in event_lines if "Source" in line), "Unknown")
                description_lines = []
                capture_description = False

                for line in event_lines:
                    if "Description:" in line:
                        capture_description = True
                        description_lines.append(line.split("Description:", 1)[1].strip())
                    elif capture_description:
                        if line.strip() == "":
                            break  # Stop capturing on an empty line
                        description_lines.append(line.strip())

                description = " ".join(description_lines).strip() if description_lines else "No Description Found"
                
                description = clean_text(description)

                # ✅ Fix: Replace problematic characters for ReportLab
                description = " ".join(description_lines) if description_lines else "No Description Found"
                description = clean_text(description)

                level = next((line.split(":")[1].strip() for line in event_lines if "Level" in line), "Information")

                log_style = error_style if "Error" in level else warning_style if "Warning" in level else info_style
                formatted_logs.append((
                    f"<b>Event ID:</b> {event_id}<br/>"
                    f"<b>Timestamp:</b> {timestamp}<br/>"
                    f"<b>Source:</b> {source}<br/>"
                    f"<b>Description:</b> {description}<br/><br/>", 
                    log_style
                ))

        return formatted_logs

    def add_log_section(title, logs):
        elements.append(Paragraph(f"<b>{title}</b>", heading_style))
        elements.append(Spacer(1, 5))

        log_entries = format_logs_for_pdf(logs)
        list_items = [ListItem(Paragraph(log[0], log[1])) for log in log_entries]
        elements.append(ListFlowable(list_items, bulletType="bullet"))
        elements.append(Spacer(1, 20))

    add_log_section("<u>USB Logs</u>", get_usb_logs())
    add_log_section("<u>Security Logs</u>", get_security_logs())
    add_log_section("<u>System Logs</u>", get_system_logs())
    add_log_section("<u>Application Logs</u>", get_application_logs())
    add_log_section("<u>DNS Logs</u>", get_dns_logs())

    # ✅ End of Report Section (on same page)
    elements.append(Spacer(1, 40))  # Small space before ending text
    elements.append(Paragraph("<b>--- END OF REPORT ---</b>", ParagraphStyle(
        name="EndStyle",
        parent=body_style,
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.darkgray,
        spaceBefore=10,
        spaceAfter=10
    )))
    elements.append(Paragraph("This concludes the Cyber Security Audit Report.", disclaimer_style))

    # ✅ Save the PDF
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"✅ PDF Report Generated: {filename}")
    
def calculate_security_score():
    score = 100
    deductions = []
    password_status = get_password_policy_status()
    lockout_status = get_lockout_policy_status()
    firewall_status = get_firewall_status()
    antivirus_status = get_antivirus_status()
    scan_time = get_last_scan_time()
    default_share_status = get_default_share_status()
    shared_folders = get_shared_folders()
    rdp_status = get_rdp_status()
    telnet_status = get_telnet_status()
    remote_services = check_remote_services()
    usb_access = get_usb_device_control_status()
    autoplay_status = get_autoplay_status()
    pnp_status = get_plug_and_play_status()

    # Password policy scoring
    if "Weak" in password_status:
        score -= 15
        deductions.append(("Weak Password Policy", -15))
    elif "Partial" in password_status:
        score -= 7
        deductions.append(("Partial Password Policy", -7))

    # Lockout policy scoring
    if "No Lockout" in lockout_status:
        score -= 10
        deductions.append(("No Lockout Policy Configured", -10))

    if "May Be Set" in get_bios_password_status():
        score -= 5
        deductions.append(("BIOS Password Not Set", -5))

    if "No Windows Login Password" in get_login_password_status():
        score -= 10
        deductions.append(("Login Without Password Allowed", -10))

    if "Passwords Saved" in check_saved_passwords():
        score -= 5
        deductions.append(("Saved Browser/System Passwords Detected", -5))

    # 🧱 Firewall & Antivirus
    disabled_count = firewall_status.count("Disabled")

    if disabled_count > 0:
        score -= 5 * disabled_count  # max 15 points
        deductions.append((f"{disabled_count} Firewall Profile(s) Disabled", -5 * disabled_count))

    if "windows defender" in antivirus_status.lower() and "," not in antivirus_status:
        score -= 5
        deductions.append(("Only Windows Defender Found", -5))

    try:
        # Handle raw datetime string like "4/13/2025 9:40:00 PM"
        scan_dt = datetime.strptime(scan_time, "%m/%d/%Y %I:%M:%S %p")
        delta_days = (datetime.now() - scan_dt).days

        if delta_days > 10:
            score -= 3
            deductions.append((f"Windows Defender Scan Older than 10 Days ({delta_days} days)", -3))

    except:
        if "Passive Mode" in scan_time:
            deductions.append(("Windows Defender is in Passive Mode (Another AV active)", 0))
        elif "inactive" in scan_time.lower() or "not scanning" in scan_time.lower():
            score -= 3
            deductions.append(("Windows Defender Inactive or Not Scanning", -3))
        else:
            # Could not parse, don't deduct but log it
            deductions.append(("Unable to determine Windows Defender scan age", 0))

    # 📁 Network & Sharing
    if default_share_status.startswith("Enabled"):
        score -= 10
        deductions.append(("Default Share Enabled", -10))
    elif "Error" in default_share_status:
        deductions.append(("Could not determine Default Share Status", 0))

    if len(shared_folders) > 0:
        score -= 5
        deductions.append(("Shared Folders Detected", -5))
    
    # 💻 Remote Access
    if rdp_status.startswith("Enabled"):
        score -= 10
        deductions.append(("RDP Enabled", -10))
    elif "Error" in rdp_status or "unknown" in rdp_status.lower():
        deductions.append(("Unable to determine RDP status", 0))

    if telnet_status.startswith("Enabled"):
        score -= 10
        deductions.append(("Telnet Enabled", -10))
    elif "Not Installed" in telnet_status:
        deductions.append(("Telnet is not installed (Safe)", 0))
    elif "Disabled" in telnet_status:
        deductions.append(("Telnet is Disabled", 0))
    elif "unknown" in telnet_status.lower():
        deductions.append(("Telnet status unknown", 0))

    #Remote Services
    risky_services = [name for name, status in remote_services.items() if status.strip().lower() == "running"]

    if len(risky_services) > 0:
        penalty = min(3 * len(risky_services), 15)
        score -= penalty
        deductions.append((f"{len(risky_services)} Remote Services Running", -penalty))
    
    # 🚨 Critical Services Check
    critical_services = check_critical_services()

    # 🚨 Essential Critical Services Check (only the truly must-run ones)
    # ✅ Must be running
    essential_services_should_run = [
        "DNS Client",
        "RPC Endpoint Mapper",
        "Remote Procedure Call (RPC)"
    ]

    # ❌ Must NOT be running
    services_should_be_stopped = [
        "Remote Desktop Services",
        "Telnet Client",
        "Remote Registry",
        "Routing and Remote Access",
        "Remote Access Auto Connection Manager",
        "Remote Access Connection Manager",
        "Distributed Transaction Coordinator",
        "OpenSSH Authentication Agent",
        "Remote Desktop Configuration",
        "Problem Reports Control Panel Support"
    ]

    # ✅ Must be running
    problem_services_missing = [
        svc for svc in essential_services_should_run
        if critical_services.get(svc, "").strip().lower() != "running"
    ]
    if problem_services_missing:
        penalty = min(3 * len(problem_services_missing), 10)
        score -= penalty
        deductions.append((f"{len(problem_services_missing)} Essential Services Not Running", -penalty))

    # ❌ Should be stopped
    problem_services_running = [
        svc for svc in services_should_be_stopped
        if critical_services.get(svc, "").strip().lower() == "running"
    ]
    if problem_services_running:
        penalty = min(2 * len(problem_services_running), 10)
        score -= penalty
        deductions.append((f"{len(problem_services_running)} Insecure Services Running", -penalty))

    # 🔌 USB
    if usb_access.startswith("USB Access: Allowed"):
        score -= 5
        deductions.append(("USB Storage Access Allowed", -5))
    elif "Error" in usb_access or "Status" in usb_access:
        deductions.append(("Unable to determine USB access status", 0))

    #autoplay
    if autoplay_status.startswith("AutoPlay is Enabled"):
        score -= 3
        deductions.append(("AutoPlay Enabled", -3))
    elif "unknown" in autoplay_status.lower() or "error" in autoplay_status.lower():
        deductions.append(("Unable to determine AutoPlay status", 0))

    # 🌐 Open Ports
    open_ports = get_open_ports()
    open_tcp = open_ports["tcp"]
    udp_services = open_ports["udp"]

    # Filter real TCP ports (exclude 'No open...' or 'Error' messages)
    actual_tcp = [p for p in open_tcp if "port" in p.lower()]
    if len(actual_tcp) >= 4:
        score -= 10
        deductions.append((f"{len(actual_tcp)} TCP Ports Open", -10))

    # Filter real UDP services (exclude 'No active...' or 'Error' messages)
    actual_udp = [p for p in udp_services if "port" in p.lower()]
    if len(actual_udp) > 0:
        score -= 5
        deductions.append((f"{len(actual_udp)} UDP Services Running", -5))

    # ⚙️ System Info
    if "Manual Start" in pnp_status or "Automatic Start" in pnp_status:
        score -= 5
        deductions.append(("Plug and Play is Enabled — Must be Disabled", -5))
    elif "Disabled" in pnp_status:
        deductions.append(("Plug and Play is Properly Disabled", 0))
    elif "Error" in pnp_status or "Unknown" in pnp_status:
        deductions.append(("Unable to determine Plug and Play status", 0))

    # 🗑️ Clutter & Startup
    _, file_count = get_desktop_files()
    if file_count > 50:
        score -= 2
        deductions.append((f"Desktop Files Found ({file_count})", -2))

    unwanted_software_list = detect_unwanted_software() or []
    if len(unwanted_software_list) >= 3:
        score -= 5
        deductions.append((f"Unwanted Programs Detected ({len(unwanted_software_list)})", -5))

    startup_apps = get_startup_programs()
    if len(startup_apps) > 8:
        score -= 3
        deductions.append((f"Startup Apps Detected ({len(startup_apps)})", -3))

    # ✅ Optional Hybrid: Cap total deduction at 100 for final score
    raw_penalty = sum(abs(penalty) for _, penalty in deductions)
    score = max(100 - min(raw_penalty, 100), 0)
    return score, deductions

def add_security_score_section(elements):
    score, deductions = calculate_security_score()

    if score >= 85:
        status = "Secure"
        color = colors.green
    elif score >= 70:
        status = "Moderately Secure"
        color = colors.orange
    elif score >= 50:
        status = "At Risk"
        color = colors.darkorange
    else:
        status = "Vulnerable"
        color = colors.red

    # Header
    elements.append(Paragraph("<b><u>Cyber Security Health Score</u></b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    # Score Box
    score_table = Table(
        [[f"Score: {score} / 100", f"Status: {status}"]],
        colWidths=[200, 200]
    )
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 15))

    # Breakdown Table
    if deductions:
        elements.append(Paragraph("<b>Score Deductions:</b>", styles["Heading3"]))
        data = [["Issue", "Penalty"]]
        for reason, penalty in deductions:
            data.append([reason, f"{penalty}"])

        table = Table(data, colWidths=[350, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # ✅ Alternate row colors
        for row_idx in range(1, len(data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        # Recommendations
        elements.append(Paragraph("<b>Recommended Actions:</b>", styles["Heading3"]))
        suggestions = set()

        for reason, _ in deductions:
            suggestion = ""

            if "Password Policy" in reason:
                suggestion = "Enforce strong password policy requirements."
            elif "BIOS Password" in reason:
                suggestion = "Set a BIOS password to prevent unauthorized boot changes."
            elif "Windows Defender" in reason:
                suggestion = "Install a more robust antivirus solution."
            elif "Firewall" in reason:
                suggestion = "Enable Windows Firewall for system protection."
            elif "Default Share" in reason:
                suggestion = "Disable default administrative shares."
            elif "Shared Folders" in reason:
                suggestion = "Review and restrict shared folders."
            elif "Telnet" in reason:
                suggestion = "Disable Telnet – it is insecure."
            elif "USB" in reason:
                suggestion = "Restrict USB storage device access."
            elif "AutoPlay" in reason:
                suggestion = "Disable AutoPlay to prevent malware execution."
            elif "TCP Ports" in reason:
                suggestion = "Close unnecessary open TCP ports."
            elif "Geo-Location" in reason:
                suggestion = "Turn off geo-location tracking if unnecessary."
            elif "Plug and Play" in reason:
                suggestion = "Ensure Plug and Play service is set to Automatic."
            elif "Essential Services Not Running" in reason:
                suggestion = "Ensure essential system services like DNS Client and RPC are running."
            elif "Insecure Services Running" in reason:
                suggestion = "Stop insecure services that expose the system to risk (e.g., Telnet, Remote Registry, etc.)."
            elif "Startup Apps" in reason:
                suggestion = "Disable excessive startup apps to improve performance."

            if suggestion:
                suggestions.add(suggestion)

        # ✅ Now add only unique suggestions
        for s in sorted(suggestions):
            elements.append(Paragraph(f"• {s}", styles["Normal"]))

    elements.append(Spacer(1, 20))
    
# ✅ Run the script
if __name__ == "__main__":
    generate_pdf_report()
