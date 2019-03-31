import re

from lxml import etree

class Selector:
    def __init__(self, html):
        self.tree = etree.HTML(html)

    def extract(self, xpath):
        treeElems = self.tree.xpath(xpath)
        seleElems = []
        for elem in treeElems:
            if isinstance(elem, str):
                seleElems.append(elem)
            else:
                seleElems.append(Selector(etree.tounicode(elem, method="html")))
        return seleElems           

    def extract_first(self, xpath):
        elems = self.extract(xpath)
        if elems:
            return elems[0]
            