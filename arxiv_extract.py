from bs4 import  BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
import re

class get_paper_info:    
    def __init__(self,source_code):        
        self.source_code = source_code
        self.parent_tag = None
        self.parent_class = None
        
        self.tag_and_class = {"title":["h1","title mathjax"],"authors":["div","authors"],"doi":["td","tablecell arxivdoi"],"conference":["td","tablecell comments mathjax"]}
        self.title = None
        self.doi = None
        self.conference_journal = None
        self.authors = None
        self.published_year = None

    
    def implement(self):
        for attribute in self.tag_and_class.keys():
            
            tag = self.tag_and_class[attribute][0]
            tag_class = self.tag_and_class[attribute][1]
            text = self.source_code.find(tag,{'class':tag_class})
            
            if attribute == "title":
                self.get_title(text)
                
            elif attribute == "authors":
                self.get_authors(text)
            
            elif attribute == "doi":
                self.get_doi(text)
                
            elif attribute == "conference":
                self.get_conference_journal(text)
        
        print(self.title, self.authors, self.doi, self.conference_journal, self.published_year)
        
        
        
    def get_title(self,text):
        text = text.getText()
        self.title = text.replace("Title:","")
        
    def get_authors(self,text):
        text = text.getText()
        self.authors = text.replace("Authors:","")
    
    def get_doi(self,text):
        self.doi = text.a.get("href")
    
    def get_conference_journal(self,text):
        if text is None:
            self.no_peer_review()
        else:    
            try:
                text = text.getText()
                conference_year = re.search("[a-zA-Z]+ [0-9]{4}",text)
                conference_year = conference_year.group()
                self.conference_journal, self.published_year = conference_year.split(" ")
          
            except AttributeError:
                self.no_peer_review()           
    
    def no_peer_review(self):
        tag = "div"
        tag_class = "dateline"
        tag_text = self.source_code.find(tag,{'class':tag_class})
        tag_text = tag_text.getText()
        self.conference_journal = "Arxiv"
        for year in re.finditer("[0-9]{4}",tag_text):
            self.published_year = year.group()
    
    def get_extracted_info(self):
        return self.title, self.authors, self.doi, self.conference_journal, self.published_year
        

class access_web_extract:
    def __init__(self,web_url,parser):
        """
        Args:
            web_url (str): URL you want to access
            parser (str): html.parser
        """        
        self.web_url = web_url
        self.parser = parser
        
        try:
            html = urlopen(self.web_url)
            source_code = BeautifulSoup(html,self.parser)
        except URLError as e:
            print(f"{e}:This URL can't be accessed")
        
        self.get_paper_info = get_paper_info(source_code)
        
    def implement(self):
        self.get_paper_info.implement()
        extracted_info = self.get_paper_info.get_extracted_info()
        return extracted_info

