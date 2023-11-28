from reportlab.platypus import Paragraph,  Image, Table,  HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os 

class PDF_STYLE:
    def __init__(self):
        pdfmetrics.registerFont(TTFont("Soehne-Kraeftig", os.path.join(os.path.dirname(__file__), 'TTF_fonts', 'Soehne-Kraeftig.ttf')))
        pdfmetrics.registerFont(TTFont("Soehne-Buch", os.path.join(os.path.dirname(__file__), 'TTF_fonts', 'Soehne-Buch.ttf')))
        pdfmetrics.registerFont(TTFont("Soehne-BuchKursiv", os.path.join(os.path.dirname(__file__), 'TTF_fonts', 'Soehne-BuchKursiv.ttf')))
        
        registerFontFamily('Soehne-Buch',normal='Soehne-Buch',bold='Soehne-Kraeftig',italic='Soehne-BuchKursiv',boldItalic='Soehne-BuchKursiv') 
        
        pdfmetrics.registerFont(TTFont('CourierNew', os.path.join(os.path.dirname(__file__), 'TTF_fonts', 'COUR.TTF')))
        pdfmetrics.registerFont(TTFont('CourierNewBold', os.path.join(os.path.dirname(__file__), 'TTF_fonts', 'COURBD.ttf')))
        registerFontFamily('CourierNew',normal='CourierNew',bold='CourierNewBold',italic='Soehne-BuchKursiv',boldItalic='Soehne-BuchKursiv')
        
        self.styles = getSampleStyleSheet()
        
        self.title_style = ParagraphStyle('normal_style', 
                                          self.styles['Heading1'], 
                                          fontName='Soehne-Kraeftig') 
        self.title_style_c = ParagraphStyle('title_style', 
                                            parent=self.styles['Heading1'], 
                                            alignment=1, 
                                            fontName='Soehne-Kraeftig') 
        self.sub_style = ParagraphStyle('sub_style', 
                                            parent=self.styles['Heading2'], 
                                            fontName='Soehne-Kraeftig') 
        self.comp_style = ParagraphStyle("CustomStyle", 
                                         parent=self.styles['Heading2'],
                                         leftIndent=20, 
                                         fontName='Soehne-Kraeftig')
        self.normal_style = ParagraphStyle('normal_style', 
                                           self.styles['Normal'], 
                                           fontName='Soehne-Buch')
        self.normal_style_c = ParagraphStyle('normal_style', 
                                             parent=self.styles['Normal'],
                                             alignment=1, 
                                             fontName='Soehne-Buch')
        self.custom_style = ParagraphStyle("CustomStyle",
                                           parent=self.styles['Normal'],
                                           leftIndent=20, 
                                           fontName='Soehne-Buch')
        self.italic_style = ParagraphStyle("italicStyle",
                                           parent=self.styles['Italic'],
                                           leftIndent=20, 
                                           fontName='Soehne-BuchKursiv')
        self.courier_new_white = ParagraphStyle('indented_style',
                                        parent=self.styles['Normal'],
                                        textColor=colors.white,
                                        leftIndent=20,
                                        fontName='CourierNew')
        self.courier_new_green = ParagraphStyle('green_style',
                                        parent=self.styles['Normal'],
                                        textColor=colors.green,
                                        fontSize=24,
                                        fontName='CourierNew',
                                        alignment=2
                                        )
        
        logo_path = os.path.join(os.path.dirname(__file__), 'media', 'supernova-logo.png')
        self.logo = Image(logo_path, width=105, height=25) 
        logo_path2 = os.path.join(os.path.dirname(__file__), 'media', 'verified.jpg')
        self.logo2 = Image(logo_path2, width=240, height=53, hAlign='RIGHT') 
        
        self.topright = "placeholder"
        self.bottomright = "placeholder"
        self.middleright = "placeholder"
        self.bottomleft = "placeholder"
        
        self.horizontal_line = HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey)
    
    
    def onFirstPage(self, canvas, document):            
        
        table_data = [
            [self.logo, self.topright],
            [self.bottomleft, self.middleright],
            ['', self.bottomright]]
        
        table = Table(table_data, colWidths=[250, 390], rowHeights=52)
        table.setStyle([
            ('FONT', (0,0), (-1,-1), 'Soehne-Kraeftig'), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('SPAN',(0,-1),(0,-2)),
            ('LEFTPADDING', (0,0), (-1,-1), 75),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.lightgrey),
        ])
        table.wrapOn(canvas, 300, 800)
        table.drawOn(canvas, 0, 685)
        

    def onLaterPages(self, canvas, document):
        # Draw a header on later pages
        header = Table([[self.logo, self.topright]], colWidths=[250, 390], rowHeights=80)
        header.setStyle([
            ('FONT', (0,0), (-1,-1), 'Soehne-Kraeftig'), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('LEFTPADDING', (0,0), (-1,-1), 75),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.lightgrey),
        ])
        header.wrapOn(canvas, 300, 400)
        header.drawOn(canvas, 0, 765)
        
    def calculation_table(self, text):
        text_ = Paragraph(text, self.courier_new_white)
        
        # Create table with black background
        table_data = [[text_]]
        table = Table(table_data, cornerRadii=[3,3,3,3])
        table.setStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
            ('BACKGROUND', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white)
        ])
        return table 
    
    def entity_reporting_period(self, metricValue):
        self.metricValue = metricValue
        if self.metricValue:
            if isinstance(self.metricValue['reporting_period'], list):
                period = "<b>For the reporting period: </b>" + ' - '.join(self.metricValue['reporting_period']) 
            elif isinstance(self.metricValue['reporting_period'], str):
                period = "<b>For the reporting period: </b>" + self.metricValue['reporting_period']
            else: period = "Missing data"
            return period
    