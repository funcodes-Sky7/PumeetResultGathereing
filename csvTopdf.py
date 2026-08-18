import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def convert_csv_to_pdf(csv_filename="student_details.csv", pdf_filename="student_report.pdf"):
    # Check karna ki CSV file exist karti hai ya nahi
    if not os.path.exists(csv_filename):
        print(f"Error: Mujhko '{csv_filename}' file nahi mili! Pehle file ko isi folder mein rakhein.")
        return

    # PDF Document setup (30pt margins)
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Header Style
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    # Table Column Headers Style
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    # Inside Cell/Text Style
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )
    
    story = []
    story.append(Paragraph("Student Academic & Branch Allocation Report", title_style))
    story.append(Spacer(1, 10))
    
    table_data = []
    
    # CSV File ko Open aur Read karne ka engine
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        # Pehli line (Headers) ko read karna
        try:
            headers = next(csv_reader)
            table_data.append([Paragraph(h, header_style) for h in headers])
        except StopIteration:
            print("Error: Di gayi CSV file bilkul khali hai.")
            return
            
        # Baaki saari data rows ko read aur process karna
        for row in csv_reader:
            if not row: # Khali rows ko skip karne ke liye
                continue
            table_data.append([Paragraph(cell, cell_style) for cell in row])
        
    # Column Widths Setup (Total alignment: 552 points, fits letter page)
    # Roll No (60), Name (150), Father Name (150), Marks (50), Rank (40), Branch (70)
    data_table = Table(table_data, colWidths=[60, 150, 150, 50, 40, 70], repeatRows=1)
    
    # Table Styling
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
    ]))
    
    story.append(data_table)
    
    # PDF Rendering Execution
    doc.build(story)
    print(f"Success! Aapki PDF kamyaabi se ban gayi hai: {pdf_filename}")

if __name__ == "__main__":
    # Agar aapki file ka naam kuch aur hai, toh yahan change karein:
    convert_csv_to_pdf(csv_filename="student_details.csv", pdf_filename="student_details_sorted_with_branches.pdf")