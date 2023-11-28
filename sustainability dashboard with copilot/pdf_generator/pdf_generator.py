from utils.db import db
from bson.objectid import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from io import BytesIO
import logging
from pdf_generator.pdf_style import PDF_STYLE
from api_orion import BASE
from datatools.google_cloud_storage import GoogleCloudStorage

class ENTITTY_PDF(PDF_STYLE):
    def __init__(self, metricValue_id):
        super().__init__()
        self.metricValue_id = metricValue_id
        self.metricValue = db.metricValues.find_one({'_id': ObjectId(self.metricValue_id)})
        if self.metricValue: 
            self.metricMeta_id = self.metricValue['metric_meta_link']
            self.metricMeta = db.metricMeta.find_one({'_id': ObjectId(self.metricMeta_id)}, {'embeddings':0})
            self.company_id = self.metricValue['company_link']
            self.company = db.companies.find_one({'_id': ObjectId(self.company_id)})
        
        if self.metricValue and self.metricMeta and self.metricValue and self.company:
            logging.info("It found the metricValue %s and metricMeta %s on mongodb", str(self.metricValue_id), str(self.metricMeta_id))
            self.topright = Paragraph(f"<b>For company:</b> {self.company['title']}<br/>", self.normal_style)
            self.middleright = Paragraph(f"<b>ID:</b> {self.company['_id']}", self.normal_style)
            self.bottomright = Paragraph(f"<b>Reporting period: </b>{self.entity_reporting_period(self.metricValue)}", self.normal_style)
            self.bottomleft = Paragraph(f"PROOF <br/>DOCUMENT", self.title_style) # <br/>{self.metricMeta['title']}
    
            
    def entity_pdf(self):
        # Create a new document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=90)
        
        elements: list[Flowable] = [Spacer(1, 75)] 
        
        if self.metricValue is None:
            elements.append(Paragraph(f"The metricValue {self.metricValue_id} does not seem to exist on our database.", self.italic_style))
        elif self.metricMeta is None:
            elements.append(Paragraph(f"The metricMeta {self.metricMeta_id} does not seem to exist on our database.", self.italic_style))
        elif self.company is None:
            elements.append(Paragraph(f"The company {self.company_id} does not seem to exist on our database.", self.italic_style))
        else:
            # indicator description
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('INDICATOR', self.sub_style))
            elements.append(Paragraph(self.metricMeta['title'], self.comp_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Definition</b><br/>{self.metricMeta['description']}",self.normal_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Usage Guidance</b><br/>{self.metricMeta['Usage Guidance']}",self.normal_style))
            elements.append(Spacer(1, 5))
            if 'Calculation' in self.metricMeta.keys():
                elements.append(Paragraph(f"<b>Calculation</b><br/>{self.metricMeta['Calculation']}", self.normal_style))
                elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Footnote</b><br/>{self.metricMeta['Footnote']}", self.normal_style))
            elements.append(Spacer(1, 5))
            
            # metric url
            metric_url = BASE + f"/library/{str(self.metricMeta_id)}"
            elements.append(Paragraph(f"<u><link href={metric_url}>Read more on the metric</link></u>", self.custom_style))
            
            # companies
            elements.append(Spacer(1, 15))  
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('COMPANY', self.sub_style))
            elements.append(Spacer(1, 5))
            
            elements.append(Paragraph(self.company['title'], self.comp_style))
                            
            companyValue = '<b>Value: </b>' + str(self.metricValue['value']) if self.metricValue else "No value"
            
            if 'unit' in self.metricValue.keys():
                unit = str(self.metricValue['unit']) 
            else: 
                unit = "(no unit specified)"
            
            period = self.entity_reporting_period(self.metricValue)
                                    
            elements.append(Paragraph(f"{companyValue} {unit} <br/><br/> {period}", self.custom_style))
            
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('CALCULATION', self.sub_style))
            elements.append(Spacer(1, 5))
            if 'description' in self.metricValue.keys():
                calculation = f"{self.metricValue['description']}<br/>" # + f" = {str(self.metricValue['value'])}"
            else: calculation = "Calculation not provided."
            elements.append(self.calculation_table(calculation))
            
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('SUPPORTING DOCUMENTS', self.sub_style))
            elements.append(Spacer(1, 5))
            if 'proof_file' in self.metricValue.keys():
                proof_store = GoogleCloudStorage()
                bucket = proof_store.storage_client.bucket("media")
                list_of_urls = self.metricValue['proof_file']
                if isinstance(list_of_urls, list):
                    for url_dict in list_of_urls:      
                        blob_name = bucket.blob(url_dict['name'])
                        url = proof_store.generate_signed_url(blob_name)
                        name = url_dict['originalName']
                        elements.append(Paragraph(f"<u><link href={url}>{name}</link></u>", self.custom_style))
                        elements.append(Spacer(1, 5))
                else: 
                    logging.warning(f"{self.metricValue['proof_file']} is not a list")
            else: elements.append(Paragraph("No proof submitted", self.custom_style))
            
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('CERTIFICATION', self.sub_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("This document has been electronically generated using tested and verified algorithms.", self.custom_style))
            elements.append(Spacer(1, 15))
            # elements.append(Paragraph("VERIFIED", self.courier_new_green))
            elements.append(self.logo2)
            
        # Build the PDF
        doc.build(elements, onFirstPage=self.onFirstPage, onLaterPages=self.onLaterPages)
        buffer.seek(0)
        return buffer

class AGGREGATE_PDF(PDF_STYLE):
    def __init__(self, metricMeta_id, exchange_id):
        super().__init__()
        self.metricMeta_id = metricMeta_id
        self.exchange_id = exchange_id
        self.exchange = db.exchange.find_one({'_id': ObjectId(self.exchange_id)})
        self.metricMeta = db.metricMeta.find_one({'_id': ObjectId(self.metricMeta_id)}, {'embeddings':0})
        if self.exchange:
            self.fund_id = self.exchange['fund_link']
            self.fund = db.funds.find_one({'_id': ObjectId(self.fund_id)})
        
        if self.exchange and self.metricMeta and self.fund:
            logging.info("It found the request %s and metricMeta %s on mongodb", str(self.exchange_id), str(self.metricMeta_id))
            self.topright = Paragraph(f"<b>Your fund:</b> {self.fund['title']}<br/><b>ID:</b> {self.exchange['fund_link']}", self.normal_style)
            self.bottomright = Paragraph(f"<b>Reporting period: </b>{' - '.join(self.exchange['reporting_period'])}<br/>", self.normal_style)
            self.middleright = Paragraph(f"<b>Deadline:</b> {self.exchange['deadline']}", self.normal_style)
            self.bottomleft = Paragraph(f"CALCULATION CERTIFICATE", self.title_style) # <br/>{self.metricMeta['title']}
     
    def aggregate_sum(self):
        sum = 0
        if self.exchange:
            for comp in self.exchange['companies']:
                entitity_id = comp['company_link']
                if self.metricMeta_id in comp['requested_metrics']:
                        metricValue = db.metricValues.find_one({'company_link': entitity_id})
                        if metricValue:
                            sum += float(metricValue['value'])
            return sum
    
    def weighted_average(self, percentages, sizes):
        weighted_sum = sum(p * n for p, n in zip(percentages, sizes))
        total_size = sum(sizes)
        return weighted_sum / total_size if total_size else 0    
    
    def aggregation_type(self):
        """needs to be another loop, as I need to check ALL metricValues"""
        return self.aggregate_sum()
        
        for metricValue in db.metricValues.find():
            if metricValue:
                if 'aggregation_type' in metricValue.keys():
                    if metricValue['aggregation_type'] == 'weighted average':
                        percentages = NotImplemented
                        sizes = NotImplemented
                        return self.weighted_average(percentages, sizes)
            else: return self.aggregate_sum()
    
    def aggregate(self):
        # Create a new document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=90)
        
        elements: list[Flowable] = [Spacer(1, 75)]
        
        if self.exchange is None:
            elements.append(Paragraph(f"The exchange {self.exchange} does not seem to exist on our database.", self.italic_style))
        elif self.metricMeta is None:
            elements.append(Paragraph(f"The metricMeta {self.metricMeta} does not seem to exist on our database.", self.italic_style))
        else:
            sum = self.aggregation_type()
            
            # elements.append(Spacer(1, 15))                
            elements.append(Paragraph(f"Value {sum} MtCO2eq", self.title_style_c))
            
            elements.append(Spacer(1, 5))
            
            elements.append(self.horizontal_line)
            
            # indicator description
            elements.append(Paragraph(self.metricMeta['title'], self.comp_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Definition</b><br/>{self.metricMeta['description']}",self.normal_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<b>Usage Guidance</b><br/>{self.metricMeta['Usage Guidance']}",self.normal_style))
            elements.append(Spacer(1, 5))
            if 'Calculation' in self.metricMeta.keys():
                elements.append(Paragraph(f"<b>Calculation</b><br/>{self.metricMeta['Calculation']}", self.normal_style))
                elements.append(Spacer(1, 5))

            elements.append(Paragraph(f"<b>Footnote</b><br/>{self.metricMeta['Footnote']}", self.normal_style))
            
            # metric url
            elements.append(Spacer(1, 5))
            metric_url = BASE + f"/library/{str(self.metricMeta_id)}"
            elements.append(Paragraph(f"<u><link href={metric_url}>Read more on the metric</link></u>", self.custom_style))
            
            # companies
            elements.append(Spacer(1, 15))  
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15))
            elements.append(Paragraph('COMPANIES', self.sub_style))
            elements.append(Spacer(1, 5))
            
            valuelist = []
            
            # loop over the companies in the request
            for comp in self.exchange['companies']:
                entitity_id = comp['company_link']
                company = db.companies.find_one({'_id': ObjectId(entitity_id)})
                
                if company:
                    elements.append(Paragraph(company['title'], self.comp_style))
                    
                    # if the company in the request has the metric, take the value
                    if self.metricMeta_id in comp['requested_metrics']:
                        metricValue = db.metricValues.find_one({'company_link': entitity_id})
                        
                        if metricValue:
                            companyValue = '<b>Value: </b>' + str(metricValue['value']) if metricValue else "No value"
                            if 'unit' in metricValue.keys():
                                unit = str(metricValue['unit']) 
                            else: 
                                unit = "(no unit specified)"
                                
                            
                            period = self.entity_reporting_period(metricValue)
                            elements.append(Paragraph(f"{companyValue} {unit} <br/><br/> {period}", self.custom_style))
                            
                            # url = BASE + f"/api/v1/entity_pdf_get/{self.metricMeta_id}" 
                            
                            # elements.append(Paragraph(f"<u><link href={url}>Read more on entity-level calculation here</link></u>", self.custom_style))
                            
                            if metricValue: 
                                valuelist.append(str(metricValue['value'])) 
                        else: 
                            elements.append(Paragraph(f"The metricValue for company with ID {entitity_id} does not seem to exist on our database.", self.italic_style))
                else: 
                    elements.append(Paragraph(f"The company with ID {entitity_id} does not seem to exist on our database.", self.comp_style))
                    continue 
            
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('CALCULATION', self.sub_style))
            elements.append(Spacer(1, 5))
            calculation = " + ".join(valuelist) + f" = {sum}" # "Aggregation method: UNWEIGHTED SUM <br/>" 
            elements.append(self.calculation_table(calculation))

            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('CERTIFICATION', self.sub_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("This document has been electronically generated using tested and verified algorithms.", self.custom_style))
            elements.append(Spacer(1, 15))
            # elements.append(Paragraph("VERIFIED", self.courier_new_green))
            elements.append(self.logo2)
            
        doc.build(elements, onFirstPage=self.onFirstPage, onLaterPages=self.onLaterPages)
        buffer.seek(0)
        return buffer

class DATA_REQUEST(PDF_STYLE):
    def __init__(self, exchange_id):
        super().__init__()
        self.exchange_id = exchange_id
        self.exchange = db.exchange.find_one({'_id': ObjectId(self.exchange_id)})
        
        if self.exchange:
            self.fund_id = self.exchange['fund_link']
            self.fund = db.funds.find_one({'_id': ObjectId(self.fund_id)})
            logging.info("It found the request %s and fund %s on mongodb", str(self.exchange_id), str(self.fund_id))
            if self.fund:
                self.topright = Paragraph(f"<b>Your fund:</b> {self.fund['title']}<br/><b>ID:</b> {self.exchange['fund_link']}", self.normal_style)
                self.bottomright = Paragraph(f"<b>Reporting period: </b>{' - '.join(self.exchange['reporting_period'])}<br/>", self.normal_style)
                self.middleright = Paragraph(f"<b>Deadline:</b> {self.exchange['deadline']}", self.normal_style)
                self.bottomleft = Paragraph(f"DATA REQUEST", self.title_style) 

    def data_request(self):      
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=90)
        elements: list[Flowable] = [Spacer(1, 75)]
        
        if self.exchange is None:
            elements.append(Paragraph(f"The exchange {self.exchange_id} does not seem to exist on our database.", self.italic_style))
            
        elif self.fund is None:
            elements.append(Paragraph(f"The fund {self.fund_id} does not seem to exist on our database.", self.italic_style))
        else:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph('DESCRIPTION', self.sub_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph('This is a detailed overview of the request you have compiled for the companies in your fund. Read carefully before sending out. In case you have any questions, contact your Supernova reporting expert.', self.custom_style))
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15)) 
            elements.append(Paragraph('ENTITIES', self.sub_style))
            
            company_list = []
            broken_company_list = []
            metric_list = []  
            broken_id_list = []                  
            for comp in self.exchange['companies']:
                entitity_id = comp['company_link']
                company_ = db.companies.find_one({'_id': ObjectId(entitity_id)})
                if company_:
                    company_list.append(company_['title'])
                else: 
                    broken_company_list.append(entitity_id)
                
                for req_met in range(len(comp['requested_metrics'])):
                    metric_id = comp['requested_metrics'][req_met]
                    m = db.metricMeta.find_one({'_id': ObjectId(metric_id)}, {'embeddings':0})
                    if m and m not in metric_list:
                        metric_list.append(m)
                    elif m is None:
                        print(metric_id, "is broken")
                        broken_id_list.append(metric_id)
            
            elements.append(Paragraph(", ".join(company_list), self.custom_style))
                                    
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15))            
            elements.append(Paragraph('INDICATORS', self.sub_style)) 
            elements.append(Spacer(1, 5))
                            
            for metric in metric_list:
                elements.append(Paragraph(metric['title'], self.comp_style))
                elements.append(Paragraph(metric['description'], self.custom_style))
                if metric.get('Usage guidance', {}):
                    elements.append(Paragraph(metric['Usage guidance'], self.custom_style))
                    elements.append(Paragraph(metric['footnote'], self.custom_style))
                elements.append(Spacer(1, 5))
                
                # metric url
                metric_url = BASE + f"/library/{str(metric['_id'])}"
                elements.append(Paragraph(f"<u><link href={metric_url}>Read more on the metric</link></u>", self.custom_style))
               
            elements.append(Spacer(1, 15))    
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15))
            
            if broken_company_list or broken_id_list:
                elements.append(Spacer(1, 15))
                elements.append(Paragraph('ERRORS', self.sub_style)) 
                if broken_company_list:
                    elements.append(Paragraph("Couldn't find the following companies:", self.comp_style))
                    for broken in broken_company_list: 
                        elements.append(Paragraph(f"Company with ID {broken}", self.italic_style))
                        elements.append(Spacer(1, 5))
                    elements.append(Spacer(1, 15))
                    elements.append(self.horizontal_line)
                    elements.append(Spacer(1, 15))  
                           
                if broken_id_list: 
                    elements.append(Paragraph("Couldn't find the following indicators:", self.comp_style))
                    for id in set(broken_id_list):
                        elements.append(Paragraph(f"metricMeta with ID: {id}", self.italic_style))
                        elements.append(Spacer(1, 5))

        
        doc.build(elements, onFirstPage=self.onFirstPage, onLaterPages=self.onLaterPages)
        buffer.seek(0)
        return buffer
    
class FRAMEWORK_SFDR(PDF_STYLE):
    def __init__(self, exchange_id):
        super().__init__()
        self.exchange_id = exchange_id
        self.exchange = db.exchange.find_one({'_id': ObjectId(self.exchange_id)})
        
        if self.exchange:
            self.fund_id = self.exchange['fund_link']
            self.fund = db.funds.find_one({'_id': ObjectId(self.fund_id)})
            logging.info("It found the request %s and fund %s on mongodb", str(self.exchange_id), str(self.fund_id))
            if self.fund:
                self.topright = Paragraph(f"<b>Your fund:</b> {self.fund['title']}<br/><b>ID:</b> {self.exchange['fund_link']}", self.normal_style)
                self.bottomright = Paragraph(f"<b>Reporting period: </b>{' - '.join(self.exchange['reporting_period'])}<br/>", self.normal_style)
                self.middleright = Paragraph(f"<b>Deadline:</b> {self.exchange['deadline']}", self.normal_style)
                self.bottomleft = Paragraph(f"SFDR 9<br/>FRAMEWORK", self.title_style) 

    def framework_sfdr(self):      
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=90)
        elements: list[Flowable] = [Spacer(1, 75)]
        
        if self.exchange is None:
            elements.append(Paragraph(f"The exchange {self.exchange_id} does not seem to exist on our database.", self.italic_style))
            
        elif self.fund is None:
            elements.append(Paragraph(f"The fund {self.fund_id} does not seem to exist on our database.", self.italic_style))
        else:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph('DESCRIPTION', self.sub_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"This comprehensive report provides a detailed overview of {self.fund['title']}'s compliance with the EU's Sustainable Finance Disclosure Regulation (SFDR) Article 9 requirements. It offers an in-depth analysis of the environmental, social and governance (ESG) performance of portfolio companies, including metrics on carbon emissions, energy efficiency, water usage, and more. The data presented in this report is a testament to a commitment to sustainable investing, transparency, and the ongoing efforts to align {self.fund['title']}'s investments with the EU's sustainability objectives.", self.custom_style))
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15)) 
            elements.append(Paragraph('ENTITIES', self.sub_style))
            
            company_list = []
            broken_company_list = []
            metric_list = []  
            broken_id_list = []                  
            for comp in self.exchange['companies']:
                entitity_id = comp['company_link']
                company_ = db.companies.find_one({'_id': ObjectId(entitity_id)})
                if company_:
                    company_list.append(company_['title'])
                else: 
                    broken_company_list.append(entitity_id)
                
                for req_met in range(len(comp['requested_metrics'])):
                    metric_id = comp['requested_metrics'][req_met]
                    m = db.metricMeta.find_one({'_id': ObjectId(metric_id)}, {'embeddings':0})
                    if m and m not in metric_list:
                        metric_list.append(m)
                    elif m is None:
                        print(metric_id, "is broken")
                        broken_id_list.append(metric_id)
            
            elements.append(Paragraph(", ".join(company_list), self.custom_style))
                                    
            elements.append(Spacer(1, 15)) 
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15))            
            elements.append(Paragraph('INDICATORS', self.sub_style)) 
            elements.append(Spacer(1, 5))
                            
            for metric in metric_list:
                elements.append(Paragraph(metric['title'], self.sub_style))
                if metric.get('Mandatory', {}):
                    if metric['Mandatory'] == False:
                        elements.append(Paragraph("This is a voluntary metric", self.custom_style))
                
                elements.append(Paragraph(metric['description'], self.custom_style))
                if metric.get('Usage guidance', {}):
                    elements.append(Paragraph(metric['Usage guidance'], self.custom_style))
                    elements.append(Paragraph(metric['Calculation'], self.custom_style))
                elements.append(Spacer(1, 5))
                
                # metric url
                metric_url = BASE + f"/library/{str(metric['_id'])}"
                elements.append(Paragraph(f"<u><link href={metric_url}>Read more on the metric</link></u>", self.custom_style))
                # companies
                
                elements.append(Spacer(1, 5))
                
                # aggregate_pdf = AGGREGATE_PDF(metric['_id'], self.exchange_id)
                # sum = aggregate_pdf.aggregation_type()
                
                # # elements.append(Spacer(1, 15))                
                # elements.append(Paragraph(f"Value {sum} Units", self.title_style_c))
                
                elements.append(Spacer(1, 5))
            
                valuelist = []
                float_sum = 0
                # loop over the companies in the request
                for comp in self.exchange['companies']:
                    entitity_id = comp['company_link']
                    company = db.companies.find_one({'_id': ObjectId(entitity_id)})
                    
                    if company:
                        elements.append(Paragraph(company['title'], self.comp_style))
                        
                        # if the company in the request has the metric, take the value
                        if str(metric['_id']) in comp['requested_metrics']:
                            metricValue = db.metricValues.find_one({'company_link': entitity_id, 'metric_meta_link': str(metric['_id'])})
                            
                            if metricValue:
                                companyValue = '<b>Value: </b>' + str(metricValue['value']) if metricValue else "No value"
                                if 'unit' in metricValue.keys():
                                    unit = str(metricValue['unit']) 
                                else: 
                                    unit = "(no unit specified)"
                                    
                                period = self.entity_reporting_period(metricValue)
                                elements.append(Paragraph(f"{companyValue} {unit} <br/>{period}", self.custom_style))

                                if metricValue: 
                                    valuelist.append(str(metricValue['value']))
                                    if isinstance(float(metricValue['value']), float):
                                        float_sum += float(metricValue['value'])
                            else: 
                                elements.append(Paragraph(f"The metricValue for company with ID {entitity_id} does not seem to exist on our database.", self.italic_style))
                    else: 
                        elements.append(Paragraph(f"The company with ID {entitity_id} does not seem to exist on our database.", self.comp_style))
                        continue 
                
                elements.append(Spacer(1, 5))
                elements.append(Paragraph('CALCULATION', self.sub_style))
                elements.append(Spacer(1, 15))
                calculation = " + ".join(valuelist) + f" = {float_sum}" # "Aggregation method: UNWEIGHTED SUM <br/>" 
                elements.append(self.calculation_table(calculation))
                
                elements.append(Spacer(1, 15))  
                elements.append(self.horizontal_line)
                elements.append(Spacer(1, 15))

                
            elements.append(Spacer(1, 15))    
            elements.append(self.horizontal_line)
            elements.append(Spacer(1, 15))
            
            if broken_company_list or broken_id_list:
                elements.append(Spacer(1, 15))
                elements.append(Paragraph('ERRORS', self.sub_style)) 
                if broken_company_list:
                    elements.append(Paragraph("Couldn't find the following companies:", self.comp_style))
                    for broken in broken_company_list: 
                        elements.append(Paragraph(f"Company with ID {broken}", self.italic_style))
                        elements.append(Spacer(1, 5))
                    elements.append(Spacer(1, 15))
                    elements.append(self.horizontal_line)
                    elements.append(Spacer(1, 15))  
                           
                if broken_id_list: 
                    elements.append(Paragraph("Couldn't find the following indicators:", self.comp_style))
                    for id in set(broken_id_list):
                        elements.append(Paragraph(f"metricMeta with ID: {id}", self.italic_style))
                        elements.append(Spacer(1, 5))

        
        doc.build(elements, onFirstPage=self.onFirstPage, onLaterPages=self.onLaterPages)
        buffer.seek(0)
        return buffer
    