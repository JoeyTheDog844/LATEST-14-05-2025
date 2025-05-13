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
from usb_devices_list import get_usb_history
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
        "1. System Information",
        "2. Network Details",
        "3. Security Information",
        "4. Users Accounts",
        "5. Last Windows Update",
        "6. RDP & Remote Services",
        "7. Critical Windows Services",
        "8. Desktop Files",
        "9. USB Device Connection History",
        "10. Installed Programs",
        "11. Startup Applications",
        "12. Shared Folders",
        "13. Unwanted Softwares",
        "14. Logs"
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
    
    # ✅ Installed Programs
    elements.append(Paragraph("<b><u>Installed Programs</u></b>", heading_style))
    elements.append(Spacer(1, 5))

    installed_programs = get_installed_programs()
    num_programs = len(installed_programs)

    # Display total number of installed programs
    elements.append(Paragraph(f"<b>Total Installed Programs: {num_programs}</b>", body_style))
    elements.append(Spacer(1, 5))

    if num_programs > 0:
        # Prepare the data table
        program_data = [["S.No", "Program Name", "Version"]]

        for i, (name, version) in enumerate(installed_programs, start=1):
            program_data.append([str(i), name, version])

        # Define table column widths
        program_table = Table(program_data, colWidths=[50, 300, 100])

        # Apply styles
        program_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))

        # Apply alternating row colors
        for row_idx in range(1, len(program_data)):
            bg_color = colors.lightgrey if row_idx % 2 == 0 else colors.white
            program_table.setStyle(TableStyle([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ]))

        elements.append(program_table)  # Append the table

    else:
        elements.append(Paragraph("<i>No installed programs found.</i>", body_style))

    elements.append(Spacer(1, 20))  # Space after table
    
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
    
# ✅ Run the script
if __name__ == "__main__":
    generate_pdf_report()
