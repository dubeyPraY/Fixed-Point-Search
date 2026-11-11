"""Build Codes/companion.pdf from its editable Markdown source."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]


def build():
    styles = {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=21, leading=26,
                                textColor=colors.HexColor('#18364b'), spaceAfter=17),
        'heading': ParagraphStyle('heading', fontName='Helvetica-Bold', fontSize=12, leading=16,
                                  textColor=colors.HexColor('#18364b'), spaceBefore=10, spaceAfter=6),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14.2, spaceAfter=8),
        'cell': ParagraphStyle('cell', fontName='Helvetica', fontSize=8.5, leading=11),
    }
    story = []
    blocks = (ROOT/'Codes/companion.md').read_text(encoding='utf-8').strip().split('\n\n')
    for block in blocks:
        if block == '---':
            story.append(PageBreak())
        elif block.startswith('|'):
            rows = [[Paragraph(escape(cell.strip()), styles['cell'])
                     for cell in line.strip().strip('|').split('|')] for line in block.splitlines()]
            table = Table(rows, colWidths=[61, 57, 62, 145, 145], repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eff4')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LINEBELOW', (0,0), (-1,0), .6, colors.HexColor('#8099aa')),
                ('LINEBELOW', (0,1), (-1,-1), .3, colors.HexColor('#d2dce3')),
            ]))
            story.extend([table, Spacer(1, 10)])
        else:
            style = 'title' if block.startswith('# ') else 'heading' if block.startswith('## ') else 'body'
            content = block[2:] if style == 'title' else block[3:] if style == 'heading' else block
            story.append(Paragraph(escape(content), styles[style]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#ccd6de'))
        canvas.line(52, 43, A4[0]-52, 43)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#506779'))
        canvas.drawString(52, 30, 'Fixed-point search | Reference manuscript: 11 November 2026')
        canvas.drawRightString(A4[0]-52, 30, str(doc.page))
        canvas.restoreState()

    output = ROOT/'Codes/companion.pdf'
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=52, leftMargin=52,
                      topMargin=44, bottomMargin=57,
                      title='A guide to ancilla-mediated fixed-point search',
                      author='Fixed-point search repository').build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == '__main__':
    build()
