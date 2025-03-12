from unstructured.partition.pdf import partition_pdf
from unstructured.partition.ppt import partition_ppt
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.xml import partition_xml
from unstructured.partition.doc import partition_doc, partition_docx
from unstructured.documents.elements import Element

from typing import List
import os

class DocumentParser:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_dir, extension = os.path.splitext(file_path)
        self.extension = extension[1:]
        self.languages = ["eng", "kor"]
        self.strategy = "hi_res"
        self.elements = []
        
    def _partition_documents(self) -> List[Element]:
        
        if self.extension == 'pdf':
            self.elements = self._partition_pdf()
        # elif self.extension == 'doc':
        #     elements = self._partition_doc()
        # elif self.extension == 'docx':
        #     elements = self.partition_docx()
        # elif self.extension == 'ppt':
        #     elements = self.partition_ppt()
        # elif self.extension == 'pptx':
        #     elements = self.partition_pptx()
        else:
            raise ValueError(f"Unsupported file extension: {self.extension}")

        
        return self.elements
    
    def _partition_pdf(self) -> List[Element]:
        images_dir = os.path.join(self.file_dir, 'src')
        
        if not os.path.exists(images_dir): os.makedirs(images_dir)
        
        elements = partition_pdf(
            filename=self.file_path,                  # mandatory
            strategy=self.strategy,                                     # mandatory to use ``hi_res`` strategy
            extract_images_in_pdf=True,                            # mandatory to set as ``True``
            extract_image_block_types=["Image", "Table"],          # optional
            extract_image_block_to_payload=False,                  # optional
            extract_image_block_output_dir=images_dir,  # optional - only works when ``extract_image_block_to_payload=False``
            content_type="application/pdf", languages=self.languages
            )
        
        return elements
    
    def _partition_doc(self) -> List[Element]:
        elements = partition_doc(
            filename=self.file_path,
            languages=self.languages,
            strategy=self.strategy
        )
        return elements

    def _partition_docx(self) -> List[Element]:
        elements = partition_docx(
            filename=self.file_path,
            languages=self.languages,
            strategy=self.strategy
        )
        return elements
    
    def _partition_ppt(self) -> List[Element]:
        elements = partition_ppt(
            filename=self.file_path,
            strategy=self.strategy
        )
        return elements
    
    def _partition_pptx(self) -> List[Element]:
        elements = partition_pptx(
            filename=self.file_path,
            strategy=self.strategy
        )
        return elements
    
    def _partition_xml(self) -> List[Element]:
        elements = partition_xml(
            filename=self.file_path,
            xml_keep_tags=True
        )
        return elements
    
    def _combine_elements(self, elements: List[Element]) -> List[str]:
        result = []
        text = ''
        for i in range(len(elements)):
            el = elements[i].to_dict()  
            if el['type'] == 'Title':
                result.append(text)
                text = ''
                text+=el['text']
            elif i == len(elements)-1 :
                text+=el['text']
                result.append(text)
            else:
                text+=el['text']
        return result
    
    def parse_doc_to_seg(self):
        elements = self._partition_documents()
        
        return self._combine_elements(elements) 
    
        
if __name__=="__main__":
    pdf_file_path = '/root/parsing/data/deepmind 보고서.pdf'
    docx = '' 
    dp = DocumentParser(pdf_file_path)
    elements = dp.partition_documents()
    result = dp.combine_elements(elements)    
    with open('output.txt', "w", encoding="utf-8") as f:
        for line in result:
            f.write(line + "\n\n")  # 각 요소를 새 줄에 저장
    print(f"✅ 파일이 저장되었습니다: {'output.txt'}")

    
        
        