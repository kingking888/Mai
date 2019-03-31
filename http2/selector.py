import re

from lxml import etree

tree = etree.HTML('')
tree.xpath()

class Selector:
    def __init__(self, html):
        tree = etree.HTML("")
        tree.xpath()
    def extract(xpath):
        treeElems = self.tree.xpath(xpath)
        seleElems = []
        for elem in treeElems:
            if isinstance(elem, str):
                seleElems.append(elem)
            seleElems.append(Selector(etree.tounicode(seleElems, method="html")))
        return elem            

    def extract_first(xpath):
        elems = self.extract(xpath)
        if elems:
            return elems[0]
            